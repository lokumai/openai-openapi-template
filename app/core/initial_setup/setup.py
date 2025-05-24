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
        if db_config.DATABASE_TYPE != "embedded":
            logger.info("Skipping initial setup as database type is not embedded")
            return
        
        logger.info("Starting initial setup for embedded database")
        
        # Load and save initial chat completions
        chat_completions = self._load_initial_data()
        for completion in chat_completions:
            try:
                await self.chat_repository.save(completion)
                logger.info(f"Saved initial chat completion: {completion.completion_id}")
            except Exception as e:
                logger.error(f"Error saving chat completion {completion.completion_id}: {e}")
        
        # query of the saved chat completions
        saved_chat_completions = await self.chat_repository.find()
        logger.debug("********** Begin of Saved chat completions**********")
        logger.trace(f"{saved_chat_completions}")
        logger.debug(f"saved_chat_completions[0].messages[0]: {saved_chat_completions[0].messages[0]}")
        logger.debug("********** End of Saved chat completions**********")


        logger.info("Initial setup completed successfully for embedded database") 