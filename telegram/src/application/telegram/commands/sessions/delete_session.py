import logging
from dataclasses import dataclass

from didiator import EventMediator
from src.application.common.command import Command, CommandHandler
from src.application.common.interfaces.uow import UnitOfWork
from src.domain.telegram.services.sessions import SessionMaker
from src.domain.telegram.value_objects.phone import PhoneNumber

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteTelegramSession(Command[None]):
    phone: str


class DeleteTelegramSessionHandler(CommandHandler[DeleteTelegramSession, None]):
    def __init__(
        self,
        session_service: SessionMaker,
        uow: UnitOfWork,
        mediator: EventMediator,
    ) -> None:
        self._session_service = session_service
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: DeleteTelegramSession) -> None:
        phone = PhoneNumber(command.phone)

        await self._session_service.delete_session(phone)
        await self._mediator.publish(self._session_service.pull_events())
        await self._uow.commit()

        logger.info("Session created whitout auth.", extra={"phone": phone})
