import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import httpx

from .base import BaseAPIClient


@dataclass
class HTTPAPIClient(BaseAPIClient):
    """Конкретная реализация базового API клиента с httpx."""

    base_url: str
    default_headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 60.0
    _client: httpx.AsyncClient = field(init=False, repr=False)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(__name__), repr=False
    )

    def __post_init__(self):
        """Инициализация клиента после создания экземпляра."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=self.timeout,
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        auth: Optional[Any] = None,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        **kwargs: Any,
    ) -> Union[Any, None]:
        """Реквест на внешний API ."""
        try:
            all_headers = {**self.default_headers, **(headers or {})}

            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                data=data,
                json=json,
                headers=all_headers,
                cookies=cookies,
                auth=auth,
                timeout=timeout or self.timeout,
                follow_redirects=follow_redirects,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._logger.error(
                f"HTTP error {e.response.status_code} for {method} {endpoint}: {e}"
            )
        except httpx.RequestError as e:
            self._logger.error(f"Request failed for {method} {endpoint}: {e}")
        except Exception:
            self._logger.exception(f"Unexpected error for {method} {endpoint}")
        return None

    async def close(self) -> None:
        """Закрытие клиента с проверкой на уже закрытое состояние."""
        if hasattr(self, "_client") and self._client:
            await self._client.aclose()
            self._client = None

    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Union[Any, None]:
        """Выполняет GET-запрос."""
        return await self.request(
            "GET", endpoint, params=params, headers=headers, **kwargs
        )

    async def post(
        self,
        endpoint: str,
        *,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Union[Any, None]:
        """Выполняет POST-запрос."""
        return await self.request(
            "POST", endpoint, data=data, json=json, headers=headers, **kwargs
        )

    async def put(
        self,
        endpoint: str,
        *,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Union[Any, None]:
        """Выполняет PUT-запрос."""
        return await self.request(
            "PUT", endpoint, data=data, json=json, headers=headers, **kwargs
        )

    async def patch(
        self,
        endpoint: str,
        *,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Union[Any, None]:
        """Выполняет PATCH-запрос."""
        return await self.request(
            "PATCH", endpoint, data=data, json=json, headers=headers, **kwargs
        )

    async def delete(
        self, endpoint: str, *, headers: Optional[Dict[str, str]] = None, **kwargs: Any
    ) -> Union[Any, None]:
        """Выполняет DELETE-запрос."""
        return await self.request("DELETE", endpoint, headers=headers, **kwargs)
