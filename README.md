Stitch: Cross-Channel Identity Stitching Evaluation Harness
============================================================

An empirical evaluation harness measuring how reliably cross-channel conversation threads
(email, SMS, voice transcripts) can be stitched across exact-match, fuzzy-match,
and sentence-embedding baselines against hand-labeled ground truth.

Research Question
-----------------
How accurately can identity stitching reconstruct true cross-channel conversation
threads, and how do exact-match, fuzzy-match, and embedding-based strategies
compare in precision, recall, and failure modes?

Dataset Architecture
--------------------
- 20 development scenarios (data/dev/)
- 10 held-out test scenarios (data/test/)
- Ambiguity distributions:
  - reused_phone: Shared landlines, family plans, recycled VoIP, dispatcher lines.
  - shared_domain: Corporate domain overlap across distinct colleagues.
  - name_only: Missing-metadata voice calls and SMS.
  - none: Clean positive control handoffs.
- Ground Truth Validation: Independent dual-pass annotation on 10 dev scenarios
  yielding Cohen's kappa = 0.8817 (exceeding the 0.80 validity threshold).

Headline Benchmark Results (Held-Out Test Set, n=10)
----------------------------------------------------
Total True Identities: 16
Total True Pairwise Links: 24

| Metric | Exact-Match Baseline | Fuzzy-Match Baseline | Embedding Matcher (all-MiniLM-L6-v2) |
| :--- | :---: | :---: | :---: |
| Precision | 73.91% (17/23) | 50.00% (20/40) | 100.00% (4/4) |
| Recall | 70.83% (17/24) | 83.33% (20/24) | 16.67% (4/24) |
| F1 Score | 0.7234 | 0.6250 | 0.2857 |
| Over-Splitting Rate | 31.25% (5/16) | 18.75% (3/16) | 87.50% (14/16) |
| Over-Merging Rate | 16.67% (3/18) | 46.15% (6/13) | 0.00% (0/32) |
| Stitching Inflation | +0.2000 | -0.1000 | +1.1000 |
| Dominant Failure Mode | name_only_oversplit | unknown_overmerge | name_only_oversplit |

Key Empirical Findings
----------------------
1. The Embedding Paradox: Sentence embeddings (all-MiniLM-L6-v2) achieve flawless precision (100.0%)
   and zero privacy leaks (0.0% over-merging), but suffer severe amnesia (16.67% recall, 87.50% over-splitting).
   Even on the positive control group (none), embeddings miss 66.7% of valid links due to vocabulary variance
   across channels.
2. The Privacy Penalty: Fuzzy matching maximizes recall (83.33%) but introduces severe privacy risks
   (46.15% over-merging rate, blending distinct humans into shared clusters).
3. The Pragmatic Baseline: Exact matching with text entity extraction achieves the highest overall
   F1 (0.7234), completely solving clean handoffs and corporate domain overlaps, while failing primarily
   on shared family and business phone lines.

Repository Structure
--------------------
- data/dev/: 20 development scenarios in YAML format.
- data/test/: 10 held-out test scenarios in YAML format.
- data/dev_second_pass.yaml: Independent dual-pass annotations for Cohen's Kappa scoring.
- stitch/models.py: Data models for Messages, Identities, and Scenarios.
- stitch/loader.py: YAML scenario loader.
- stitch/agreement.py: Pairwise Cohen's Kappa agreement calculator.
- stitch/strategies/base.py: Abstract stitcher interface and Union-Find graph clustering.
- stitch/strategies/exact.py: Exact-match baseline with header and body entity extraction.
- stitch/strategies/fuzzy.py: Fuzzy-match baseline (domain, area code, name matching).
- stitch/strategies/embedding.py: Sentence-transformers embedding matcher with identifier gating.
- stitch/evaluation.py: Evaluation metrics, inflation, over-split/over-merge rates, failure analyzer.
- run_eval.py: Evaluation runner script.
- tests/test_stitchers.py: Pytest test suite covering all matchers and metrics.

Running the Pipeline
--------------------
Run test suite:
python -m pytest tests

Run complete evaluation benchmark:
python run_eval.py
