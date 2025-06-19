import logging
import re
from dataclasses import dataclass
from typing import Optional

from src.core.telegram.sessions.my_sqlalchemy import AlchemySessionContainer
from src.domain.common.service import BaseService
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.types import User

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class SessionMaker(BaseService):
    def __init__(self, session_container: AlchemySessionContainer):
        super().__init__()
        self.session_container = session_container

    async def _validate_phone_number(self, phone: str) -> str:
        try:
            cleaned = re.sub(r"[^\d]", "", phone.strip())

            if not cleaned:
                raise Exception("Phone number cannot be empty")

            if len(cleaned) < 10:
                raise Exception("Phone number is too short")

            if cleaned.startswith("8") and len(cleaned) == 11:
                cleaned = "7" + cleaned[1:]
            elif cleaned.startswith("+7") and len(cleaned) == 12:
                cleaned = "7" + cleaned[2:]
            elif not (cleaned.startswith("7") or cleaned.startswith("8")):
                if len(cleaned) == 10:
                    cleaned = "7" + cleaned
                else:
                    raise Exception("Invalid phone number format")

            if len(cleaned) != 11:
                raise Exception("Phone number must be 11 digits long")

            return cleaned
        except Exception as e:
            logger.error(f"Phone validation failed for '{phone}': {e}", exc_info=True)
            raise Exception(f"Invalid phone number format: {e}")

    async def _get_account_by_phone(
        self,
        phone: str,
        api_id: int | None = None,
        api_hash: str | None = None,
    ) -> TelegramClient:
        try:
            valid_phone = await self._validate_phone_number(phone)
            client_info = self.session_container.get_info_by_phone(phone=valid_phone)

            if client_info:
                session = self.session_container.new_session(valid_phone)
                client = TelegramClient(
                    session, client_info["api_id"], client_info["api_hash"]
                )
            else:
                if not api_id or not api_hash:
                    raise ValueError("API credentials required for new account")

                self.session_container.add_account(
                    session_id=valid_phone, api_hash=api_hash, api_id=api_id
                )
                session = self.session_container.new_session(f"{valid_phone}")
                client = TelegramClient(session, api_id, api_hash)

            return client
        except PhoneNumberInvalidError as e:
            logger.error(f"Invalid phone number: {phone}", exc_info=True)
            raise Exception(f"Invalid phone number: {e}")
        except Exception as e:
            logger.error(f"Failed to get Telegram client: {e}", exc_info=True)
            raise Exception(f"Failed to initialize Telegram client: {e}")

    async def create_and_validate_session(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
    ) -> str:
        """Создает сессию, отправляет код и сохраняет данные в БД."""
        try:
            valid_phone = await self._validate_phone_number(phone)
            client = await self._get_account_by_phone(
                api_id=api_id, api_hash=api_hash, phone=phone
            )

            try:
                if not client.is_connected():
                    await client.connect()

                if await client.is_user_authorized():
                    raise Exception("Account already authorized")

                sent = await client.send_code_request(valid_phone)
                phone_code_hash = sent.phone_code_hash

                logger.info(f"Session created for phone: {valid_phone}", exc_info=True)
                return phone_code_hash
            except FloodWaitError as e:
                logger.error(f"Flood wait required: {e}", exc_info=True)
                raise Exception(f"Please wait {e.seconds} seconds before retrying")
            finally:
                await client.disconnect()

        except Exception as e:
            raise e
        except Exception as e:
            logger.error(f"Session creation failed: {e}", exc_info=True)
            raise Exception(f"Failed to create session: {e}")

    async def confirm_session(
        self,
        code: str,
        phone_code_hash: str,
        phone: str,
        password: Optional[str] = None,
    ) -> User:
        """Подтверждает сессию кодом из SMS/2FA."""
        try:
            valid_phone = await self._validate_phone_number(phone)
            client = await self._get_account_by_phone(phone=phone)

            try:
                if not client.is_connected():
                    await client.connect()

                if password:
                    await client.sign_in(
                        phone=valid_phone,
                        code=code,
                        phone_code_hash=phone_code_hash,
                        password=password,
                    )
                else:
                    try:
                        await client.sign_in(
                            phone=valid_phone,
                            code=code,
                            phone_code_hash=phone_code_hash,
                        )
                    except SessionPasswordNeededError:
                        raise Exception("2FA password required")

                user = await client.get_me()
                logger.info(f"Successfully authorized: {user.id}")
                return user

            except PhoneCodeInvalidError:
                raise Exception("Invalid verification code")
            except PhoneCodeExpiredError:
                raise Exception("Verification code expired")
            except FloodWaitError as e:
                raise Exception(f"Please wait {e.seconds} seconds before retrying")
            finally:
                if client.is_connected():
                    await client.disconnect()

        except Exception:
            raise
        except Exception:
            raise
        except Exception as e:
            logger.error(f"Session confirmation failed: {e}", exc_info=True)
            try:
                await self.delete_session(phone)
            except Exception as delete_error:
                logger.error(
                    f"Failed to cleanup session: {delete_error}", exc_info=True
                )
            raise Exception("Authentication failed")

    async def delete_session(self, phone: str) -> bool:
        """Удаляет сессию и чистит данные."""
        try:
            valid_phone = await self._validate_phone_number(phone)

            try:
                client = await self._get_account_by_phone(phone)
                async with client:
                    await client.log_out()
            except Exception as e:
                logger.warning(f"Logout failed: {e}")

            self.session_container.delete(valid_phone)
            logger.info(f"Session deleted for phone: {valid_phone}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session: {e}", exc_info=True)
            raise e
