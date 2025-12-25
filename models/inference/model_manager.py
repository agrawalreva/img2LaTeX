import os
import json
import torch
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from unsloth import FastVisionModel
    UNSLOTH_AVAILABLE = True
except (ImportError, NotImplementedError):
    UNSLOTH_AVAILABLE = False
    FastVisionModel = None

from .unsloth_qwen import get_model_and_tokenizer

class ModelManager:
    def __init__(self):
        self.base_model = None
        self.base_tokenizer = None
        self.current_adapter = None
        self.adapter_path = None
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "./models/training/outputs")
        
    def load_base_model(self):
        if self.base_model is None:
            self.base_model, self.base_tokenizer = get_model_and_tokenizer()
    
    def get_available_adapters(self) -> list[Dict[str, Any]]:
        adapters = []
        
        if not os.path.exists(self.artifacts_dir):
            return adapters
            
        for job_dir in os.listdir(self.artifacts_dir):
            job_path = os.path.join(self.artifacts_dir, job_dir)
            if os.path.isdir(job_path):
                config_file = os.path.join(job_path, "training_config.json")
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        model_files = [f for f in os.listdir(job_path) if f.endswith('.safetensors')]
                        if model_files:
                            adapters.append({
                                "job_id": job_dir,
                                "path": job_path,
                                "config": config,
                                "created_at": os.path.getctime(job_path)
                            })
                    except Exception:
                        pass
        
        adapters.sort(key=lambda x: x["created_at"], reverse=True)
        return adapters
    
    def load_adapter(self, adapter_path: str) -> bool:
        try:
            if not os.path.exists(adapter_path):
                return False
            
            self.load_base_model()
            
            adapter_model, adapter_tokenizer = FastVisionModel.from_pretrained(
                adapter_path,
                load_in_4bit=True,
                use_gradient_checkpointing="unsloth"
            )
            
            FastVisionModel.for_inference(adapter_model)
            
            self.base_model = adapter_model
            self.base_tokenizer = adapter_tokenizer
            self.current_adapter = adapter_path
            self.adapter_path = adapter_path
            
            return True
            
        except Exception:
            return False
    
    def switch_to_base(self) -> bool:
        try:
            self.base_model, self.base_tokenizer = get_model_and_tokenizer()
            self.current_adapter = None
            self.adapter_path = None
            return True
        except Exception:
            return False
    
    def get_current_model_info(self) -> Dict[str, Any]:
        if self.current_adapter:
            return {
                "type": "adapter",
                "path": self.adapter_path,
                "name": os.path.basename(self.adapter_path)
            }
        else:
            return {
                "type": "base",
                "path": "unsloth/Qwen2-VL-7B-Instruct",
                "name": "Base Qwen2-VL"
            }
    
    def get_model_and_tokenizer(self):
        self.load_base_model()
        return self.base_model, self.base_tokenizer


model_manager = ModelManager()
