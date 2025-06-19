import logging
from typing import Dict, List, Optional, Union

from src.domain.common.service import BaseService
from src.domain.telegram.services.manager import TelegramClientManager
from telethon import TelegramClient
from telethon.errors import PeerIdInvalidError
from telethon.tl.types import Dialog, InputPhoto, Message, User

logger = logging.getLogger(__name__)


class TelegramOperations(BaseService):
    def __init__(self, manager: TelegramClientManager):
        super().__init__()
        self.manager = manager
        self._clients: Dict[str, TelegramClient] = self.manager._telegram_clients

    async def _get_client(self, phone: str) -> Optional[TelegramClient]:
        try:
            return self._clients[phone]
        except Exception as e:
            logger.error(f"Error in _get_client for {phone}: {e}", exc_info=True)
            raise e

    async def get_account_by_phone(self, phone: str) -> Optional[User]:
        try:
            client = await self._get_client(phone)
            return await client.get_me()
        except Exception as e:
            logger.error(
                f"Error in get_account_by_phone for {phone}: {e}", exc_info=True
            )
            raise e

    async def get_accounts(self) -> Optional[List[User]]:
        accounts = []
        for phone, client in self._clients.items():
            try:
                account = await client.get_me()
                accounts.append(account)
            except Exception as e:
                logger.error(f"Error in get_accounts: {phone} {e}", exc_info=True)
                raise e
        return accounts

    async def get_dialogs_by_phone(self, phone: str) -> Optional[List[Dialog]]:
        try:
            client = await self._get_client(phone)
            return await client.get_dialogs()
        except Exception as e:
            logger.error(f"Error getting dialogs for {phone}: {e}", exc_info=True)
            raise e

    async def get_account_dialog_by_entity(
        self, entity: Union[str, int], phone: str
    ) -> Optional[Dialog]:
        try:
            client = await self._get_client(phone)
            chat_entity = await client.get_entity(entity)
            dialogs = await client.get_dialogs()
            for chat in dialogs:
                if chat.entity.id == chat_entity.id:
                    return chat
            return None

        except PeerIdInvalidError as e:
            logger.warning(
                f"Peer ID {entity} is invalid in get_account_chat_by_entity."
            )
            raise e
        except Exception as e:
            logger.error(f"Error getting chat by peer {entity}: {e}", exc_info=True)
            raise e

    async def get_messages_by_chat_entity_by_account_phone(
        self, entity: Union[str, int], phone: str, offset_id: int, limit: int = 100
    ) -> Optional[List[Message]]:
        try:
            client = await self._get_client(phone)
            return await client.get_messages(
                entity=entity,
                limit=min(limit, 100),
                offset_id=offset_id,
            )
        except PeerIdInvalidError as e:
            logger.warning(
                msg=(
                    f"Peer ID {entity} is invalid",
                    "in get_messages_by_chat_entity_by_account_phone.",
                )
            )
            raise e
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise e

    async def download_image_by_metadata(
        self,
        phone: str,
        photo_id: int,
        access_hash: int,
        dc_id: int,
        file_reference: bytes = b"",
        mime_type: str = "image/jpeg",
    ) -> Optional[bytes]:
        try:
            client = await self._get_client(phone)
            photo = InputPhoto(
                id=photo_id,
                access_hash=access_hash,
                file_reference=file_reference,
                version=0,
            )

            return await client.download_file(
                photo,
                file=bytes,
                dc_id=dc_id,
            )

        except Exception as e:
            logger.warning(
                f"Error downloading image in download_image_by_metadata: {e}",
                exc_info=True,
            )
            raise e
