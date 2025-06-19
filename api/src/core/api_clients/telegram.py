from dataclasses import dataclass

from src.config.settings import settings

from .base import HTTPAPIClient


@dataclass
class TelegramAPIClient(HTTPAPIClient):
    base_url: str = settings.bot_api_url
