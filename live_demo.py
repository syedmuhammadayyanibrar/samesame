import sys
import time
from typing import List, Dict, Set
from stitch.models import Message, A2AContext, PermissionPolicy
from stitch.strategies.composite import CompositeStitcher
from stitch.strategies.exact import ExactMatchStitcher

def render_live_event(step: int, msg: Message, clusters: List[Set[str]], unresolvable: Set[str]):
    print("=" * 70)
    print(f"EVENT #{step} | INCOMING MESSAGE [{msg.channel.upper()}]")
    print("=" * 70)
    print(f"Message ID:   {msg.message_id}")
    print(f"Timestamp:    {msg.timestamp}")
    print(f"Channel:      {msg.channel}")
    print(f"Sender Email: {msg.sender_email or 'None'}")
    print(f"Sender Phone: {msg.sender_phone or 'None'}")
    print(f"Display Name: {msg.display_name or 'None'}")
    print(f"Contact ID:   {msg.contact_id or 'None'}")
    if msg.a2a_context:
        print(f"A2A Context:  task={msg.a2a_context.task_id}, agent={msg.a2a_context.agent_handle} -> {msg.a2a_context.target_handle}")
    if msg.permission_policy:
        print(f"Permission:   has policy")
    print(f"Content:      \"{msg.text}\"")
    print("-" * 70)

    assigned_cluster_id = None
    for idx, c in enumerate(clusters):
        if msg.message_id in c:
            assigned_cluster_id = f"Identity-Cluster-{idx + 1}"
            break

    if msg.message_id in unresolvable:
        print(f">> STITCH DECISION: [QUARANTINED] Message matches permission blacklist.")
        print(f">> ACTION: Isolated into separate unresolvable bucket ({assigned_cluster_id}).")
    elif msg.contact_id:
        print(f">> STITCH DECISION: [CONTACT ANCHOR] Resolved via contact_id '{msg.contact_id}'.")
        print(f">> ACTION: Linked to {assigned_cluster_id}.")
    elif msg.a2a_context:
        print(f">> STITCH DECISION: [A2A TASK] Resolved via task_id '{msg.a2a_context.task_id}'.")
        print(f">> ACTION: Linked to {assigned_cluster_id}.")
    else:
        print(f">> STITCH DECISION: [IDENTIFIER MATCH] Resolved via exact matching.")
        print(f">> ACTION: Linked to {assigned_cluster_id}.")

    print()
    print("CURRENT LIVE IDENTITY STATE:")
    for idx, c in enumerate(clusters):
        m_list = sorted(list(c))
        is_quarantined = any(m_id in unresolvable for m_id in c)
        tag = " [BLOCKED/QUARANTINE]" if is_quarantined else ""
        print(f"  * Identity-Cluster-{idx + 1}{tag}: {m_list}")
    print()

def run_live_stream():
    policy = PermissionPolicy(
        whitelist_emails=["alice@acme.com"],
        blacklist_emails=["bad.actor@phishing.net"],
        whitelist_phones=["+14155550201"],
        blacklist_phones=["+15550666"]
    )

    incoming_stream = [
        Message(
            message_id="msg_01",
            timestamp="2026-10-08T10:00:00Z",
            channel="email",
            sender_email="alice@acme.com",
            sender_phone=None,
            display_name="Alice Vance",
            text="Hi support, need help updating our Q4 enterprise fleet proposal. Reach me at +14155550201.",
            contact_id="cont_alice_99",
            permission_policy=policy
        ),
        Message(
            message_id="msg_02",
            timestamp="2026-10-08T10:05:00Z",
            channel="sms",
            sender_email=None,
            sender_phone="+14155550201",
            display_name=None,
            text="Alice Vance here following up via SMS on the proposal updates.",
            contact_id=None,
            permission_policy=policy
        ),
        Message(
            message_id="msg_03",
            timestamp="2026-10-08T10:10:00Z",
            channel="voice",
            sender_email=None,
            sender_phone=None,
            display_name=None,
            text="Hey, Alice calling regarding our proposal meeting tomorrow. Account email is alice@acme.com.",
            contact_id="cont_alice_99",
            permission_policy=policy
        ),
        Message(
            message_id="msg_04",
            timestamp="2026-10-08T10:15:00Z",
            channel="voice",
            sender_email=None,
            sender_phone=None,
            display_name=None,
            text="Autonomous dispatch agent running fleet scheduling task 8801.",
            a2a_context=A2AContext(agent_handle="fleet_bot", target_handle="dispatcher_bot", task_id="task_8801"),
            permission_policy=policy
        ),
        Message(
            message_id="msg_05",
            timestamp="2026-10-08T10:18:00Z",
            channel="sms",
            sender_email=None,
            sender_phone=None,
            display_name=None,
            text="Dispatcher bot acknowledging fleet scheduling task 8801.",
            a2a_context=A2AContext(agent_handle="dispatcher_bot", target_handle="fleet_bot", task_id="task_8801"),
            permission_policy=policy
        ),
        Message(
            message_id="msg_06",
            timestamp="2026-10-08T10:25:00Z",
            channel="sms",
            sender_email=None,
            sender_phone="+15550666",
            display_name=None,
            text="URGENT: Click here to claim your wire refund prize immediately.",
            permission_policy=policy
        )
    ]

    stitcher = CompositeStitcher(fallback_stitcher=ExactMatchStitcher())
    active_messages: List[Message] = []

    print("=" * 70)
    print("STARTING LIVE CROSS-CHANNEL IDENTITY STITCHING STREAM")
    print("System: SameSame / Stitch v2.0 (Inkbox-aligned Composite Engine)")
    print("=" * 70)
    print()

    for step, msg in enumerate(incoming_stream, start=1):
        active_messages.append(msg)
        clusters = stitcher.stitch(active_messages)
        unresolvable = stitcher.get_unresolvable_message_ids(active_messages)
        render_live_event(step, msg, clusters, unresolvable)

    print("=" * 70)
    print("LIVE STREAM COMPLETED: FINAL IDENTITY PARTITION SUMMARY")
    print("=" * 70)
    final_clusters = stitcher.stitch(active_messages)
    final_unres = stitcher.get_unresolvable_message_ids(active_messages)
    for idx, c in enumerate(final_clusters):
        is_quarantined = any(m_id in final_unres for m_id in c)
        tag = " [QUARANTINED BLACKLIST]" if is_quarantined else " [VERIFIED HUMAN/AGENT IDENTITY]"
        print(f"Cluster #{idx + 1}{tag}:")
        for m_id in sorted(list(c)):
            m = next(item for item in active_messages if item.message_id == m_id)
            print(f"  - [{m.channel.upper()}] {m.message_id}: {m.text[:60]}...")
    print()

if __name__ == "__main__":
    run_live_stream()
