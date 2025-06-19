from datetime import datetime
from typing import Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .settings import settings

engine = create_engine(settings.db_url)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


def session_getter() -> Annotated[Annotated, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
