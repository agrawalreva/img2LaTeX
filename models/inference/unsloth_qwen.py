import os
import time
import hashlib
import tempfile
from typing import Optional, Tuple
from PIL import Image
import torch

try:
    from unsloth import FastVisionModel
    UNSLOTH_AVAILABLE = True
except (ImportError, NotImplementedError):
    UNSLOTH_AVAILABLE = False
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    FastVisionModel = None

# Global model and tokenizer instances
_model = None
_tokenizer = None


def get_model_and_tokenizer():
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if UNSLOTH_AVAILABLE:
            if device == "cuda":
                _model, _tokenizer = FastVisionModel.from_pretrained(
                    "unsloth/Qwen2-VL-7B-Instruct",
                    load_in_4bit=True,
                    use_gradient_checkpointing="unsloth"
                )
            else:
                _model, _tokenizer = FastVisionModel.from_pretrained(
                    "unsloth/Qwen2-VL-7B-Instruct",
                    load_in_4bit=False,
                    use_gradient_checkpointing="unsloth",
                    torch_dtype=torch.float32
                )
            FastVisionModel.for_inference(_model)
        else:
            if device == "cuda":
                model_name = "Qwen/Qwen2-VL-7B-Instruct"
            else:
                model_name = "Qwen/Qwen2-VL-2B-Instruct"
            
            _processor = AutoProcessor.from_pretrained(model_name)
            _model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            _tokenizer = _processor
    
    return _model, _tokenizer


def get_image_hash(image_path: str) -> str:
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def run_inference(image_path: str, max_new_tokens: int = 256, temperature: float = 0.7, min_p: float = 0.1) -> Tuple[str, int, int]:
    start_time = time.time()
    
    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model and tokenizer
        model, tokenizer = get_model_and_tokenizer()
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        
        # Prepare chat template
        instruction = "Write the LaTeX representation for this image."
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image", "image": image}
                ]
            }
        ]
        
        # Apply chat template
        input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        
        # Tokenize inputs
        inputs = tokenizer(
            image, input_text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(device)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                use_cache=True,
                temperature=temperature,
                min_p=min_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Calculate tokens used
        tokens_used = len(outputs[0]) - len(inputs['input_ids'][0])
        
        # Calculate time
        time_ms = int((time.time() - start_time) * 1000)
        
        return generated_text.strip(), tokens_used, time_ms
        
    except Exception as e:
        raise RuntimeError(f"Inference failed: {str(e)}")


def run_inference_with_cache(image_path: str, cache_dir: Optional[str] = None, **kwargs) -> Tuple[str, int, int]:
    if cache_dir is None:
        cache_dir = tempfile.gettempdir()
    
    # Generate cache key
    image_hash = get_image_hash(image_path)
    cache_file = os.path.join(cache_dir, f"latex_cache_{image_hash}.txt")
    
    # Check cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached_data = f.read().strip().split('|')
                if len(cached_data) == 3:
                    latex, tokens, time_ms = cached_data
                    return latex, int(tokens), int(time_ms)
        except:
            pass
    
    # Run inference
    latex, tokens, time_ms = run_inference(image_path, **kwargs)
    
    # Cache result
    try:
        with open(cache_file, 'w') as f:
            f.write(f"{latex}|{tokens}|{time_ms}")
    except:
        pass
    
    return latex, tokens, time_ms
