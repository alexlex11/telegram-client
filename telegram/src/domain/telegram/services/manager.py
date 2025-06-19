import logging
from typing import Dict, List, Optional, Union

from src.core.telegram.sessions.my_sqlalchemy import AlchemySessionContainer
from src.domain.common.service import BaseService
from telethon import TelegramClient
from telethon.errors import RPCError

logger = logging.getLogger(__name__)


class TelegramClientManager(BaseService):
    def __init__(self, session_container: AlchemySessionContainer):
        super().__init__()
        self.session_container = session_container
        self._telegram_clients: Dict[str, TelegramClient] | None = None

    async def _load_data_from_db(self) -> List[Dict[str, str | int]]:
        try:
            accounts_data = await self.session_container.get_accounts()
            if not accounts_data:
                logger.warning("No accounts found in the database")
                raise Exception("No accounts found in the database")
            return accounts_data
        except Exception as e:
            logger.error(f"Failed to load accounts from DB: {e}")
            raise e

    async def start_client(
        self, account: Dict[str, Union[str, int]]
    ) -> Optional[TelegramClient]:
        try:
            session = self.session_container.new_session(account["session_id"])
            client = TelegramClient(
                session=session, api_id=account["api_id"], api_hash=account["api_hash"]
            )

            if not client.is_connected():
                await client.connect()
            return client

        except RPCError as e:
            logger.error(
                f"Failed to start client for {account['session_id']}: {e}",
                exc_info=True,
            )
            raise e
        except Exception as e:
            logger.error(
                f"Unexpected error for {account['session_id']}: {e}", exc_info=True
            )
            raise e

    async def start_clients(self) -> Dict[str, TelegramClient]:
        accounts_data = self._load_data_from_db()

        for account in accounts_data:
            if account["session_id"] in self._telegram_clients:
                continue

            client = await self.start_client(account)
            if client:
                self._telegram_clients[account["session_id"]] = client
                logger.info(f"Successfully started client for {account['session_id']}")
        if self._telegram_clients:
            return self._telegram_clients
        else:
            raise Exception("No telegram clisent to start.")

    async def close_all(self):
        for client in self._telegram_clients.values():
            await client.disconnect()
        self._telegram_clients.clear()

    async def get_connected_clients(self) -> Dict[str, TelegramClient]:
        return self._telegram_clients
