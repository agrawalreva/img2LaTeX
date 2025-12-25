import os


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "256"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.min_p = float(os.getenv("MIN_P", "0.1"))
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")


settings = Settings() 