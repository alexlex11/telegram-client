from src.application.common.exceptions import MappingError
from src.domain.telegram.events.message import TelegramMessageReceived
from src.infrastructure.event_bus import events as integration_events

DomainEvents = TelegramMessageReceived


def convert_telegram_message_received_to_integration(
    event: TelegramMessageReceived,
) -> integration_events.TelegramMessageReceived:
    return integration_events.TelegramMessageReceived(
        id=event.id,
        message=event.message,
        date=event.date,
        peer_id=event.peer_id,
        from_id=event.from_id,
        is_outgoing=event.is_outgoing,
        media_type=event.media_type,
        reply_to_msg_id=event.reply_to_msg_id,
        forwarded_from=event.forwarded_from,
    )


def convert_domain_event_to_integration(
    event: DomainEvents,
) -> integration_events.IntegrationEvent:
    match event:
        case TelegramMessageReceived():
            return convert_telegram_message_received_to_integration(event)
        case _:
            raise MappingError(f"Event {event} cannot be mapped to integration event")
