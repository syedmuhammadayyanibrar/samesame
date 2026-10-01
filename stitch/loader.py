from pathlib import Path
from typing import List, Dict, Any, Union
import yaml
from stitch.models import Message, Identity, Scenario

def load_scenario_from_dict(data: Dict[str, Any]) -> Scenario:
    identities = [
        Identity(
            identity_id=item["identity_id"],
            canonical_name=item["canonical_name"],
            canonical_email=item.get("canonical_email"),
            canonical_phone=item.get("canonical_phone")
        )
        for item in data.get("true_identities", [])
    ]
    messages = [
        Message(
            message_id=item["message_id"],
            timestamp=str(item["timestamp"]),
            channel=item["channel"],
            sender_email=item.get("sender_email"),
            sender_phone=item.get("sender_phone"),
            display_name=item.get("display_name"),
            text=item["text"],
            true_identity_id=item.get("true_identity_id")
        )
        for item in data.get("messages", [])
    ]
    return Scenario(
        scenario_id=data["scenario_id"],
        title=data["title"],
        ambiguity_type=data["ambiguity_type"],
        true_identities=identities,
        messages=messages
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
