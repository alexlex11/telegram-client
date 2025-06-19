import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class ApiClient:
    """Универсальный клиент для взаимодействия с API."""

    def __init__(self, base_url: str, endpoint: Optional[str] = None, **kwargs: Any):
        self.base_url = base_url
        self._endpoint = endpoint
        self._params = kwargs

    async def fetch_data(self) -> Optional[Any]:
        """Выполняет запрос к API и возвращает результат."""
        if not self.endpoint:
            logger.warning("Endpoint is not set.  Cannot fetch data.")
            return None

        url = f"{self.base_url}{self.endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=self._params
                )  # Асинхронный запрос
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return None

    @property
    def endpoint(self) -> Optional[str]:
        """Возвращает текущий endpoint."""
        return self._endpoint

    @endpoint.setter
    def endpoint(self, new_endpoint: str):
        """Устанавливает новый endpoint."""
        self._endpoint = new_endpoint

    @property
    def params(self) -> Optional[str]:
        """Возвращает текущий endpoint."""
        return self._params

    @params.setter
    def params(self, new_params: str):
        """Устанавливает новый endpoint."""
        self._params = new_params
