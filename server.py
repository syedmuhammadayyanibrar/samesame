import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from stitch.models import Message, Scenario, A2AContext, PermissionPolicy
from stitch.loader import load_scenario_file
from stitch.evaluation import evaluate_scenario
from stitch.strategies.composite import CompositeStitcher
from stitch.strategies.exact import ExactMatchStitcher
from stitch.strategies.fuzzy import FuzzyMatchStitcher
from stitch.strategies.embedding import EmbeddingMatchStitcher
from stitch.strategies.permission import PermissionAwareStitcher
from stitch.strategies.contact import ContactResolutionStitcher
from stitch.strategies.a2a import A2AStitcher

app = FastAPI(title="SameSame Identity Stitching Engine")

DATA_DIR = Path(__file__).parent / "data"
DEV_DIR = DATA_DIR / "dev"
TEST_DIR = DATA_DIR / "test"
WEB_DIR = Path(__file__).parent / "web"

class A2APayload(BaseModel):
    agent_handle: Optional[str] = None
    target_handle: Optional[str] = None
    task_id: Optional[str] = None

class PermissionPayload(BaseModel):
    whitelist_emails: List[str] = []
    blacklist_emails: List[str] = []
    whitelist_phones: List[str] = []
    blacklist_phones: List[str] = []

class MessagePayload(BaseModel):
    message_id: str
    timestamp: str = "2026-10-08T12:00:00Z"
    channel: str = "email"
    sender_email: Optional[str] = None
    sender_phone: Optional[str] = None
    display_name: Optional[str] = None
    text: str
    true_identity_id: Optional[str] = None
    contact_id: Optional[str] = None
    a2a_context: Optional[A2APayload] = None
    permission_policy: Optional[PermissionPayload] = None

class StitchRequest(BaseModel):
    strategy: str = "composite"
    messages: List[MessagePayload]
    permission_policy: Optional[PermissionPayload] = None

def get_stitcher_instance(name: str):
    key = name.strip().lower()
    if key == "composite":
        return CompositeStitcher()
    if key == "exact":
        return ExactMatchStitcher()
    if key == "fuzzy":
        return FuzzyMatchStitcher()
    if key == "embedding":
        return EmbeddingMatchStitcher()
    if key == "contact":
        return ContactResolutionStitcher(ExactMatchStitcher())
    if key == "permission":
        return PermissionAwareStitcher(ExactMatchStitcher())
    if key == "a2a":
        return A2AStitcher()
    return CompositeStitcher()

def serialize_message(m: Message) -> Dict[str, Any]:
    a2a = None
    if m.a2a_context:
        if isinstance(m.a2a_context, dict):
            a2a = m.a2a_context
        else:
            a2a = {
                "agent_handle": m.a2a_context.agent_handle,
                "target_handle": m.a2a_context.target_handle,
                "task_id": m.a2a_context.task_id
            }
    policy = None
    if m.permission_policy:
        if isinstance(m.permission_policy, dict):
            policy = m.permission_policy
        else:
            policy = {
                "whitelist_emails": m.permission_policy.whitelist_emails,
                "blacklist_emails": m.permission_policy.blacklist_emails,
                "whitelist_phones": m.permission_policy.whitelist_phones,
                "blacklist_phones": m.permission_policy.blacklist_phones
            }
    return {
        "message_id": m.message_id,
        "timestamp": m.timestamp,
        "channel": m.channel,
        "sender_email": m.sender_email,
        "sender_phone": m.sender_phone,
        "display_name": m.display_name,
        "text": m.text,
        "true_identity_id": m.true_identity_id,
        "contact_id": m.contact_id,
        "a2a_context": a2a,
        "permission_policy": policy
    }

def serialize_scenario(s: Scenario, s_type: str) -> Dict[str, Any]:
    policy = None
    if s.permission_policy:
        if isinstance(s.permission_policy, dict):
            policy = s.permission_policy
        else:
            policy = {
                "whitelist_emails": s.permission_policy.whitelist_emails,
                "blacklist_emails": s.permission_policy.blacklist_emails,
                "whitelist_phones": s.permission_policy.whitelist_phones,
                "blacklist_phones": s.permission_policy.blacklist_phones
            }
    return {
        "scenario_id": s.scenario_id,
        "title": s.title,
        "type": s_type,
        "ambiguity_type": s.ambiguity_type,
        "true_identities": [
            {
                "identity_id": ident.identity_id,
                "canonical_name": ident.canonical_name,
                "canonical_email": ident.canonical_email,
                "canonical_phone": ident.canonical_phone
            }
            for ident in s.true_identities
        ],
        "messages": [serialize_message(m) for m in s.messages],
        "permission_policy": policy
    }

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Web dashboard index.html not found.")
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "SameSame Stitching Engine",
        "strategies": ["composite", "exact", "fuzzy", "embedding", "contact", "permission", "a2a"]
    }

@app.get("/api/scenarios")
def list_scenarios():
    items = []
    if DEV_DIR.exists():
        for file in sorted(DEV_DIR.glob("*.yaml")):
            try:
                s = load_scenario_file(file)
                items.append({
                    "id": s.scenario_id,
                    "title": s.title,
                    "type": "dev",
                    "ambiguity_type": s.ambiguity_type,
                    "message_count": len(s.messages),
                    "identity_count": len(s.true_identities)
                })
            except Exception:
                continue
    if TEST_DIR.exists():
        for file in sorted(TEST_DIR.glob("*.yaml")):
            try:
                s = load_scenario_file(file)
                items.append({
                    "id": s.scenario_id,
                    "title": s.title,
                    "type": "test",
                    "ambiguity_type": s.ambiguity_type,
                    "message_count": len(s.messages),
                    "identity_count": len(s.true_identities)
                })
            except Exception:
                continue
    return items

@app.get("/api/scenarios/{scenario_type}/{scenario_id}")
def get_scenario(scenario_type: str, scenario_id: str):
    target_dir = DEV_DIR if scenario_type == "dev" else TEST_DIR
    target_file = target_dir / f"{scenario_id}.yaml"
    if not target_file.exists():
        matches = list(target_dir.glob(f"{scenario_id}.*"))
        if matches:
            target_file = matches[0]
        else:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found in {scenario_type}.")
    s = load_scenario_file(target_file)
    return serialize_scenario(s, scenario_type)

@app.post("/api/stitch")
def execute_stitch(req: StitchRequest):
    stitcher = get_stitcher_instance(req.strategy)
    msg_objs: List[Message] = []
    global_policy = None
    if req.permission_policy:
        global_policy = PermissionPolicy(
            whitelist_emails=list(req.permission_policy.whitelist_emails),
            blacklist_emails=list(req.permission_policy.blacklist_emails),
            whitelist_phones=list(req.permission_policy.whitelist_phones),
            blacklist_phones=list(req.permission_policy.blacklist_phones)
        )
    for p in req.messages:
        a2a_ctx = None
        if p.a2a_context:
            a2a_ctx = A2AContext(
                agent_handle=p.a2a_context.agent_handle or "",
                target_handle=p.a2a_context.target_handle or "",
                task_id=p.a2a_context.task_id or ""
            )
        msg_pol = global_policy
        if p.permission_policy:
            msg_pol = PermissionPolicy(
                whitelist_emails=list(p.permission_policy.whitelist_emails),
                blacklist_emails=list(p.permission_policy.blacklist_emails),
                whitelist_phones=list(p.permission_policy.whitelist_phones),
                blacklist_phones=list(p.permission_policy.blacklist_phones)
            )
        msg_objs.append(
            Message(
                message_id=p.message_id,
                timestamp=p.timestamp,
                channel=p.channel,
                sender_email=p.sender_email,
                sender_phone=p.sender_phone,
                display_name=p.display_name,
                text=p.text,
                true_identity_id=p.true_identity_id,
                contact_id=p.contact_id,
                a2a_context=a2a_ctx,
                permission_policy=msg_pol
            )
        )
    start_time = time.perf_counter()
    partition = stitcher.partition(msg_objs)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    unresolvable_ids = []
    if hasattr(stitcher, "get_unresolvable_message_ids"):
        unresolvable_ids = sorted(list(stitcher.get_unresolvable_message_ids(msg_objs)))
    msg_dict = {m.message_id: serialize_message(m) for m in msg_objs}
    cluster_results = []
    for idx, c in enumerate(partition):
        cluster_msgs = [msg_dict[mid] for mid in c if mid in msg_dict]
        names = [m["display_name"] for m in cluster_msgs if m.get("display_name")]
        emails = [m["sender_email"] for m in cluster_msgs if m.get("sender_email")]
        phones = [m["sender_phone"] for m in cluster_msgs if m.get("sender_phone")]
        contacts = [m["contact_id"] for m in cluster_msgs if m.get("contact_id")]
        channels = list({m["channel"] for m in cluster_msgs if m.get("channel")})
        canonical_name = names[0] if names else (contacts[0] if contacts else f"Identity Cluster #{idx + 1}")
        cluster_results.append({
            "cluster_id": idx + 1,
            "canonical_name": canonical_name,
            "message_ids": c,
            "message_count": len(c),
            "channels": channels,
            "inferred_emails": sorted(list(set(emails))),
            "inferred_phones": sorted(list(set(phones))),
            "inferred_contacts": sorted(list(set(contacts))),
            "messages": cluster_msgs
        })
    labeled_messages = [m for m in msg_objs if m.true_identity_id is not None]
    metrics = None
    if len(labeled_messages) >= 2:
        dummy_scenario = Scenario(
            scenario_id="runtime_evaluation",
            title="Runtime Scenario",
            ambiguity_type="runtime",
            true_identities=[],
            messages=msg_objs,
            permission_policy=global_policy
        )
        res = evaluate_scenario(dummy_scenario, stitcher)
        metrics = {
            "precision": round(res.precision, 4),
            "recall": round(res.recall, 4),
            "f1": round(res.f1, 4),
            "tp": res.true_positive_pairs,
            "fp": res.false_positive_pairs,
            "fn": res.false_negative_pairs,
            "tn": res.true_negative_pairs,
            "over_split_identities": res.over_split_identities,
            "over_splitting_rate": round(res.over_split_identities / res.total_true_identities, 4) if res.total_true_identities > 0 else 0.0,
            "over_merged_clusters": res.over_merged_clusters,
            "over_merging_rate": round(res.over_merged_clusters / res.total_predicted_clusters, 4) if res.total_predicted_clusters > 0 else 0.0,
            "stitching_inflation": round(res.stitching_inflation, 4),
            "contact_resolution_accuracy": round(res.contact_resolution_accuracy, 4),
            "permission_blocked_precision": round(res.permission_blocked_precision, 4),
            "a2a_recall": round(res.a2a_recall, 4)
        }
    return {
        "strategy": req.strategy,
        "elapsed_ms": elapsed_ms,
        "total_messages": len(msg_objs),
        "cluster_count": len(cluster_results),
        "unresolvable_ids": unresolvable_ids,
        "clusters": cluster_results,
        "metrics": metrics
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

