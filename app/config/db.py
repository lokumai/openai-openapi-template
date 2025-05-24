from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_TYPE: Literal["mongodb", "embedded"] = "embedded"
    DATABASE_NAME: str = "openai_chatbot_api"

    MONGO_USER: str = "root"
    MONGO_PASSWORD: str = "rootPass"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_URI: str = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DATABASE_NAME}"

    def get_mongo_uri(self) -> str:
        return self.MONGO_URI


db_config = DBConfig()
