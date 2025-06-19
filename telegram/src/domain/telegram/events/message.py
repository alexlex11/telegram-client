from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.common.event import Event


@dataclass(frozen=True)
class TelegramMessageReceived(Event):
    id: int
    message: str
    date: datetime
    peer_id: str
    from_id: Optional[str] = None
    is_outgoing: Optional[bool] = None
    media_type: Optional[str] = None
    reply_to_msg_id: Optional[int] = None
    forwarded_from: Optional[str] = None
