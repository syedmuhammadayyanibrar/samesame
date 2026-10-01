import sys
import yaml
from pathlib import Path
from stitch.loader import load_scenarios_from_directory
from stitch.agreement import compute_dataset_kappa
from stitch.strategies.exact import ExactMatchStitcher
from stitch.strategies.fuzzy import FuzzyMatchStitcher
from stitch.strategies.embedding import EmbeddingMatchStitcher
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
    print("-" * 60)
    print(f"STRATEGY: {res.strategy_name} on {dataset_label} ({res.num_scenarios} scenarios)")
    print("-" * 60)
    print(f"Precision:                   {res.precision:.4f}")
    print(f"Recall:                      {res.recall:.4f}")
    print(f"F1 Score:                    {res.f1:.4f}")
    print(f"Over-Splitting Rate:         {res.over_splitting_rate * 100:.2f}%")
    print(f"Over-Merging Rate:           {res.over_merging_rate * 100:.2f}%")
    print(f"Average Stitching Inflation: {res.average_stitching_inflation:+.4f}")
    print(f"Dominant Failure Mode:       {res.dominant_failure_mode}")
    print("Failure Mode Breakdown:")
    for mode, count in res.failure_mode_counts.items():
        print(f"  {mode}: {count}")
    print("Breakdown By Ambiguity Type:")
    for amb, stats in res.by_ambiguity_type.items():
        print(f"  [{amb}] Prec: {stats['precision']:.2f} | Rec: {stats['recall']:.2f} | F1: {stats['f1']:.2f} | Inflation: {stats['avg_inflation']:+.2f}")
    print()

def main():
    overall_kappa, flagged = run_annotator_agreement_check()

    dev_scenarios = load_scenarios_from_directory("data/dev")
    test_scenarios = load_scenarios_from_directory("data/test")

    strategies = [
        ("Exact Match Baseline", ExactMatchStitcher()),
        ("Fuzzy Match Baseline", FuzzyMatchStitcher()),
        ("Embedding Matcher (all-MiniLM-L6-v2)", EmbeddingMatchStitcher(similarity_threshold=0.60))
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
