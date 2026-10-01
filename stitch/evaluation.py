from typing import List, Dict, Set, Tuple, Any
from itertools import combinations
from dataclasses import dataclass, field
from stitch.models import Scenario, Message
from stitch.strategies.base import Stitcher

@dataclass
class ScenarioEvaluationResult:
    scenario_id: str
    ambiguity_type: str
    num_messages: int
    num_true_clusters: int
    num_predicted_clusters: int
    true_positive_pairs: int
    false_positive_pairs: int
    false_negative_pairs: int
    true_negative_pairs: int
    precision: float
    recall: float
    f1: float
    over_split_identities: int
    total_true_identities: int
    over_merged_clusters: int
    total_predicted_clusters: int
    stitching_inflation: float
    failure_cases: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AggregatedEvaluationResult:
    strategy_name: str
    num_scenarios: int
    precision: float
    recall: float
    f1: float
    over_splitting_rate: float
    over_merging_rate: float
    average_stitching_inflation: float
    by_ambiguity_type: Dict[str, Dict[str, float]]
    failure_mode_counts: Dict[str, int]
    dominant_failure_mode: str
    scenario_results: List[ScenarioEvaluationResult] = field(default_factory=list)

def evaluate_scenario(scenario: Scenario, stitcher: Stitcher) -> ScenarioEvaluationResult:
    messages = scenario.messages
    message_ids = [m.message_id for m in messages]
    predicted_clusters = stitcher.partition(messages)
    
    pred_map = Stitcher.clusters_to_map(predicted_clusters)
    true_map = {m.message_id: m.true_identity_id for m in messages if m.true_identity_id is not None}
    
    unique_true_ids = set(true_map.values())
    num_true_clusters = len(unique_true_ids)
    num_predicted_clusters = len(predicted_clusters)

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    failure_cases = []

    pairs = list(combinations(message_ids, 2))
    msg_dict = {m.message_id: m for m in messages}

    for m1_id, m2_id in pairs:
        m1 = msg_dict[m1_id]
        m2 = msg_dict[m2_id]
        t1 = true_map.get(m1_id)
        t2 = true_map.get(m2_id)
        p1 = pred_map.get(m1_id)
        p2 = pred_map.get(m2_id)

        same_true = (t1 is not None and t2 is not None and t1 == t2)
        same_pred = (p1 is not None and p2 is not None and p1 == p2)

        if same_true and same_pred:
            tp += 1
        elif not same_true and same_pred:
            fp += 1
            cause = "unknown_overmerge"
            if m1.sender_phone and m2.sender_phone and m1.sender_phone == m2.sender_phone:
                cause = "reused_phone_overmerge"
            elif m1.sender_email and m2.sender_email and "@" in m1.sender_email and "@" in m2.sender_email and m1.sender_email.split("@")[1] == m2.sender_email.split("@")[1]:
                cause = "shared_domain_overmerge"
            elif m1.display_name and m2.display_name and m1.display_name.lower() == m2.display_name.lower():
                cause = "name_collision_overmerge"
            failure_cases.append({
                "type": "false_positive",
                "cause": cause,
                "m1": m1_id,
                "m2": m2_id,
                "t1": t1,
                "t2": t2
            })
        elif same_true and not same_pred:
            fn += 1
            cause = "unknown_oversplit"
            if m1.channel != m2.channel:
                if not m1.sender_email or not m2.sender_email:
                    cause = "sparse_identifier_oversplit"
                if m1.channel == "voice" or m2.channel == "voice":
                    cause = "name_only_oversplit"
            else:
                cause = "content_dissimilarity_oversplit"
            failure_cases.append({
                "type": "false_negative",
                "cause": cause,
                "m1": m1_id,
                "m2": m2_id,
                "t1": t1,
                "t2": t2
            })
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if fp == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if fn == 0 else 0.0)
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    identity_to_pred_clusters: Dict[str, Set[str]] = {}
    for m_id, t_id in true_map.items():
        if t_id not in identity_to_pred_clusters:
            identity_to_pred_clusters[t_id] = set()
        identity_to_pred_clusters[t_id].add(pred_map[m_id])

    over_split_identities = sum(1 for c_set in identity_to_pred_clusters.values() if len(c_set) > 1)
    total_true_identities = len(unique_true_ids)

    over_merged_clusters = 0
    for cluster in predicted_clusters:
        true_ids_in_cluster = {true_map[m_id] for m_id in cluster if m_id in true_map}
        if len(true_ids_in_cluster) > 1:
            over_merged_clusters += 1
    total_predicted_clusters = len(predicted_clusters)

    stitching_inflation = (num_predicted_clusters - num_true_clusters) / num_true_clusters if num_true_clusters > 0 else 0.0

    return ScenarioEvaluationResult(
        scenario_id=scenario.scenario_id,
        ambiguity_type=scenario.ambiguity_type,
        num_messages=len(messages),
        num_true_clusters=num_true_clusters,
        num_predicted_clusters=num_predicted_clusters,
        true_positive_pairs=tp,
        false_positive_pairs=fp,
        false_negative_pairs=fn,
        true_negative_pairs=tn,
        precision=precision,
        recall=recall,
        f1=f1,
        over_split_identities=over_split_identities,
        total_true_identities=total_true_identities,
        over_merged_clusters=over_merged_clusters,
        total_predicted_clusters=total_predicted_clusters,
        stitching_inflation=stitching_inflation,
        failure_cases=failure_cases
    )

def evaluate_scenarios(
    scenarios: List[Scenario],
    stitcher: Stitcher,
    strategy_name: str
) -> AggregatedEvaluationResult:
    results: List[ScenarioEvaluationResult] = []
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    total_over_split = 0
    total_identities = 0
    total_over_merged = 0
    total_predicted_clusters = 0
    inflations = []

    by_ambiguity: Dict[str, Dict[str, Any]] = {}
    failure_mode_counts: Dict[str, int] = {}

    for s in scenarios:
        res = evaluate_scenario(s, stitcher)
        results.append(res)

        total_tp += res.true_positive_pairs
        total_fp += res.false_positive_pairs
        total_fn += res.false_negative_pairs
        total_tn += res.true_negative_pairs

        total_over_split += res.over_split_identities
        total_identities += res.total_true_identities

        total_over_merged += res.over_merged_clusters
        total_predicted_clusters += res.total_predicted_clusters

        inflations.append(res.stitching_inflation)

        amb = res.ambiguity_type
        if amb not in by_ambiguity:
            by_ambiguity[amb] = {"tp": 0, "fp": 0, "fn": 0, "inflations": []}
        by_ambiguity[amb]["tp"] += res.true_positive_pairs
        by_ambiguity[amb]["fp"] += res.false_positive_pairs
        by_ambiguity[amb]["fn"] += res.false_negative_pairs
        by_ambiguity[amb]["inflations"].append(res.stitching_inflation)

        for fc in res.failure_cases:
            cause = fc["cause"]
            failure_mode_counts[cause] = failure_mode_counts.get(cause, 0) + 1

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else (1.0 if total_fp == 0 else 0.0)
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else (1.0 if total_fn == 0 else 0.0)
    overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0

    over_splitting_rate = total_over_split / total_identities if total_identities > 0 else 0.0
    over_merging_rate = total_over_merged / total_predicted_clusters if total_predicted_clusters > 0 else 0.0
    avg_inflation = sum(inflations) / len(inflations) if inflations else 0.0

    ambiguity_breakdown: Dict[str, Dict[str, float]] = {}
    for amb, stats in by_ambiguity.items():
        p_tp = stats["tp"]
        p_fp = stats["fp"]
        p_fn = stats["fn"]
        p_prec = p_tp / (p_tp + p_fp) if (p_tp + p_fp) > 0 else (1.0 if p_fp == 0 else 0.0)
        p_rec = p_tp / (p_tp + p_fn) if (p_tp + p_fn) > 0 else (1.0 if p_fn == 0 else 0.0)
        p_f1 = (2 * p_prec * p_rec) / (p_prec + p_rec) if (p_prec + p_rec) > 0 else 0.0
        ambiguity_breakdown[amb] = {
            "precision": p_prec,
            "recall": p_rec,
            "f1": p_f1,
            "avg_inflation": sum(stats["inflations"]) / len(stats["inflations"]) if stats["inflations"] else 0.0
        }

    dominant_failure = max(failure_mode_counts.items(), key=lambda x: x[1])[0] if failure_mode_counts else "none"

    return AggregatedEvaluationResult(
        strategy_name=strategy_name,
        num_scenarios=len(scenarios),
        precision=overall_precision,
        recall=overall_recall,
        f1=overall_f1,
        over_splitting_rate=over_splitting_rate,
        over_merging_rate=over_merging_rate,
        average_stitching_inflation=avg_inflation,
        by_ambiguity_type=ambiguity_breakdown,
        failure_mode_counts=failure_mode_counts,
        dominant_failure_mode=dominant_failure,
        scenario_results=results
    )
