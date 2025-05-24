from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class SecurityConfig(BaseSettings):
    """Security configuration to be set in env variables"""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SECRET_KEY: str = "your-secret-key-here"
    ENABLED: bool = True
    DEFAULT_USERNAME: str = "admin"

@lru_cache()
def get_security_config() -> SecurityConfig:
    return SecurityConfig() 
