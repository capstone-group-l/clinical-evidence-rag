import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_retrieval import RUNS_DIR, load_questions

HIT_TARGET = 0.8
PRECISION_TARGET = 0.5
# z for a two-sided 95% interval
Z_95 = 1.96
# hit@k and precision@k intervals are shown with three significant figures
CI_FORMAT = "#.3g"


def load_gold():
    # Only answerable questions are scored
    gold = {}
    for question in load_questions():
        if question["answerable"] and question["relevant_chunk_ids"]:
            gold[question["id"]] = set(question["relevant_chunk_ids"])
    return gold


def score_question(chunk_ids, relevant, k):
    top_k = chunk_ids[:k]
    hits = len(set(top_k) & relevant)
    precision = hits / k
    # hit@k: 1 if at least one relevant chunk appears in the top k
    hit = 1.0 if hits > 0 else 0.0
    return hits, precision, hit


def score_run(run_file, gold, k):
    results = json.loads(run_file.read_text(encoding="utf-8"))
    rows = []
    for result in results:
        if result["id"] not in gold:
            continue
        relevant = gold[result["id"]]
        hits, precision, hit = score_question(result["chunk_ids"], relevant, k)
        rows.append((result["id"], hits, len(relevant), precision, hit))

    if not rows:
        return None, rows

    # One row per question, columns: hit, precision
    scores = np.array([(row[4], row[3]) for row in rows], dtype=float)
    means = scores.mean(axis=0)
    # Sample standard deviation
    standard_deviation = (
        scores.std(axis=0, ddof=1)
        if len(scores) > 1
        else np.zeros(scores.shape[1])
    )

    # 95% CI normal approximation
    n = len(scores)
    half_widths = Z_95 * standard_deviation / np.sqrt(n)
    lows = means - half_widths
    highs = means + half_widths
    # hit@k is 0/1 proportion so we decided to use Wilson
    # This is better for proportions near 0 or 1.
    lows[0], highs[0] = wilson_interval(means[0], n)
    cis = np.clip(np.stack([lows, highs], axis=1), 0.0, 1.0)
    return (means, standard_deviation, cis), rows


def wilson_interval(p, n, z=Z_95):
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return center - half, center + half


def metric_cell(mean, ci, sd, ci_format=".2f"):
    return (
        f"{mean:>7.3f} [{ci[0]:{ci_format}}, {ci[1]:{ci_format}}] ({sd:.2f})"
    )


def mark(value, target):
    if value >= target:
        return "^"
    return "x"


def main():
    parser = argparse.ArgumentParser(description="Score saved retrieval runs.")
    parser.add_argument(
        "setup",
        nargs="?",
        help="highlight this setup (all setups are always scored)",
    )
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument(
        "--per-question", action="store_true", help="print hits per question"
    )
    parser.add_argument(
        "--times", action="store_true", help="only print retrieval times"
    )
    args = parser.parse_args()
    k = args.k

    if args.times:
        print_times(sorted(RUNS_DIR.glob("*.json")))
        return

    gold = load_gold()

    if args.setup and not (RUNS_DIR / f"{args.setup}.json").exists():
        print(f"No run file found: {RUNS_DIR / f'{args.setup}.json'}")
        sys.exit(1)
    run_files = sorted(RUNS_DIR.glob("*.json"))

    print(
        f"Targets: hit@{k} >= {HIT_TARGET}, "
        f"precision@{k} >= {PRECISION_TARGET}"
    )
    print()

    print(
        "Each metric: mean [95% CI] (sd); "
        "CI uses Wilson for hit@k, mean +/- 1.96*SE otherwise"
    )
    print()

    header = (
        f"{'setup':<22}{'hit@' + str(k):>29}  {'precision@' + str(k):>29}  "
    )
    print(header)
    print("-" * len(header))

    for run_file in run_files:
        summary, rows = score_run(run_file, gold, k)
        if summary is None:
            print(f"{run_file.stem:<22}  (no answerable questions found)")
            continue

        means, standard_deviation, cis = summary
        hit_rate, precision = means
        hit_cell = metric_cell(
            hit_rate, cis[0], standard_deviation[0], CI_FORMAT
        )
        precision_cell = metric_cell(
            precision, cis[1], standard_deviation[1], CI_FORMAT
        )
        print(
            f"{run_file.stem:<22}"
            f"{hit_cell:>29} {mark(hit_rate, HIT_TARGET)}"
            f"{precision_cell:>29} {mark(precision, PRECISION_TARGET)}"
            f"{'  <-' if run_file.stem == args.setup else ''}"
        )

        if args.per_question:
            for question_id, hits, total, q_precision, q_hit in rows:
                print(
                    f"    {question_id}  hits {hits}/{total}"
                    f"  precision {q_precision:.2f}"
                    f"  hit {int(q_hit)}"
                )

    print_times(run_files)


def print_times(run_files):

    print()
    print("Retrieval time per question (seconds), all questions in the run")
    print(f"{'setup':<22}{'min':>8}{'median':>8}{'max':>8}")
    for run_file in run_files:
        results = json.loads(run_file.read_text(encoding="utf-8"))
        seconds = [result["seconds"] for result in results]
        print(
            f"{run_file.stem:<22}"
            f"{min(seconds):>8.3f}{np.median(seconds):>8.3f}{max(seconds):>8.3f}"
        )


if __name__ == "__main__":
    main()
