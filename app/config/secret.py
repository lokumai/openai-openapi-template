from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretConfig(BaseSettings):
    """Secret configuration to be set in env variables"""

    model_config = SettingsConfigDict(
        env_prefix="SECRET_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    KEY: str = "mock-secret-key"


secret_config = SecretConfig()
