"""Application configuration using Pydantic Settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = ""

    # Supabase Configuration
    supabase_url: str = ""
    supabase_secret_key: str = ""

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def openai_api_key_value(self) -> str:
        """Get OpenAI API key."""
        return self.openai_api_key

    @property
    def supabase_url_value(self) -> str:
        """Get Supabase URL."""
        return self.supabase_url

    @property
    def supabase_secret_key_value(self) -> str:
        """Get Supabase secret key."""
        return self.supabase_secret_key

    def validate_required(self) -> bool:
        """Check if required settings are configured."""
        return bool(self.openai_api_key and self.supabase_url and self.supabase_secret_key)


# Global settings instance
settings = Settings()

