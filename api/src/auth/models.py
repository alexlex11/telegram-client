from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.connections import Base


class Password(Base):
    __tablename__ = "passwords"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    hashed_pass: Mapped[str] = mapped_column(nullable=False)

    user = relationship("User", back_populates="password")

    def __str__(self):
        return f"password of {self.id}: {self.hashed_pass}"
