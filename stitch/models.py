from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Any, Union

@dataclass(frozen=True)
class A2AContext:
    agent_handle: str
    target_handle: str
    task_id: str

@dataclass(frozen=True)
class PermissionPolicy:
    whitelist_emails: List[str] = field(default_factory=list)
    blacklist_emails: List[str] = field(default_factory=list)
    whitelist_phones: List[str] = field(default_factory=list)
    blacklist_phones: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ContactMemory:
    memory_id: str
    contact_id: str
    text: str
    citations: List[str] = field(default_factory=list)

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
    contact_id: Optional[str] = None
    a2a_context: Optional[Union[A2AContext, Dict[str, Any]]] = None
    permission_policy: Optional[Union[PermissionPolicy, Dict[str, Any]]] = None

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
    permission_policy: Optional[Union[PermissionPolicy, Dict[str, Any]]] = None
