from datetime import datetime

from pydantic import UUID4, BaseModel
from src.pagination import PaginationModel


class SDisplayMessage(BaseModel):
    id: UUID4
    message_type: str
    content: str
    time_stamp: str


class SPagMessages(PaginationModel):
    messages: list[SDisplayMessage]


class SDisplayChat(BaseModel):
    last_time_online: datetime | None
    peer: int
    avatar: str | None
    name: str
    last_message: dict


class SDisplayAllChats(BaseModel):
    chats: list[SDisplayChat]
