import logging

from fastapi import APIRouter, Depends
from src.api_client import ApiClient
from src.auth.dependencies import get_current_user
from src.users.models import User

from .dependencies import get_bots

logger = logging.getLogger((__name__))

ch_router = APIRouter(prefix="/chats", tags=["Chats"])


@ch_router.get(path="/", description="Get all chats from teleton acc peer.")
async def get_user_chats(
    bot_peer: int,
    user: User = Depends(get_current_user),
    bot_api: ApiClient = Depends(get_bots),
) -> dict:

    bot_api.endpoint = f"/ch/{bot_peer}"
    data = await bot_api.fetch_data()

    return data
