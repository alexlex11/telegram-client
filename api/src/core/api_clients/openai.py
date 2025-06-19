import logging
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class OpenAIClient(BaseAPIClient):
    """Специализированный клиент для OpenAI."""

    api_key: str
    base_url: str
    model: str = "gpt-4.1-nano"
    _client: AsyncOpenAI = field(init=False)

    def __post_init__(self):
        self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def request(self, **kwargs) -> Any:
        if "model" not in kwargs:
            kwargs["model"] = self.model
        return await self._client.chat.completions.create(**kwargs)

    async def close(self):
        await self._client.close()
