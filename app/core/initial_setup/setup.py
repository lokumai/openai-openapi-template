import json
import os
from typing import List, Optional
from loguru import logger
from app.model.chat_model import ChatCompletion
from app.repository.chat_repository import ChatRepository
from app.config.db import db_config


class InitialSetup:
    """Initial setup manager for the application when database type is embedded"""

    def __init__(self):
        self._chat_repository: Optional[ChatRepository] = None
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")

    @property
    def chat_repository(self) -> ChatRepository:
        """Lazy loading of ChatRepository"""
        if self._chat_repository is None:
            self._chat_repository = ChatRepository()
        return self._chat_repository

    def _load_initial_data(self) -> List[ChatCompletion]:
        """Load initial data from JSON files"""
        try:
            with open(os.path.join(self.data_dir, "initial_chat_completions.json"), "r") as f:
                data = json.load(f)
                return [ChatCompletion(**item) for item in data["chat_completions"]]
        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
            return []

    async def setup(self) -> None:
        """Setup initial data if database type is embedded"""
        try:
            if db_config.DATABASE_TYPE != "embedded":
                logger.info("Skipping initial setup as database type is not embedded")
                return

            # if MONGO_URI is not set, it means we are using embedded database
            # last check is for the case of using mongomock-motor for database_type=embedded
            # so last exit before the bridge :) turkish joke
            if db_config.MONGO_URI is None:
                # delete all chat completions in the embedded database
                logger.warning("Deleting all chat completions in the embedded database")
                await self.chat_repository.db.chat_completion.delete_many({})
                logger.warning("Deleting all chat completions in the embedded database done")

            chat_completions = self._load_initial_data()
            logger.info(f"Loaded {len(chat_completions)} initial chat completions")

            for completion in chat_completions:
                try:
                    found_id = await self.chat_repository.find_by_id(completion.completion_id)
                    if found_id:
                        logger.debug(f"Chat completion already exists: {found_id}")
                        continue

                    saved = await self.chat_repository.save(completion)
                    logger.info(f"Successfully saved chat completion: {saved.completion_id}")

                except Exception as e:
                    logger.error(f"Error saving chat completion {completion.completion_id}: {e}")
                    raise

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

        # query of the saved chat completions
        saved_chat_completions = await self.chat_repository.find()
        logger.debug("********** Begin of Saved chat completions**********")
        logger.trace(f"{saved_chat_completions}")

        logger.debug("********** End of Saved chat completions**********")

        logger.info("Initial setup completed successfully for embedded database")
