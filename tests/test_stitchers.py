import pytest
from stitch.models import Message, Identity, Scenario
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
