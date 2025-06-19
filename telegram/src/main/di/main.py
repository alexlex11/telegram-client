import aio_pika
from di import Container, bind_by_type
from di.api.providers import DependencyProviderType
from di.api.scopes import Scope
from di.dependent import Dependent
from di.executors import AsyncExecutor
from didiator import CommandMediator, EventMediator, Mediator, QueryMediator
from didiator.interface.utils.di_builder import DiBuilder
from didiator.utils.di_builder import DiBuilderImpl
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from src.application.common.interfaces.uow import UnitOfWork
from src.infrastructure.event_bus.event_bus import EventBusImpl
from src.infrastructure.message_broker.interface import MessageBroker
from src.infrastructure.message_broker.message_broker import MessageBrokerImpl
from src.main.di.constants import DiScope
from src.main.di.db import build_sa_session
from src.main.di.message_broker import build_rq_channel, build_rq_transaction
from src.main.di.uow import build_uow
from src.main.mediator.utils import get_mediator


def init_di_builder() -> DiBuilder:
    di_container = Container()
    di_executor = AsyncExecutor()
    di_scopes = [DiScope.APP, DiScope.REQUEST]
    di_builder = DiBuilderImpl(di_container, di_executor, di_scopes=di_scopes)
    return di_builder


def setup_di_builder(
    di_builder: DiBuilder,
    di_engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
    rq_connection_pool: aio_pika.pool.Pool[aio_pika.abc.AbstractConnection],
    rq_channel_pool: aio_pika.pool.Pool[aio_pika.abc.AbstractChannel],
) -> None:
    di_builder.bind(
        bind_by_type(Dependent(lambda *args: di_builder, scope=DiScope.APP), DiBuilder)
    )
    di_builder.bind(
        bind_by_type(Dependent(build_uow, scope=DiScope.REQUEST), UnitOfWork)
    )
    setup_mediator_factory(di_builder, get_mediator, DiScope.REQUEST)
    setup_db_factories(di_builder, di_engine, session_factory)
    setup_event_bus_factories(di_builder, rq_connection_pool, rq_channel_pool)


def setup_mediator_factory(
    di_builder: DiBuilder,
    mediator_factory: DependencyProviderType,
    scope: Scope,
) -> None:
    di_builder.bind(bind_by_type(Dependent(mediator_factory, scope=scope), Mediator))
    di_builder.bind(
        bind_by_type(Dependent(mediator_factory, scope=scope), QueryMediator)
    )
    di_builder.bind(
        bind_by_type(Dependent(mediator_factory, scope=scope), CommandMediator)
    )
    di_builder.bind(
        bind_by_type(Dependent(mediator_factory, scope=scope), EventMediator)
    )


def setup_db_factories(
    di_builder: DiBuilder,
    db_engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    di_builder.bind(
        bind_by_type(Dependent(lambda *args: db_engine, scope=DiScope.APP), AsyncEngine)
    )
    di_builder.bind(
        bind_by_type(
            Dependent(lambda *args: session_factory, scope=DiScope.APP),
            async_sessionmaker[AsyncSession],
        ),
    )
    di_builder.bind(
        bind_by_type(Dependent(build_sa_session, scope=DiScope.REQUEST), AsyncSession)
    )


def setup_event_bus_factories(
    di_builder: DiBuilder,
    rq_connection_pool: aio_pika.pool.Pool[aio_pika.abc.AbstractConnection],
    rq_channel_pool: aio_pika.pool.Pool[aio_pika.abc.AbstractChannel],
) -> None:
    di_builder.bind(
        bind_by_type(
            Dependent(lambda *args: rq_connection_pool, scope=DiScope.APP),
            aio_pika.pool.Pool[aio_pika.abc.AbstractConnection],
        ),
    )
    di_builder.bind(
        bind_by_type(
            Dependent(lambda *args: rq_channel_pool, scope=DiScope.APP),
            aio_pika.pool.Pool[aio_pika.abc.AbstractChannel],
        ),
    )
    di_builder.bind(
        bind_by_type(
            Dependent(build_rq_channel, scope=DiScope.REQUEST),
            aio_pika.abc.AbstractChannel,
        ),
    )
    di_builder.bind(
        bind_by_type(
            Dependent(build_rq_transaction, scope=DiScope.REQUEST),
            aio_pika.abc.AbstractTransaction,
        ),
    )
    di_builder.bind(
        bind_by_type(Dependent(MessageBrokerImpl, scope=DiScope.REQUEST), MessageBroker)
    )
    di_builder.bind(
        bind_by_type(Dependent(EventBusImpl, scope=DiScope.REQUEST), EventBusImpl)
    )
