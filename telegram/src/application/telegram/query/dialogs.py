import logging
from dataclasses import dataclass
from typing import List, Union

from src.application.common.query import Query, QueryHandler
from src.domain.telegram.services.operations import TelegramOperations
from telethon.tl.types import Dialog

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetTelegramDialogsByPhone(Query):
    phone: str


class GetTelegramDialogsByPhoneHandler(
    QueryHandler[GetTelegramDialogsByPhone, List[Dialog]]
):
    def __init__(self, telegram_operations: TelegramOperations):
        self._telegram_operations = telegram_operations

    async def __call__(self, query: GetTelegramDialogsByPhone) -> List[Dialog]:
        dialogs = await self._telegram_operations.get_dialogs_by_phone(query.phone)

        if dialogs is None:
            raise Exception("Account does not exists.")

        logger.info("Get accounts by phone", extra={"account_phone": query.phone})
        return dialogs


@dataclass(frozen=True)
class GetTelegramDialogByEntity(Query):
    phone: str
    entity: Union[str, int]


class GetTelegramDialogByEntityHandler(QueryHandler[GetTelegramDialogByEntity, Dialog]):
    def __init__(self, telegram_operations: TelegramOperations):
        self._telegram_operations = telegram_operations

    async def __call__(self, query: GetTelegramDialogByEntity) -> Dialog:
        dialog = await self._telegram_operations.get_account_dialog_by_entity(
            query.entity, query.phone
        )

        if dialog is None:
            raise Exception("Account does not exists.")

        logger.info(
            "Get accounts by phone",
            extra={"account_phone": query.phone, "query_entity": query.entity},
        )
        return dialog
