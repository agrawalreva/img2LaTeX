import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://redis:6379/0"
    model_name: str = "unsloth/Qwen2-VL-7B-Instruct"
    use_4bit: bool = True
    max_new_tokens: int = 256
    temperature: float = 0.7
    min_p: float = 0.1
    artifacts_dir: str = "./models/training/outputs"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings() 