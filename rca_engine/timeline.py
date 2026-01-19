from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TimelineEvent:
    """
    Represents a single moment in an incident timeline.
    """

    # When did this event occur (epoch ms or iso string)
    timestamp: float

    # Which service experienced this event
    service: str

    # Type of event
    # start | root_failure | propagated_failure | recovery
    event_type: str

    # Incident this event belongs to
    incident_id: Optional[str]

    # Optional explanation (human-readable)
    message: Optional[str] = None
