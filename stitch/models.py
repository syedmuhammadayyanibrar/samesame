from dataclasses import dataclass
from typing import Optional, List, Dict, Set, Any

@dataclass(frozen=True)
class Message:
    message_id: str
    timestamp: str
    channel: str
    sender_email: Optional[str]
    sender_phone: Optional[str]
    display_name: Optional[str]
    text: str
    true_identity_id: Optional[str] = None

@dataclass(frozen=True)
class Identity:
    identity_id: str
    canonical_name: str
    canonical_email: Optional[str] = None
    canonical_phone: Optional[str] = None

@dataclass
class Scenario:
    scenario_id: str
    title: str
    ambiguity_type: str
    true_identities: List[Identity]
    messages: List[Message]
