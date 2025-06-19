import logging

from src.domain.common.service import BaseService
from src.domain.telegram.events.message import (
    TelegramMessageReceived,
)
from src.domain.telegram.services.manager import TelegramClientManager
from telethon import events

logger = logging.getLogger(__name__)


class TelegramListener(BaseService):
    def __init__(self, manager: TelegramClientManager):
        super().__init__()
        self.manager = manager

    async def start_listening(self) -> None:
        clients = await self.manager.get_connected_clients()
        for client in clients.values():

            @client.on(events.NewMessage)
            async def handle_new_message(event: events.NewMessage.Event):
                message = event.message

                telegram_event = TelegramMessageReceived(
                    id=message.id,
                    message=message.text,
                    date=message.date,
                    peer_id=str(message.peer_id),
                    from_id=str(message.from_id) if message.from_id else None,
                    is_outgoing=message.out,
                    media_type=(
                        message.media.__class__.__name__ if message.media else None
                    ),
                    reply_to_msg_id=(
                        message.reply_to.reply_to_msg_id if message.reply_to else None
                    ),
                    forwarded_from=(
                        str(message.fwd_from.from_id) if message.fwd_from else None
                    ),
                )

                await self._record_event(telegram_event)
