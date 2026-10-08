import pytest
from stitch.models import Message, Identity, Scenario, A2AContext, PermissionPolicy, ContactMemory
from stitch.strategies.exact import (
    ExactMatchStitcher,
    normalize_phone,
    normalize_email,
    extract_emails_from_text,
    extract_phones_from_text,
    get_message_emails,
    get_message_phones
)
from stitch.strategies.fuzzy import (
    FuzzyMatchStitcher,
    extract_domain,
    extract_area_code,
    normalize_name,
    names_partially_match,
    extract_self_identified_name
)
from stitch.strategies.embedding import EmbeddingMatchStitcher
from stitch.strategies.permission import PermissionAwareStitcher
from stitch.strategies.contact import ContactResolutionStitcher
from stitch.strategies.a2a import A2AStitcher
from stitch.strategies.memory import MemoryStitcher
from stitch.strategies.composite import CompositeStitcher
from stitch.agreement import compute_dataset_kappa, extract_pairwise_links
from stitch.evaluation import evaluate_scenario, evaluate_scenarios

def test_normalization():
    assert normalize_phone("+1 (555) 019-2831") == "15550192831"
    assert normalize_phone("123") is None
    assert normalize_phone(None) is None
    assert normalize_email("  USER@Domain.COM ") == "user@domain.com"
    assert normalize_email("nodomain") is None
    assert normalize_email(None) is None

def test_body_extraction():
    text = "Please reach me at user@test.com or call 206-555-0401 today."
    emails = extract_emails_from_text(text)
    phones = extract_phones_from_text(text)
    assert "user@test.com" in emails
    assert "12065550401" in phones

    msg = Message("m1", "2026-10-01T10:00:00Z", "sms", None, None, None, text)
    assert "user@test.com" in get_message_emails(msg)
    assert "12065550401" in get_message_phones(msg)

def test_fuzzy_helpers():
    assert extract_domain("alice@company.org") == "company.org"
    assert extract_area_code("+14155550192") == "415"
    assert extract_area_code("4155550192") == "415"
    assert names_partially_match("John Smith", "John") is True
    assert names_partially_match("Alice Vance", "Bob Vance") is False
    assert extract_self_identified_name("Hello, this is Sarah speaking") == "Sarah"

def test_exact_match_partition():
    stitcher = ExactMatchStitcher()
    m1 = Message("m1", "2026-10-01T10:00:00Z", "email", "alice@test.com", None, "Alice", "Hello")
    m2 = Message("m2", "2026-10-01T10:05:00Z", "sms", None, "+15550100", "Alice", "Hi, my email is alice@test.com")
    m3 = Message("m3", "2026-10-01T10:10:00Z", "email", "alice@test.com", None, "Alice", "Followup")
    m4 = Message("m4", "2026-10-01T10:15:00Z", "voice", None, None, None, "Voice note without identifiers")

    clusters = stitcher.partition([m1, m2, m3, m4])
    cluster_map = stitcher.clusters_to_map(clusters)

    assert cluster_map["m1"] == cluster_map["m2"]
    assert cluster_map["m1"] == cluster_map["m3"]
    assert cluster_map["m4"] != cluster_map["m1"]

def test_fuzzy_match_partition():
    stitcher = FuzzyMatchStitcher()
    m1 = Message("m1", "2026-10-01T10:00:00Z", "email", "alice@company.com", None, "Alice Vance", "Billing question")
    m2 = Message("m2", "2026-10-01T10:05:00Z", "email", "bob@company.com", None, "Bob Vance", "Shipping question")
    m3 = Message("m3", "2026-10-01T10:10:00Z", "voice", None, None, None, "This is Alice calling about billing")

    clusters = stitcher.partition([m1, m2, m3])
    cluster_map = stitcher.clusters_to_map(clusters)

    assert cluster_map["m1"] == cluster_map["m2"]
    assert cluster_map["m1"] == cluster_map["m3"]

def test_embedding_match_partition():
    stitcher = EmbeddingMatchStitcher(similarity_threshold=0.55)
    m1 = Message("m1", "2026-10-01T10:00:00Z", "email", "user@company.com", None, "Alice", "I need to return my defective laptop charger.")
    m2 = Message("m2", "2026-10-01T10:05:00Z", "sms", None, None, "Alice", "Following up on returning the broken charger for laptop.")
    m3 = Message("m3", "2026-10-01T10:10:00Z", "email", "other@company.com", None, "Bob", "Inquiring about enterprise tax compliance guidelines.")

    clusters = stitcher.partition([m1, m2, m3])
    cluster_map = stitcher.clusters_to_map(clusters)

    assert cluster_map["m1"] == cluster_map["m2"]
    assert cluster_map["m1"] != cluster_map["m3"]

def test_pairwise_kappa():
    scenario = Scenario(
        scenario_id="s1",
        title="Test Scenario",
        ambiguity_type="none",
        true_identities=[Identity("u1", "User 1"), Identity("u2", "User 2")],
        messages=[
            Message("m1", "2026-10-01T10:00:00Z", "email", "u1@a.com", None, "U1", "Text 1", "u1"),
            Message("m2", "2026-10-01T10:05:00Z", "email", "u1@a.com", None, "U1", "Text 2", "u1"),
            Message("m3", "2026-10-01T10:10:00Z", "email", "u2@a.com", None, "U2", "Text 3", "u2"),
            Message("m4", "2026-10-01T10:15:00Z", "email", "u2@a.com", None, "U2", "Text 4", "u2"),
        ]
    )
    second_pass = {
        "s1": {"m1": "u1", "m2": "u1", "m3": "u2", "m4": "u2"}
    }
    kappa, per_s, flagged = compute_dataset_kappa([scenario], second_pass)
    assert kappa == 1.0
    assert len(flagged) == 0

def test_evaluation_metrics():
    scenario = Scenario(
        scenario_id="s1",
        title="Metric Test",
        ambiguity_type="reused_phone",
        true_identities=[Identity("u1", "U1"), Identity("u2", "U2")],
        messages=[
            Message("m1", "2026-10-01T10:00:00Z", "sms", None, "+15550100", "Mark", "Text 1", "u1"),
            Message("m2", "2026-10-01T10:05:00Z", "voice", None, "+15550100", "Sarah", "Text 2", "u2")
        ]
    )
    stitcher = ExactMatchStitcher()
    res = evaluate_scenario(scenario, stitcher)

    assert res.true_positive_pairs == 0
    assert res.false_positive_pairs == 1
    assert res.false_negative_pairs == 0
    assert res.precision == 0.0
    assert res.over_merged_clusters == 1
    assert res.stitching_inflation == -0.5

def test_permission_aware_stitcher():
    policy = PermissionPolicy(
        whitelist_emails=["alice@whitelist.com"],
        blacklist_emails=["blocked@bad.com"],
        whitelist_phones=["+15550101"],
        blacklist_phones=["+15550666"]
    )
    m1 = Message("m1", "2026-10-08T10:00:00Z", "email", "alice@whitelist.com", None, "Alice", "Hello", permission_policy=policy)
    m2 = Message("m2", "2026-10-08T10:05:00Z", "sms", None, "+15550101", None, "Hi", permission_policy=policy)
    m3 = Message("m3", "2026-10-08T10:10:00Z", "sms", None, "+15550666", None, "Spam", permission_policy=policy)
    m4 = Message("m4", "2026-10-08T10:15:00Z", "email", "blocked@bad.com", None, None, "Fraud", permission_policy=policy)

    stitcher = PermissionAwareStitcher(ExactMatchStitcher())
    unres = stitcher.get_unresolvable_message_ids([m1, m2, m3, m4])
    assert "m3" in unres
    assert "m4" in unres
    assert "m1" not in unres
    assert "m2" not in unres

    clusters = stitcher.partition([m1, m2, m3, m4])
    c_map = stitcher.clusters_to_map(clusters)
    assert c_map["m1"] == c_map["m2"]
    assert c_map["m3"] != c_map["m1"]
    assert c_map["m4"] != c_map["m1"]
    assert c_map["m3"] != c_map["m4"]

def test_contact_resolution_stitcher():
    m1 = Message("m1", "2026-10-08T10:00:00Z", "voice", None, None, None, "Voice note", contact_id="c_samuel")
    m2 = Message("m2", "2026-10-08T10:05:00Z", "email", "samuel@work.com", None, "Samuel", "Email", contact_id="c_samuel")
    m3 = Message("m3", "2026-10-08T10:10:00Z", "voice", None, None, None, "Voice 2", contact_id="c_diana")
    m4 = Message("m4", "2026-10-08T10:15:00Z", "sms", None, "+15550300", None, "Reach me at samuel@work.com")

    stitcher = ContactResolutionStitcher(ExactMatchStitcher())
    clusters = stitcher.partition([m1, m2, m3, m4])
    c_map = stitcher.clusters_to_map(clusters)

    assert c_map["m1"] == c_map["m2"]
    assert c_map["m4"] == c_map["m1"]
    assert c_map["m3"] != c_map["m1"]

    m5 = Message("m5", "2026-10-08T10:00:00Z", "sms", None, "+15550999", None, "Call 1", contact_id="c_1")
    m6 = Message("m6", "2026-10-08T10:05:00Z", "sms", None, "+15550999", None, "Call 2", contact_id="c_2")
    split_clusters = stitcher.partition([m5, m6])
    split_map = stitcher.clusters_to_map(split_clusters)
    assert split_map["m5"] != split_map["m6"]

def test_a2a_stitcher():
    ctx1 = A2AContext(agent_handle="bot_a", target_handle="bot_b", task_id="task_99")
    ctx2 = A2AContext(agent_handle="bot_b", target_handle="bot_a", task_id="task_99")
    ctx3 = A2AContext(agent_handle="bot_x", target_handle="bot_y", task_id="task_88")
    m1 = Message("m1", "2026-10-08T10:00:00Z", "voice", None, None, None, "Msg 1", a2a_context=ctx1)
    m2 = Message("m2", "2026-10-08T10:05:00Z", "sms", None, None, None, "Msg 2", a2a_context=ctx2)
    m3 = Message("m3", "2026-10-08T10:10:00Z", "sms", None, None, None, "Msg 3", a2a_context=ctx3)
    m4 = Message("m4", "2026-10-08T10:15:00Z", "email", None, None, None, "Msg 4")

    stitcher = A2AStitcher()
    clusters = stitcher.partition([m1, m2, m3, m4])
    c_map = stitcher.clusters_to_map(clusters)

    assert c_map["m1"] == c_map["m2"]
    assert c_map["m3"] != c_map["m1"]
    assert c_map["m4"] != c_map["m1"]

def test_composite_stitcher_layering():
    policy = PermissionPolicy(
        whitelist_emails=[],
        blacklist_emails=["spammer@evil.com"],
        whitelist_phones=[],
        blacklist_phones=[]
    )
    ctx_agent = A2AContext(agent_handle="alpha", target_handle="beta", task_id="task_123")
    ctx_agent_recip = A2AContext(agent_handle="beta", target_handle="alpha", task_id="task_123")

    m1 = Message("m1", "2026-10-08T10:00:00Z", "voice", None, None, None, "Voice note", contact_id="cont_a")
    m2 = Message("m2", "2026-10-08T10:05:00Z", "email", "alice@co.com", None, "Alice", "Email note", contact_id="cont_a")
    m3 = Message("m3", "2026-10-08T10:10:00Z", "sms", None, None, None, "Agent sync", a2a_context=ctx_agent)
    m4 = Message("m4", "2026-10-08T10:15:00Z", "sms", None, None, None, "Agent ack", a2a_context=ctx_agent_recip)
    m5 = Message("m5", "2026-10-08T10:20:00Z", "email", "spammer@evil.com", None, None, "Bad spam", permission_policy=policy)

    composite = CompositeStitcher(fallback_stitcher=ExactMatchStitcher())
    clusters = composite.stitch([m1, m2, m3, m4, m5])
    c_map = composite.clusters_to_map(clusters)

    assert c_map["m1"] == c_map["m2"]
    assert c_map["m3"] == c_map["m4"]
    assert c_map["m5"] != c_map["m1"]
    assert c_map["m5"] != c_map["m3"]

def test_composite_stitcher_baseline_equivalence():
    m1 = Message("m1", "2026-10-01T10:00:00Z", "email", "alice@test.com", None, "Alice", "Hello")
    m2 = Message("m2", "2026-10-01T10:05:00Z", "sms", None, "+15550100", "Alice", "Hi, reach me at alice@test.com")
    m3 = Message("m3", "2026-10-01T10:10:00Z", "email", "alice@test.com", None, "Alice", "Followup")
    m4 = Message("m4", "2026-10-01T10:15:00Z", "voice", None, "+15550299", None, "Different person entirely")

    messages = [m1, m2, m3, m4]
    exact = ExactMatchStitcher()
    composite = CompositeStitcher(fallback_stitcher=exact)

    exact_clusters = exact.partition(messages)
    comp_clusters = composite.partition(messages)

    exact_sets = [frozenset(c) for c in exact_clusters]
    comp_sets = [frozenset(c) for c in comp_clusters]

    assert set(exact_sets) == set(comp_sets)

def test_memory_stitcher():
    mem = ContactMemory(
        memory_id="mem_1",
        contact_id="cont_vip",
        text="Customer VIP order replacement for gold watch model 884.",
        citations=["gold watch", "vip_customer@luxury.com"]
    )
    m1 = Message("m1", "2026-10-08T10:00:00Z", "email", "vip_customer@luxury.com", None, "VIP", "Inquiry about gold watch replacement.")
    m2 = Message("m2", "2026-10-08T10:05:00Z", "voice", None, None, None, "Calling regarding my order replacement for the gold watch.")
    m3 = Message("m3", "2026-10-08T10:10:00Z", "sms", None, None, None, "Unrelated question about office parking hours.")

    stitcher = MemoryStitcher(memories=[mem], similarity_threshold=0.50, enabled=True)
    clusters = stitcher.partition([m1, m2, m3])
    c_map = stitcher.clusters_to_map(clusters)

    assert c_map["m1"] == c_map["m2"]
    assert c_map["m3"] != c_map["m1"]
