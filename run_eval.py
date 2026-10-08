import sys
import yaml
from pathlib import Path
from stitch.loader import load_scenarios_from_directory
from stitch.agreement import compute_dataset_kappa
from stitch.strategies.exact import ExactMatchStitcher
from stitch.strategies.fuzzy import FuzzyMatchStitcher
from stitch.strategies.embedding import EmbeddingMatchStitcher
from stitch.strategies.composite import CompositeStitcher
from stitch.evaluation import evaluate_scenarios, AggregatedEvaluationResult

def run_annotator_agreement_check():
    dev_scenarios = load_scenarios_from_directory("data/dev")
    with open("data/dev_second_pass.yaml", "r", encoding="utf-8") as f:
        second_pass_data = yaml.safe_load(f)

    overall_kappa, per_scenario_kappa, flagged = compute_dataset_kappa(
        dev_scenarios,
        second_pass_data
    )

    print("=" * 60)
    print("PHASE 1: INTER-ANNOTATOR AGREEMENT (COHEN'S KAPPA)")
    print("=" * 60)
    print(f"Overall Pairwise Cohen's Kappa: {overall_kappa:.4f}")
    print("Per-Scenario Kappa Breakdown:")
    for s_id, k in per_scenario_kappa.items():
        print(f"  {s_id}: {k:.4f}")

    if overall_kappa < 0.70:
        print("[CRITICAL ERROR] Overall Kappa < 0.70. Ground truth is unreliable.")
        sys.exit(1)
    elif overall_kappa < 0.80 or flagged:
        print(f"[WARNING] Disputed scenarios flagged (< 0.80): {flagged}")
    else:
        print("[OK] Agreement is high (Kappa >= 0.80). Ground truth is validated.")
    print()
    return overall_kappa, flagged

def print_evaluation_summary(res: AggregatedEvaluationResult, dataset_label: str):
    pred_pairs = res.total_tp + res.total_fp
    true_pairs = res.total_tp + res.total_fn

    print("-" * 60)
    print(f"STRATEGY: {res.strategy_name} on {dataset_label} ({res.num_scenarios} scenarios)")
    print("-" * 60)
    print(f"Precision:                   {res.precision * 100:.2f}% ({res.total_tp}/{pred_pairs})")
    print(f"Recall:                      {res.recall * 100:.2f}% ({res.total_tp}/{true_pairs})")
    print(f"F1 Score:                    {res.f1:.4f}")
    print(f"Over-Splitting Rate:         {res.over_splitting_rate * 100:.2f}% ({res.total_over_split}/{res.total_identities} identities)")
    print(f"Over-Merging Rate:           {res.over_merging_rate * 100:.2f}% ({res.total_over_merged}/{res.total_predicted_clusters} clusters)")
    print(f"Average Stitching Inflation: {res.average_stitching_inflation:+.4f}")
    print(f"Contact Resolution Accuracy: {res.contact_resolution_accuracy * 100:.2f}%")
    print(f"Permission Block Precision:  {res.permission_blocked_precision * 100:.2f}%")
    print(f"A2A Recall:                  {res.a2a_recall * 100:.2f}%")
    print(f"Dominant Failure Mode:       {res.dominant_failure_mode}")
    print("Failure Mode Breakdown:")
    for mode, count in res.failure_mode_counts.items():
        print(f"  {mode}: {count}")
    print("Breakdown By Ambiguity Type:")
    for amb, stats in res.by_ambiguity_type.items():
        a_pred = stats['tp'] + stats['fp']
        a_true = stats['tp'] + stats['fn']
        print(f"  [{amb}] Prec: {stats['precision'] * 100:.1f}% ({stats['tp']}/{a_pred}) | Rec: {stats['recall'] * 100:.1f}% ({stats['tp']}/{a_true}) | F1: {stats['f1']:.2f} | Inflation: {stats['avg_inflation']:+.2f}")
    print()

def main():
    overall_kappa, flagged = run_annotator_agreement_check()

    dev_scenarios = load_scenarios_from_directory("data/dev")
    test_scenarios = load_scenarios_from_directory("data/test")

    strategies = [
        ("Exact Match Baseline", ExactMatchStitcher()),
        ("Fuzzy Match Baseline", FuzzyMatchStitcher()),
        ("Embedding Matcher (all-MiniLM-L6-v2)", EmbeddingMatchStitcher(similarity_threshold=0.60)),
        ("Composite Layered Stitcher", CompositeStitcher())
    ]

    print("=" * 60)
    print("PHASE 2 & 3: EVALUATION ON DEV SET (DEBUGGING / CALIBRATION)")
    print("=" * 60)
    for name, stitcher in strategies:
        res = evaluate_scenarios(dev_scenarios, stitcher, name)
        print_evaluation_summary(res, "DEV SET")

    print("=" * 60)
    print("PHASE 3: HEADLINE EVALUATION ON HELD-OUT TEST SET (NEVER TOUCHED IN DEBUGGING)")
    print("=" * 60)
    test_results = []
    for name, stitcher in strategies:
        res = evaluate_scenarios(test_scenarios, stitcher, name)
        test_results.append(res)
        print_evaluation_summary(res, "HELD-OUT TEST SET")

if __name__ == "__main__":
    main()
