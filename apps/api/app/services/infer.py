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
        
        model, tokenizer = model_manager.get_model_and_tokenizer()
        
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
        
        input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        
        inputs = tokenizer(
            image, input_text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=settings.max_new_tokens,
                use_cache=True,
                temperature=settings.temperature,
                min_p=settings.min_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        tokens_used = len(outputs[0]) - len(inputs['input_ids'][0])
        time_ms = int((time.time() - start_time) * 1000)
        
        return generated_text.strip(), tokens_used, time_ms
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )
