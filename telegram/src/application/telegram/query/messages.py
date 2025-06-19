import logging
from dataclasses import dataclass
from typing import List, Union

from src.application.common.query import Query, QueryHandler
from src.domain.telegram.services.operations import TelegramOperations
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetTelegramMessagesByEntityByPhone(Query):
    entity: Union[str, int]
    phone: str
    offset_id: int
    limit: int


class GetTelegramMessagesByEntityByPhoneHandler(
    QueryHandler[GetTelegramMessagesByEntityByPhone, List[Message]]
):
    def __init__(self, telegram_operations: TelegramOperations):
        self._telegram_operations = telegram_operations

    async def __call__(
        self, query: GetTelegramMessagesByEntityByPhone
    ) -> List[Message]:
        messages = await self._telegram_operations.get_messages_by_chat_entity_by_account_phone(  # noqa
            query.entity,
            query.phone,
            query.offset_id,
            query.limit,
        )

        if messages is None:
            raise Exception("Cant get messages.")

        logger.info(
            "Get messages.",
            extra={"account_phone": query.phone, "entity": query.entity},
        )
        return messages
