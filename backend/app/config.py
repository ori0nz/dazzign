import os
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database settings
    DATABASE_URL: PostgresDsn
    
    # Server settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Create settings instance
settings = Settings() 