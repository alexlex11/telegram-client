import asyncio
import logging

import websockets
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.api_client import ApiClient
from src.auth.dependencies import get_current_user
from src.users.models import User

from .dependencies import get_message_list_from_bots_api
from .exceptions import CannotGetMessages

# from .service import connect_and_receive

logger = logging.getLogger(__name__)

message_router = APIRouter(prefix="/messages", tags=["Messages"])


@message_router.websocket("/ws/{chat_peer}/{user_peer}")
async def websocket_endpoint(
    websocket: WebSocket, chat_peer: int, user_peer: int
) -> None:
    """Улучшенный WebSocket endpoint с полным контролем состояния."""
    await websocket.accept()
    logger.info(f"New connection: chat={chat_peer}, user={user_peer}")

    connection_alive = True
    external_ws = None

    try:
        # Подключаемся к внешнему WebSocket с таймаутом
        external_ws = await asyncio.wait_for(
            websockets.connect(f"ws://bots:1111/ws/{chat_peer}/{user_peer}"),
            timeout=10.0,
        )
        logger.info("Connected to external WS")

        # Создаем очередь для сообщений между задачами
        # message_queue = asyncio.Queue(maxsize=10)

        async def forward_messages():
            """Пересылает сообщения от клиента к внешнему серверу."""
            nonlocal connection_alive
            try:
                while connection_alive:
                    try:
                        # Таймаут 1 сек для проверки флага connection_alive
                        message = await asyncio.wait_for(
                            websocket.receive_text(), timeout=1.0
                        )
                        await external_ws.send(message)
                        logger.debug(f"Forwarded to external: {message}")
                    except asyncio.TimeoutError:
                        continue
                    except WebSocketDisconnect:
                        logger.info("Client disconnected normally")
                        break
                    except RuntimeError as e:
                        if "WebSocket is not connected" in str(e):
                            logger.info("Client connection lost")
                            break
                        raise
            except Exception as e:
                logger.error(f"Forward error: {str(e)}")
            finally:
                connection_alive = False

        async def receive_messages():
            """Получает сообщения от внешнего сервера и отправляет клиенту."""
            nonlocal connection_alive
            try:
                while connection_alive:
                    try:
                        # Таймаут 1 сек для проверки флага
                        message = await asyncio.wait_for(
                            external_ws.recv(), timeout=1.0
                        )
                        if connection_alive:
                            await websocket.send_text(message)
                            logger.debug(f"Sent to client: {message}")
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        logger.info("External WS closed")
                        break
            except Exception as e:
                logger.error(f"Receive error: {str(e)}")
            finally:
                connection_alive = False

        # Запускаем обе задачи параллельно
        await asyncio.gather(
            forward_messages(), receive_messages(), return_exceptions=True
        )

    except asyncio.TimeoutError:
        logger.error("Timeout connecting to external WS")
        await websocket.send_text("External service timeout")
    except ConnectionRefusedError:
        logger.error("External WS refused connection")
        await websocket.send_text("External service unavailable")
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        await websocket.send_text(f"Server error: {str(e)}")
    finally:
        connection_alive = False
        await external_ws.close()

        try:
            if external_ws and not external_ws.closed:
                await external_ws.close()
        except Exception as e:
            logger.error(f"Error closing external WS: {str(e)}")

        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing client WS: {str(e)}")

        logger.info("Connection fully closed")


@message_router.get(
    "/{account_peer}/{chat_peer}",
    summary="endpoint for get massage history with pagination",
)
async def get_messages_history(
    account_peer: int,
    chat_peer: int,
    offset: int = 0,
    limit: int = 10,
    user: User = Depends(get_current_user),
    bot_client: ApiClient = Depends(get_message_list_from_bots_api),
) -> dict:
    """Pagination messages for chat history."""

    bot_client.endpoint = f"/ms/{account_peer}/{chat_peer}"

    bot_client.params = {"offset": offset, "limit": limit}
    messages = await bot_client.fetch_data()
    if not messages:
        raise CannotGetMessages
    return messages
