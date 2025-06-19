from uuid import UUID, uuid4

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from src.config.connections import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    soc_net_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unread_messages: Mapped[int] = mapped_column(default=0)
    # account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"),nullable=False)

    # account = relationship("Account", back_populates="chats")


"""
class ChatMembers(Base):
    ...
"""
