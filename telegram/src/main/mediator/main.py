import logging

from didiator import (
    CommandDispatcherImpl,
    EventObserverImpl,
    Mediator,
    MediatorImpl,
    QueryDispatcherImpl,
)
from didiator.interface.utils.di_builder import DiBuilder
from didiator.middlewares.di import DiMiddleware, DiScopes
from didiator.middlewares.logging import LoggingMiddleware
from src.application.telegram.commands.messages import (
    StartListening,
    StartListeningHandler,
)
from src.application.telegram.commands.sessions import (
    AuthTelegramSession,
    AuthTelegramSessionHandler,
    CreateTelegramSession,
    CreateTelegramSessionHandler,
    DeleteTelegramSession,
    DeleteTelegramSessionHandler,
)
from src.application.telegram.query.accounts import (
    GetTelegramAccountByPhone,
    GetTelegramAccountByPhoneHandler,
    GetTelegramAccounts,
    GetTelegramAccountsHandler,
)
from src.application.telegram.query.dialogs import (
    GetTelegramDialogByEntity,
    GetTelegramDialogByEntityHandler,
    GetTelegramDialogsByPhone,
    GetTelegramDialogsByPhoneHandler,
)
from src.application.telegram.query.messages import (
    GetTelegramMessagesByEntityByPhone,
    GetTelegramMessagesByEntityByPhoneHandler,
)
from src.domain.common.event import Event
from src.infrastructure.event_bus.event_handler import EventHandlerPublisher
from src.infrastructure.logs.event_handler import EventLogger
from src.main.di.constants import DiScope


def init_mediator(di_builder: DiBuilder) -> Mediator:
    middlewares = (
        LoggingMiddleware("mediator", level=logging.DEBUG),
        DiMiddleware(di_builder, scopes=DiScopes(DiScope.REQUEST)),
    )
    command_dispatcher = CommandDispatcherImpl(middlewares=middlewares)
    query_dispatcher = QueryDispatcherImpl(middlewares=middlewares)
    event_observer = EventObserverImpl(middlewares=middlewares)

    mediator = MediatorImpl(command_dispatcher, query_dispatcher, event_observer)
    return mediator


def setup_mediator(mediator: Mediator) -> None:
    mediator.register_command_handler(StartListening, StartListeningHandler)
    mediator.register_command_handler(
        CreateTelegramSession, CreateTelegramSessionHandler
    )
    mediator.register_command_handler(AuthTelegramSession, AuthTelegramSessionHandler)
    mediator.register_command_handler(
        DeleteTelegramSession, DeleteTelegramSessionHandler
    )
    mediator.register_query_handler(
        GetTelegramAccountByPhone, GetTelegramAccountByPhoneHandler
    )
    mediator.register_query_handler(
        GetTelegramMessagesByEntityByPhone, GetTelegramMessagesByEntityByPhoneHandler
    )
    mediator.register_query_handler(
        GetTelegramDialogByEntity, GetTelegramDialogByEntityHandler
    )
    mediator.register_query_handler(
        GetTelegramDialogsByPhone, GetTelegramDialogsByPhoneHandler
    )
    mediator.register_query_handler(GetTelegramAccounts, GetTelegramAccountsHandler)
    mediator.register_event_handler(Event, EventLogger)
    mediator.register_event_handler(Event, EventHandlerPublisher)
