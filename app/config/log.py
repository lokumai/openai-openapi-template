from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class LogConfig(BaseSettings):
    """Logging configuration to be set for the server with LOG PREFIX in env variables"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.add(
            self.FILE_NAME,
            level=self.LEVEL,
            rotation=self.FILE_SIZE,
            retention=self.FILE_COUNT,
            # compression=self.FILE_AGE,
        )

    model_config = SettingsConfigDict(
        env_prefix="LOG_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    LEVEL: str = "DEBUG"
    FILE_NAME: str = "app.log"
    FILE_SIZE: int = 10485760  # 10MB
    FILE_COUNT: int = 3
    FILE_AGE: int = 3600  # 1 hour

    def get_log_level(self) -> int:
        return logger.level(self.LEVEL)


log_config = LogConfig()