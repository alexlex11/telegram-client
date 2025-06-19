import logging
from dataclasses import dataclass
from typing import List, Union

from fastapi import HTTPException
from src.accounts.schemas import STelethonAccount
from src.config.settings import settings

from ..core.api_clients.telegram import TelegramAPIClient

logger = logging.getLogger(__name__)


@dataclass
class TelegramAccsService:
    client: TelegramAPIClient

    async def get_teleton_accounts(self) -> Union[List[STelethonAccount], None]:
        try:
            response = await self.client.get(
                endpoint=settings.all_teleton_accounts_endpoint
            )
            return response
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {e}")
            raise HTTPException(
                status_code=503, detail="Bot service unavailable"
            ) from e
