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
    """Manages switching between base model and fine-tuned adapters."""
    
    def __init__(self):
        self.base_model = None
        self.base_tokenizer = None
        self.current_adapter = None
        self.adapter_path = None
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "./models/training/outputs")
        
    def load_base_model(self):
        """Load the base Qwen2-VL model."""
        if self.base_model is None:
            print("Loading base Qwen2-VL model...")
            self.base_model, self.base_tokenizer = get_model_and_tokenizer()
            print("Base model loaded successfully!")
    
    def get_available_adapters(self) -> list[Dict[str, Any]]:
        """Get list of available fine-tuned adapters."""
        adapters = []
        
        if not os.path.exists(self.artifacts_dir):
            return adapters
            
        for job_dir in os.listdir(self.artifacts_dir):
            job_path = os.path.join(self.artifacts_dir, job_dir)
            if os.path.isdir(job_path):
                # Check if this is a completed training job
                config_file = os.path.join(job_path, "training_config.json")
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        # Check if model files exist
                        model_files = [f for f in os.listdir(job_path) if f.endswith('.safetensors')]
                        if model_files:
                            adapters.append({
                                "job_id": job_dir,
                                "path": job_path,
                                "config": config,
                                "created_at": os.path.getctime(job_path)
                            })
                    except Exception as e:
                        print(f"Error reading adapter {job_dir}: {e}")
        
        # Sort by creation time (newest first)
        adapters.sort(key=lambda x: x["created_at"], reverse=True)
        return adapters
    
    def load_adapter(self, adapter_path: str) -> bool:
        """Load a fine-tuned adapter."""
        try:
            if not os.path.exists(adapter_path):
                print(f"Adapter path does not exist: {adapter_path}")
                return False
            
            # Load base model if not already loaded
            self.load_base_model()
            
            # Load adapter weights
            print(f"Loading adapter from: {adapter_path}")
            
            # For Unsloth, we need to reload the model with adapter
            # This is a simplified approach - in production you'd use proper adapter loading
            adapter_model, adapter_tokenizer = FastVisionModel.from_pretrained(
                adapter_path,
                load_in_4bit=True,
                use_gradient_checkpointing="unsloth"
            )
            
            # Switch to inference mode
            FastVisionModel.for_inference(adapter_model)
            
            # Update current model
            self.base_model = adapter_model
            self.base_tokenizer = adapter_tokenizer
            self.current_adapter = adapter_path
            self.adapter_path = adapter_path
            
            print(f"Adapter loaded successfully from: {adapter_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load adapter: {e}")
            return False
    
    def switch_to_base(self) -> bool:
        """Switch back to base model."""
        try:
            print("Switching to base model...")
            
            # Reload base model
            self.base_model, self.base_tokenizer = get_model_and_tokenizer()
            self.current_adapter = None
            self.adapter_path = None
            
            print("Switched to base model successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to switch to base model: {e}")
            return False
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model."""
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
        """Get the current model and tokenizer."""
        self.load_base_model()
        return self.base_model, self.base_tokenizer


# Global model manager instance
model_manager = ModelManager()
