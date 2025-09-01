import json
import os

from core.events import BaseEvent


class WAL:
    """Write-Ahead Log for event persistence."""

    def __init__(self, log_file: str):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Ensure the log file exists."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("")  # Create empty file

    def append(self, event: BaseEvent) -> None:
        """Append an event to the WAL."""
        with open(self.log_file, "a") as f:
            entry = {
                "type": event.type,
                "data": event.data,
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "correlation_id": event.correlation_id,
            }
            f.write(json.dumps(entry) + "\n")

    def recover(self) -> list[BaseEvent]:
        """Recover events from the WAL."""
        events = []
        if not os.path.exists(self.log_file):
            return events

        with open(self.log_file) as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        event = BaseEvent(
                            type=entry["type"],
                            data=entry["data"],
                            id=entry["id"],
                            timestamp=entry["timestamp"],
                            correlation_id=entry.get("correlation_id"),
                        )
                        events.append(event)
                    except (json.JSONDecodeError, KeyError):
                        # Skip corrupted entries
                        continue
        return events

    def clear(self) -> None:
        """Clear the WAL (for testing)."""
        with open(self.log_file, "w") as f:
            f.write("")
