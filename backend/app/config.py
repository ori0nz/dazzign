import os
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database settings
    DATABASE_URL: Optional[PostgresDsn] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "dazzign"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    
    @property
    def get_database_url(self) -> PostgresDsn:
        """Fallback to construct DATABASE_URL if not provided"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
            
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.POSTGRES_DB,
        )
    
    # Server settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Create settings instance
settings = Settings() 