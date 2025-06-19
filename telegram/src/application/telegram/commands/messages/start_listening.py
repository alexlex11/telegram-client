import logging
from dataclasses import dataclass

from didiator import EventMediator
from src.application.common.command import Command, CommandHandler
from src.application.common.interfaces.uow import UnitOfWork
from src.domain.telegram.services.listener import TelegramListener

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StartListening(Command[None]):
    pass


class StartListeningHandler(CommandHandler[StartListening, None]):
    def __init__(
        self,
        listening_service: TelegramListener,
        uow: UnitOfWork,
        mediator: EventMediator,
    ) -> None:
        self._listening_service = listening_service
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: StartListening) -> None:

        await self._listening_service.start_listening()
        await self._mediator.publish(self._listening_service.pull_events())
        await self._uow.commit()

        logger.info("Listening start.")
