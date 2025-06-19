from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.orm import Session
from src.core.api_clients.base import HTTPAPIClient
from src.repositories import BaseRepository

from ..core.api_clients.telegram import TelegramAPIClient
from ..services.telegram import TelegramAccsService
from .exceptions import AccountDoesNotExist


class AccountRepository(BaseRepository):
    model = None


def get_account_or_404(session: Session, **data):
    account_repository = AccountRepository()
    account = account_repository.get(session, **data)
    if not account:
        raise AccountDoesNotExist
    return account


async def get_telegram_client() -> TelegramAPIClient:
    return TelegramAPIClient()


async def get_telegram_accs_service(
    client: HTTPAPIClient = Depends(get_telegram_client),
) -> AsyncGenerator[TelegramAccsService, None]:
    async with client:
        yield TelegramAccsService(client=client)
