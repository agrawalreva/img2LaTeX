import os
import sys
import time
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException
from PIL import Image
import torch

# Add project root to path for model imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from models.inference.model_manager import model_manager
from app.core.config import settings


async def run_inference_service(image_path: str) -> Tuple[str, int, int]:
    """Run model inference on image to generate LaTeX using model_manager."""
    start_time = time.time()
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Check if model is available, with timeout handling
        import asyncio
        try:
            model, tokenizer = await asyncio.wait_for(
                asyncio.to_thread(model_manager.get_model_and_tokenizer),
                timeout=300.0  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Model loading timed out. The model may be too large for this system."
            )
        
        image = Image.open(image_path).convert('RGB')
        
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
        
        # Detect if we're using processor (has tokenizer attribute) or direct tokenizer
        is_processor = hasattr(tokenizer, 'tokenizer')
        
        if is_processor:
            # Qwen2VLProcessor interface - use apply_chat_template for proper image token handling
            messages_qwen = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": instruction}
                    ]
                }
            ]
            text = tokenizer.apply_chat_template(messages_qwen, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(
                text=[text],
                images=[image],
                return_tensors="pt",
                padding=True
            ).to(device)
            eos_token_id = getattr(model.config, 'eos_token_id', None)
            input_ids_len = inputs['input_ids'].shape[1]
        else:
            # Unsloth tokenizer interface
            input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
            inputs = tokenizer(
                image, input_text,
                add_special_tokens=False,
                return_tensors="pt",
            ).to(device)
            eos_token_id = getattr(tokenizer, 'eos_token_id', None) or getattr(model.config, 'eos_token_id', None)
            input_ids_len = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            if is_processor:
                # Qwen2VL requires all inputs from processor
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=settings.max_new_tokens,
                    temperature=settings.temperature,
                    do_sample=True,
                    eos_token_id=eos_token_id
                )
            else:
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=settings.max_new_tokens,
                    use_cache=True,
                    temperature=settings.temperature,
                    min_p=settings.min_p,
                    do_sample=True,
                    pad_token_id=eos_token_id
                )
        
        # Decode output - handle both tokenizer and processor
        if hasattr(tokenizer, 'decode'):
            generated_text = tokenizer.decode(outputs[0][input_ids_len:], skip_special_tokens=True)
        else:
            # Processor has tokenizer attribute
            generated_text = tokenizer.tokenizer.decode(outputs[0][input_ids_len:], skip_special_tokens=True)
        
        tokens_used = len(outputs[0]) - len(inputs['input_ids'][0])
        time_ms = int((time.time() - start_time) * 1000)
        
        return generated_text.strip(), tokens_used, time_ms
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )
