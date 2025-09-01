import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.telemetry import get_correlation_id


@dataclass
class AuditEvent:
    """Represents an audit event with immutable data."""

    timestamp: datetime
    correlation_id: str
    event_type: str
    actor: str
    resource: str
    action: str
    data: dict[str, Any]
    signature: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "resource": self.resource,
            "action": self.action,
            "data": self.data,
            "signature": self.signature,
        }


class AuditLogger:
    """Immutable audit logger with HMAC integrity."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode("utf-8")
        self.logger = logging.getLogger(__name__)

    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for data integrity."""
        return hmac.new(self.secret_key, data.encode("utf-8"), hashlib.sha256).hexdigest()

    def _create_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Create a signed audit event."""
        correlation_id = get_correlation_id()
        timestamp = datetime.utcnow()

        event_data = {
            "timestamp": timestamp.isoformat(),
            "correlation_id": correlation_id,
            "event_type": event_type,
            "actor": actor,
            "resource": resource,
            "action": action,
            "data": data or {},
        }

        # Create signature from canonical JSON
        canonical_data = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        signature = self._generate_signature(canonical_data)

        return AuditEvent(
            timestamp=timestamp,
            correlation_id=correlation_id,
            event_type=event_type,
            actor=actor,
            resource=resource,
            action=action,
            data=data or {},
            signature=signature,
        )

    def log_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log an audit event and return it."""
        event = self._create_event(event_type, actor, resource, action, data)

        # Log to application logger as well
        self.logger.info(
            f"AUDIT: {event_type} - {actor} {action} {resource}",
            extra={"correlation_id": event.correlation_id, "audit_event": event.to_dict()},
        )

        return event

    def verify_event(self, event: AuditEvent) -> bool:
        """Verify the integrity of an audit event."""
        event_dict = event.to_dict()
        signature = event_dict.pop("signature")

        canonical_data = json.dumps(event_dict, sort_keys=True, separators=(",", ":"))
        expected_signature = self._generate_signature(canonical_data)

        return hmac.compare_digest(signature, expected_signature)
