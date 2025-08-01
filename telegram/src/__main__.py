import asyncio
import logging

from src.infrastructure.config_loader import load_config
from src.infrastructure.db.main import build_sa_engine, build_sa_session_factory
from src.infrastructure.event_bus.exchanges import declare_exchanges
from src.infrastructure.logs.main import configure_logging
from src.infrastructure.message_broker.main import (
    build_rq_channel_pool,
    build_rq_connection_pool,
)
from src.main.di.constants import DiScope
from src.main.di.main import init_di_builder, setup_di_builder
from src.main.mediator.main import init_mediator, setup_mediator
from src.presentation.api.config import Config
from src.presentation.api.main import init_api, run_api

logger = logging.getLogger(__name__)


async def async_main() -> None:
    config = load_config(Config)
    configure_logging(config.logging)

    logger.info("Launch app")

    async with (
        build_sa_engine(config.db) as db_engine,
        build_rq_connection_pool(config.event_bus) as rq_connection_pool,
        build_rq_channel_pool(rq_connection_pool) as rq_channel_pool,
    ):
        session_factory = build_sa_session_factory(db_engine)
        di_builder = init_di_builder()
        setup_di_builder(
            di_builder, db_engine, session_factory, rq_connection_pool, rq_channel_pool
        )

        mediator = init_mediator(di_builder)
        setup_mediator(mediator)

        async with di_builder.enter_scope(DiScope.APP) as di_state:
            async with di_builder.enter_scope(
                DiScope.REQUEST, state=di_state
            ) as request_di_state:
                await di_builder.execute(
                    declare_exchanges, DiScope.REQUEST, state=request_di_state
                )

            app = init_api(config.api.debug)
            await run_api(app, config.api)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
