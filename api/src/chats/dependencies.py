from uuid import UUID

import requests
from sqlalchemy.orm import Session
from src.accounts.dependencies import get_account_or_404
from src.api_client import ApiClient

from .repositories import ChatRepository


def get_chat_or_create(session: Session, chat_id: int, to_account_id: int):
    chat = ChatRepository.get(session, soc_net_id=chat_id)
    if not chat:
        account = get_account_or_404(session, soc_net_id=to_account_id)
        chat = ChatRepository.add(
            session=session,
            soc_net_id=chat_id,
            account_id=account.id,
        )
    return chat


def get_chats_id(session: Session, account_id: UUID):
    chats = ChatRepository.get_all(session, account_id=account_id)
    result = []
    for chat in chats:
        result.append(chat.soc_net_id)
    return result


def _chats_id_to_dict(chats_id: list[int]):
    result = {}
    for chat_id in chats_id:
        result["chat_peer"] = chat_id
    return result


def get_chats_request(chats_id: list[int], bot_id: int):
    chats_id = _chats_id_to_dict(chats_id)
    result = requests.get(
        f"http://localhost:1111/cmd/ch/{bot_id}", params=chats_id
    )  # вынести ссылку в env
    return result.json()


async def get_bots() -> ApiClient:
    """Dependency для получения ApiClient, который сразу выполняет запрос."""
    api_client = ApiClient(base_url="http://bots:1111/cmd")

    return api_client
