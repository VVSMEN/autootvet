"""
Application configuration using pydantic-settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AutoOtvet"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/autootvet.db"
    
    # Security
    ENCRYPTION_KEY: str
    
    # Marketplace API Keys
    WB_API_KEY: Optional[str] = None
    OZON_CLIENT_ID: Optional[str] = None
    OZON_API_KEY: Optional[str] = None
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "gigachat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 200
    LLM_MODEL: Optional[str] = None
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GIGACHAT_API_KEY: Optional[str] = None
    GIGACHAT_CREDENTIALS: Optional[str] = None
    YANDEX_API_KEY: Optional[str] = None
    YANDEX_FOLDER_ID: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Review Processing
    REVIEW_CHECK_INTERVAL: int = 5  # minutes
    AUTO_SEND_RESPONSES: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/autootvet.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
