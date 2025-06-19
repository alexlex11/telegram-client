from typing import AsyncGenerator

from fastapi import Depends
from src.config.settings import settings
from src.core.api_clients.openai import OpenAIClient
from src.services.ai import AIService


async def get_openaiclient() -> OpenAIClient:
    return OpenAIClient(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
    )


async def get_aiservice(
    client: OpenAIClient = Depends(get_openaiclient),
) -> AsyncGenerator[AIService, None]:
    async with client:
        yield AIService(client=client)
