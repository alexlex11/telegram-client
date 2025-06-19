from src.api_client import ApiClient
from src.config.settings import settings


async def get_message_list_from_bots_api() -> ApiClient:
    """Dependency для получения ApiClient, который сразу выполняет запрос."""
    api_url = f"{settings.bot_host}:{settings.bot_port}/cmd"
    api_client = ApiClient(base_url=api_url)
    return api_client
