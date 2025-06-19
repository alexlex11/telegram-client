from src.infrastructure.message_broker.message_broker import MessageBroker

TELEGRAM_EXCHANGE = "telegram"


async def declare_exchanges(message_broker: MessageBroker) -> None:
    await message_broker.declare_exchange(TELEGRAM_EXCHANGE)
