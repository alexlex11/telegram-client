from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.chats import ChatService
from src.config.connections import session_getter

from . import schemas as sch

wb_router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@wb_router.post(path="/chat", summary="Get count of new messages")
def update_new_users_messages(
    date: sch.SNewMessage,
    session: Session = Depends(session_getter),
):
    ChatService.update_unread_messages(session, date.chat_id, date.bot_id)
    session.commit()
