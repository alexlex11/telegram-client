from sqlalchemy import update
from sqlalchemy.orm import Session
from src.repositories import BaseRepository

from .models import Chat


class ChatRepository(BaseRepository):
    model = Chat

    @classmethod
    def update(cls, session: Session, soc_net_id: int, **data) -> Chat:
        query = (
            update(Chat)
            .where(Chat.soc_net_id == soc_net_id)
            .values(data)
            .returning(Chat)
        )
        result = session.execute(query)
        return result
