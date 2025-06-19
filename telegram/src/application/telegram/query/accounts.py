import logging
from dataclasses import dataclass
from typing import List

from src.application.common.query import Query, QueryHandler
from src.domain.telegram.services.operations import TelegramOperations
from telethon.tl.types import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetTelegramAccountByPhone(Query[User]):
    phone: str


class GetTelegramAccountByPhoneHandler(QueryHandler[GetTelegramAccountByPhone, User]):
    def __init__(self, telegram_operations: TelegramOperations):
        self._telegram_operations = telegram_operations

    async def __call__(self, query: GetTelegramAccountByPhone) -> User:
        account = await self._telegram_operations.get_account_by_phone(query.phone)

        if account is None:
            raise Exception("Account does not exists.")

        logger.info("Get account by phone", extra={"account_phone": query.phone})
        return account


@dataclass(frozen=True)
class GetTelegramAccounts(Query[User]):
    pass


class GetTelegramAccountsHandler(QueryHandler[GetTelegramAccounts, List[User]]):
    def __init__(self, telegram_operations: TelegramOperations):
        self._telegram_operations = telegram_operations

    async def __call__(self, query: GetTelegramAccounts) -> List[User]:
        accounts = await self._telegram_operations.get_accounts()

        if accounts is None:
            raise Exception("Cant get accounts")

        logger.info("Get accounts")
        return accounts
