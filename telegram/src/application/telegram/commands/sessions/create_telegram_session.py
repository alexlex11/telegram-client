import logging
from dataclasses import dataclass

from didiator import EventMediator
from src.application.common.command import Command, CommandHandler
from src.application.common.interfaces.uow import UnitOfWork
from src.domain.telegram.services.sessions import SessionMaker
from src.domain.telegram.value_objects.phone import PhoneNumber

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateTelegramSession(Command[str]):
    api_id: int
    api_hash: int
    phone: str


class CreateTelegramSessionHandler(CommandHandler[CreateTelegramSession, str]):
    def __init__(
        self,
        session_service: SessionMaker,
        uow: UnitOfWork,
        mediator: EventMediator,
    ) -> None:
        self._session_service = session_service
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: CreateTelegramSession) -> str:
        api_id = command.api_id
        api_hash = command.api_hash
        phone = PhoneNumber(command.phone)

        phone_code_hash = await self._session_service.create_and_validate_session(
            api_id, api_hash, phone
        )
        await self._mediator.publish(self._session_service.pull_events())
        await self._uow.commit()

        logger.info("Session created whitout auth.", extra={"phone": phone})

        return phone_code_hash
