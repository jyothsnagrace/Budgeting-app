# CHECKPOINT_1_PROJECT_SETUP
"""
Configuration Management
========================
Centralized configuration for the expense tracking backend.
Uses environment variables with fallback defaults.
"""

import os
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = ConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = "LLM Expense Tracker"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # ============================================
    # API Settings
    # ============================================
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # ============================================
    # Supabase Configuration
    # ============================================
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")
    
    # ============================================
    # LLM Configuration
    # ============================================
    # Choose: "ollama", "groq", "openai"
    LLM_PROVIDER: str = Field(default="ollama", env="LLM_PROVIDER")
    
    # Ollama settings (local)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL_EXTRACTION: str = Field(default="llama3.2", env="OLLAMA_MODEL_EXTRACTION")
    OLLAMA_MODEL_VALIDATION: str = Field(default="llama3.2", env="OLLAMA_MODEL_VALIDATION")
    
    # Groq settings (cloud)
    GROQ_API_KEY: Optional[str] = Field(None, env="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama-3.1-8b-instant", env="GROQ_MODEL")
    
    # OpenAI settings (cloud)
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
    # LLM behavior
    LLM_TEMPERATURE: float = 0.1  # Low temperature for structured outputs
    LLM_MAX_TOKENS: int = 500
    LLM_TIMEOUT: int = 30  # seconds
    
    # ============================================
    # Voice Input Configuration (Whisper)
    # ============================================
    WHISPER_MODEL: str = Field(default="base", env="WHISPER_MODEL")  # tiny, base, small, medium, large
    WHISPER_LANGUAGE: str = "en"
    AUDIO_SAMPLE_RATE: int = 16000
    MAX_AUDIO_LENGTH: int = 60  # seconds
    
    # ============================================
    # Cost of Living API
    # ============================================
    # Numbeo API (requires manual scraping or paid plan)
    # Alternative: Use Teleport API (free)
    COST_API_PROVIDER: str = Field(default="teleport", env="COST_API_PROVIDER")  # "numbeo" or "teleport"
    NUMBEO_API_KEY: Optional[str] = Field(None, env="NUMBEO_API_KEY")
    TELEPORT_API_URL: str = "https://api.teleport.org/api/urban_areas/"
    
    # Cache settings
    COST_DATA_CACHE_HOURS: int = 24 * 30  # Cache for 30 days
    
    # ============================================
    # Authentication Settings
    # ============================================
    # Username-only auth (no password)
    SESSION_SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SESSION_SECRET_KEY")
    SESSION_ALGORITHM: str = "HS256"
    SESSION_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ============================================
    # Logging
    # ============================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/app.log"
    
    # ============================================
    # Rate Limiting
    # ============================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ============================================
    # Database Connection Pool
    # ============================================
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use this function to access settings throughout the app.
    """
    return Settings()


# Global settings instance
settings = get_settings()


# ============================================
# Validation Functions
# ============================================

def validate_config():
    """
    Validate that all required configuration is present.
    Raises ValueError if critical config is missing.
    """
    errors = []
    
    # Check Supabase config
    if not settings.SUPABASE_URL:
        errors.append("SUPABASE_URL is required")
    if not settings.SUPABASE_KEY:
        errors.append("SUPABASE_KEY is required")
    
    # Check LLM provider config
    if settings.LLM_PROVIDER == "groq" and not settings.GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required when using Groq")
    if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when using OpenAI")
    
    # Check session secret
    if settings.SESSION_SECRET_KEY == "your-secret-key-change-in-production" and settings.ENVIRONMENT == "production":
        errors.append("SESSION_SECRET_KEY must be changed in production")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


def print_config_summary():
    """Print a summary of current configuration (for debugging)"""
    print("=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Whisper Model: {settings.WHISPER_MODEL}")
    print(f"Cost API: {settings.COST_API_PROVIDER}")
    print(f"Supabase URL: {settings.SUPABASE_URL[:30]}...")
    print("=" * 60)


if __name__ == "__main__":
    # Test configuration
    try:
        validate_config()
        print_config_summary()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
