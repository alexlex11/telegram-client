from dataclasses import dataclass, field

from src.infrastructure.db.config import DBConfig
from src.infrastructure.logs.config import LoggingConfig
from src.infrastructure.message_broker.config import EventBusConfig


@dataclass
class APIConfig:
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = __debug__


@dataclass
class Config:
    db: DBConfig = field(default_factory=DBConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    api: APIConfig = field(default_factory=APIConfig)
    event_bus: EventBusConfig = field(default_factory=EventBusConfig)
