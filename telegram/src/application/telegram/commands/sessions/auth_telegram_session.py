import logging
from dataclasses import dataclass
from typing import Optional

from didiator import EventMediator
from src.application.common.command import Command, CommandHandler
from src.application.common.interfaces.uow import UnitOfWork
from src.domain.telegram.services.sessions import SessionMaker
from src.domain.telegram.value_objects.phone import PhoneNumber
from telethon.tl.types import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthTelegramSession(Command[User]):
    phone: str
    code: str
    phone_code_hash: str
    password: Optional[str] = None


class AuthTelegramSessionHandler(CommandHandler[AuthTelegramSession, User]):
    def __init__(
        self,
        session_service: SessionMaker,
        uow: UnitOfWork,
        mediator: EventMediator,
    ) -> None:
        self._session_service = session_service
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: AuthTelegramSession) -> User:
        code = command.code
        phone_code_hash = command.phone_code_hash
        password = command.password
        phone = PhoneNumber(command.phone)

        user = await self._session_service.confirm_session(
            code, phone_code_hash, phone, password
        )
        await self._mediator.publish(self._session_service.pull_events())
        await self._uow.commit()

        logger.info("Session auth.", extra={"phone": phone})

        return user
