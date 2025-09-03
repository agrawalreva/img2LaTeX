import os
from typing import Optional


class Settings:
    def __init__(self):
        self.env = os.getenv("ENV", "dev")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.model_name = os.getenv("MODEL_NAME", "unsloth/Qwen2-VL-7B-Instruct")
        self.use_4bit = os.getenv("USE_4BIT", "true").lower() == "true"
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "256"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.min_p = float(os.getenv("MIN_P", "0.1"))
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "./models/training/outputs")
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")


settings = Settings() 