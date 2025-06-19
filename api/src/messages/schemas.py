from datetime import datetime

from pydantic import BaseModel
from src.pagination import PaginationModel


class SDisplayMessage(BaseModel):
    peer: int
    m_type: str
    content: str
    time_stamp: datetime


class SPagMessages(PaginationModel):
    messages: list[SDisplayMessage]
