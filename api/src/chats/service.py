from uuid import UUID

from sqlalchemy.orm import Session
from src.accounts.dependencies import get_account_or_404

from .dependencies import get_chat_or_create, get_chats_id, get_chats_request
from .repositories import ChatRepository


class ChatService:
    @classmethod
    def pagination(cls, session: Session, user_id: UUID):
        account = get_account_or_404(session, user_id=user_id)
        chats_id = get_chats_id(session, account.id)
        chats = get_chats_request(chats_id, account.soc_net_id)
        return chats

    @classmethod
    def update_unread_messages(cls, session: Session, chat_id: int, bot_id: int):
        current_chat = get_chat_or_create(session, chat_id, bot_id)
        messages = current_chat.unread_messages + 1
        new_chat = ChatRepository.update(
            session, soc_net_id=chat_id, unread_messages=messages
        )
        return new_chat
