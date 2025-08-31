import os
import json
import time
import uuid
from typing import Dict, Any
from celery import current_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unsloth import FastVisionModel
from datasets import Dataset
from trl import SFTTrainer, SFTConfig
from transformers import TextStreamer

# Import models and repositories
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../apps/api'))

from app.db.models import Pair, TrainJob
from app.db.repository import TrainJobRepository
from app.core.config import settings

def get_db_session():
    """Get database session for worker."""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def update_job_status(job_id: str, status: str, logs: str = None, artifacts_path: str = None):
    """Update training job status in database."""
    db = get_db_session()
    try:
        TrainJobRepository.update_status(db, job_id, status, logs, artifacts_path)
    finally:
        db.close()

def log_message(message: str):
    """Log message and update task status."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")
    current_task.update_state(
        state="PROGRESS",
        meta={"current": 0, "total": 100, "status": message}
    )

@celery_app.task(bind=True)
def train_lora(self, job_id: str, config: Dict[str, Any]):
    """Train LoRA adapter on dataset pairs."""
    
    try:
        log_message(f"Starting LoRA training job {job_id}")
        update_job_status(job_id, "RUNNING", "Starting training...")
        
        # Get database session
        db = get_db_session()
        
        # Fetch dataset pairs
        log_message("Fetching dataset pairs...")
        pairs = db.query(Pair).all()
        
        if len(pairs) < 5:
            raise ValueError("Need at least 5 pairs for training")
        
        log_message(f"Found {len(pairs)} pairs for training")
        
        # Prepare dataset for TRL
        log_message("Preparing dataset...")
        dataset_data = []
        
        for pair in pairs:
            # Create conversation format for vision model
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Write the LaTeX representation for this image."},
                        {"type": "image", "image": pair.image_path}
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": pair.latex_text}
                    ]
                }
            ]
            dataset_data.append({"messages": conversation})
        
        # Create dataset
        dataset = Dataset.from_list(dataset_data)
        log_message(f"Dataset prepared with {len(dataset)} samples")
        
        # Load base model
        log_message("Loading base model...")
        model, tokenizer = FastVisionModel.from_pretrained(
            "unsloth/Qwen2-VL-7B-Instruct",
            load_in_4bit=True,
            use_gradient_checkpointing="unsloth"
        )
        
        # Apply LoRA
        log_message("Applying LoRA configuration...")
        model = FastVisionModel.get_peft_model(
            model,
            finetune_vision_layers=True,
            finetune_language_layers=True,
            finetune_attention_modules=True,
            finetune_mlp_modules=True,
            r=config.get("r", 16),
            lora_alpha=config.get("lora_alpha", 16),
            lora_dropout=config.get("lora_dropout", 0),
            bias="none",
            random_state=config.get("random_state", 3407),
            use_rslora=config.get("use_rslora", False),
            loftq_config=None
        )
        
        # Create output directory
        output_dir = os.path.join(settings.artifacts_dir, job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Training configuration
        training_config = SFTConfig(
            per_device_train_batch_size=config.get("batch_size", 2),
            gradient_accumulation_steps=config.get("gradient_accumulation_steps", 4),
            warmup_steps=config.get("warmup_steps", 5),
            max_steps=config.get("max_steps", 30),
            learning_rate=config.get("learning_rate", 2e-4),
            fp16=True,
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=config.get("random_state", 3407),
            output_dir=output_dir,
            report_to="none",
            remove_unused_columns=False,
            dataset_text_field="",
            dataset_kwargs={"skip_prepare_dataset": True},
            dataset_num_proc=4,
            max_seq_length=2048,
        )
        
        # Initialize trainer
        log_message("Initializing trainer...")
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            data_collator=FastVisionModel.get_data_collator(model, tokenizer),
            train_dataset=dataset,
            args=training_config,
        )
        
        # Start training
        log_message("Starting training...")
        trainer.train()
        
        # Save model
        log_message("Saving trained model...")
        trainer.save_model()
        
        # Switch to inference mode
        FastVisionModel.for_inference(model)
        
        # Test inference
        log_message("Testing inference...")
        if len(pairs) > 0:
            test_pair = pairs[0]
            test_image = test_pair.image_path
            
            # Prepare test input
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Write the LaTeX representation for this image."},
                        {"type": "image", "image": test_image}
                    ]
                }
            ]
            
            input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
            inputs = tokenizer(
                test_image, input_text,
                add_special_tokens=False,
                return_tensors="pt",
            ).to("cuda")
            
            # Generate test output
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=256,
                    use_cache=True,
                    temperature=0.7,
                    min_p=0.1
                )
            
            test_output = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            log_message(f"Test inference successful: {test_output[:50]}...")
        
        # Update final status
        final_logs = f"Training completed successfully!\nModel saved to: {output_dir}\nTotal pairs: {len(pairs)}"
        update_job_status(job_id, "DONE", final_logs, output_dir)
        
        log_message("Training job completed successfully!")
        return {"status": "success", "output_dir": output_dir}
        
    except Exception as e:
        error_msg = f"Training failed: {str(e)}"
        log_message(error_msg)
        update_job_status(job_id, "FAILED", error_msg)
        raise e
    finally:
        if 'db' in locals():
            db.close()
