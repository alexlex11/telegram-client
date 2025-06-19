from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.connections import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(nullable=False)
    password_id: Mapped[UUID] = mapped_column(
        ForeignKey("passwords.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    password = relationship("Password", back_populates="user")
    info = relationship("Info", back_populates="user")
    # accounts = relationship("Account", back_populates="user")

    def __str__(self):
        return f"{self.username}"


class Info(Base):
    __tablename__ = "info"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="info")
