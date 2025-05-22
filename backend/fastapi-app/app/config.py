from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Comment Picker API"
    DEBUG: bool = False
    
    # Database settings (placeholders, will be configured later)
    # DATABASE_URL: str = "postgresql://user:password@host:port/database"

    # Bedrock settings
    BEDROCK_REGION: str = "us-east-1" # Default region, can be overridden by .env
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0" # Default model, can be overridden

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
