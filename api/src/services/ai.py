import logging
from dataclasses import dataclass
from typing import Optional

from openai import APIConnectionError, AuthenticationError, OpenAIError, RateLimitError
from src.core.api_clients.openai import OpenAIClient


@dataclass
class AIService:
    client: OpenAIClient
    _logger: logging.Logger = logging.getLogger(__name__)

    async def generate_text(self, prompt: str) -> Optional[str]:
        """Генерирует текст с обработкой ошибок.

        Args:
            prompt: Текст запроса
            model: Модель ИИ (по умолчанию "gpt-4.1-nano")

        Returns:
            Строка с ответом ИИ или None при ошибке
        """
        try:
            response = await self.client.request(
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except AuthenticationError as e:
            self._logger.error(f"Ошибка аутентификации: {e}")
            raise ValueError("Неверный API-ключ OpenAI") from e

        except RateLimitError as e:
            self._logger.error(f"Превышен лимит запросов: {e}")
            raise RuntimeError("Превышен лимит запросов к OpenAI API") from e

        except APIConnectionError as e:
            self._logger.error(f"Ошибка подключения: {e}")
            raise ConnectionError("Ошибка соединения с OpenAI API") from e

        except OpenAIError as e:
            self._logger.error(f"Ошибка OpenAI API: {e}")
            raise RuntimeError(f"Ошибка при генерации текста: {e}") from e

        except Exception as e:
            self._logger.error(f"Неожиданная ошибка: {e}")
            raise RuntimeError(f"Неизвестная ошибка: {e}") from e
