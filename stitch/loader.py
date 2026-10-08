from pathlib import Path
from typing import List, Dict, Any, Union
import yaml
from stitch.models import Message, Identity, Scenario, A2AContext, PermissionPolicy

def load_scenario_from_dict(data: Dict[str, Any]) -> Scenario:
    scenario_policy_raw = data.get("permission_policy")
    scenario_policy = None
    if scenario_policy_raw:
        scenario_policy = PermissionPolicy(
            whitelist_emails=list(scenario_policy_raw.get("whitelist_emails", [])),
            blacklist_emails=list(scenario_policy_raw.get("blacklist_emails", [])),
            whitelist_phones=list(scenario_policy_raw.get("whitelist_phones", [])),
            blacklist_phones=list(scenario_policy_raw.get("blacklist_phones", []))
        )

    identities = [
        Identity(
            identity_id=item["identity_id"],
            canonical_name=item["canonical_name"],
            canonical_email=item.get("canonical_email"),
            canonical_phone=item.get("canonical_phone")
        )
        for item in data.get("true_identities", [])
    ]

    messages = []
    for item in data.get("messages", []):
        a2a_raw = item.get("a2a_context")
        a2a_ctx = None
        if a2a_raw:
            a2a_ctx = A2AContext(
                agent_handle=a2a_raw.get("agent_handle", ""),
                target_handle=a2a_raw.get("target_handle", ""),
                task_id=a2a_raw.get("task_id", "")
            )

        policy_raw = item.get("permission_policy")
        msg_policy = scenario_policy
        if policy_raw:
            msg_policy = PermissionPolicy(
                whitelist_emails=list(policy_raw.get("whitelist_emails", [])),
                blacklist_emails=list(policy_raw.get("blacklist_emails", [])),
                whitelist_phones=list(policy_raw.get("whitelist_phones", [])),
                blacklist_phones=list(policy_raw.get("blacklist_phones", []))
            )

        messages.append(
            Message(
                message_id=item["message_id"],
                timestamp=str(item["timestamp"]),
                channel=item["channel"],
                sender_email=item.get("sender_email"),
                sender_phone=item.get("sender_phone"),
                display_name=item.get("display_name"),
                text=item["text"],
                true_identity_id=item.get("true_identity_id"),
                contact_id=item.get("contact_id"),
                a2a_context=a2a_ctx,
                permission_policy=msg_policy
            )
        )

    return Scenario(
        scenario_id=data["scenario_id"],
        title=data["title"],
        ambiguity_type=data["ambiguity_type"],
        true_identities=identities,
        messages=messages,
        permission_policy=scenario_policy
    )

def load_scenario_file(file_path: Union[str, Path]) -> Scenario:
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return load_scenario_from_dict(data)

def load_scenarios_from_directory(dir_path: Union[str, Path]) -> List[Scenario]:
    path = Path(dir_path)
    scenarios = []
    for file in sorted(path.glob("*.yaml")):
        scenarios.append(load_scenario_file(file))
    return scenarios
