"""
Event Dispatcher Service

Persists system events and dispatches them to EventListener for reactive workflows.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from config import get_logger
from database import db_manager
from database.models.event import EventLevel, EventType
from database.repositories import event_repository
from services.event_listener import event_listener

logger = get_logger(__name__)


class EventDispatcher:
    """Persist and dispatch events in one place."""

    async def emit(
        self,
        *,
        title: str,
        message: str,
        event_name: str,
        level: EventLevel = EventLevel.INFO,
        event_type: EventType = EventType.NOTIFICATION,
        shop_id: Optional[int] = None,
        user_id: Optional[int] = None,
        task_id: Optional[int] = None,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        dispatch: bool = True,
    ) -> Dict[str, Any]:
        """
        Create event row and optionally dispatch to listener.
        """
        payload_details = dict(details or {})
        payload_details.setdefault("event_name", event_name)

        async with db_manager.get_async_session() as db:
            event = await event_repository.create(
                db,
                {
                    "user_id": user_id,
                    "shop_id": shop_id,
                    "task_id": task_id,
                    "event_type": event_type,
                    "event_level": level,
                    "title": title,
                    "message": message,
                    "details": payload_details,
                    "source": source,
                    "event_time": datetime.utcnow(),
                },
            )

        dispatched = False
        if dispatch:
            try:
                await event_listener.on_event(event)
                dispatched = True
            except Exception as exc:
                logger.warning("Event dispatch failed for event_id=%s: %s", event.id, exc)

        return {
            "event_id": event.id,
            "event_name": event_name,
            "event_type": event_type,
            "dispatched": dispatched,
        }


event_dispatcher = EventDispatcher()

