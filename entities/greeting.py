from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AudienceLevel(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    VIP = "vip"


@dataclass(slots=True)
class GreetingRequestEntity:
    name: str
    language: str
    audience: AudienceLevel = AudienceLevel.CASUAL
    excited: bool = False


@dataclass(slots=True)
class GreetingEntity:
    message: str
    language: str
    audience: AudienceLevel
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class GreetingStatsEntity:
    total_requests: int
    requests_by_language: dict[str, int]
