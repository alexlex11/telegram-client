from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.services.telegram import TelegramAccsService
from src.users.models import User

from .dependencies import get_telegram_accs_service
from .schemas import STelethonAccount, STelethonAccountsList

teleton_account_router = APIRouter(
    prefix="/telethon_accounts", tags=["Telethon accounts"]
)


@teleton_account_router.get(
    path="/",
    summary="Endpoint for getting all user's accounts. JSON responce",
    response_model=STelethonAccountsList,
)
async def get_telethon_accounts(
    user: User = Depends(get_current_user),
    bot_service: TelegramAccsService = Depends(get_telegram_accs_service),
) -> STelethonAccountsList:

    telethon_accs = await bot_service.get_teleton_accounts()

    return STelethonAccountsList(teleton_accounts=telethon_accs)


@teleton_account_router.get(
    path="/list",
    summary="Endpoint for getting all user's accounts. List responce",
    response_model=list[STelethonAccount],
)
async def get_telethon_accounts_list(
    user: User = Depends(get_current_user),
    bot_service: TelegramAccsService = Depends(get_telegram_accs_service),
) -> list[STelethonAccount]:

    return await bot_service.get_teleton_accounts()
