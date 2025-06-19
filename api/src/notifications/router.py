import logging

from fastapi import APIRouter, WebSocket

logger = logging.getLogger(__name__)

notifications_router = APIRouter(prefix="/ws", tags=["Notifications"])


@notifications_router.websocket("/{user}")
async def websocket_endpoint(
    websocket: WebSocket, chat_peer: int, user_peer: int
) -> None:

    return
