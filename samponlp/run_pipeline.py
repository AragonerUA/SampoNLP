# run_pipeline.py

import time
from collections import Counter, defaultdict
from typing import Dict, List

from samponlp import MorphemeCleaner


def print_length_statistics(tokens: List[str], title: str):
    """Outputs statistics on token lengths."""
    print("\n" + "=" * 50)
    print(f"Length statistics: {title}")
    print("=" * 50)

    if not tokens:
        print("Token list is empty.")
        return

    length_counts = Counter(len(token) for token in tokens)

    print(f"{'Length':<10} | {'Amount':<15}")
    print("-" * 28)
    for length, count in sorted(length_counts.items()):
        print(f"{length:<10} | {count:<15}")
    print("-" * 28)
    print(f"{'Overall:':<10} | {len(tokens):<15}")


def print_detailed_score_distribution(scores: Dict[str, float], auto_threshold: float):
    """Outputs detailed statistics on score distribution."""
    print("\n" + "=" * 80)
    print(f"Detailed Score Distribution Statistics (SCORES)")
    print("=" * 80)

    if not scores:
        print("Dictionary of scores is empty.")
        return

    bins = defaultdict(int)
    for score in scores.values():
        if score >= 0.1:
            bin_index = int(score / 0.05)
            bins[bin_index * 0.05] += 1
        else:
            bin_index = int(score / 0.01)
            bins[bin_index * 0.01] += 1

    max_count = max(bins.values()) if bins else 1

    print(f"{'Range of scores':<20} | {'Amount':<15} | {'Histogram'}")
    print("-" * 80)

    sorted_bins = sorted(bins.keys(), reverse=True)

    gap_found = False
    for lower_bound in sorted_bins:
        count = bins[lower_bound]
        step = 0.05 if lower_bound >= 0.1 else 0.01
        upper_bound = lower_bound + step
        bar_length = int((count / max_count) * 50) if max_count > 0 else 0
        bar = "█" * bar_length
        range_str = f"{lower_bound:.2f} - {upper_bound:.2f}"

        if not gap_found and upper_bound <= auto_threshold < (upper_bound + step):
            pass

        if (
            not gap_found
            and auto_threshold >= lower_bound
            and auto_threshold < upper_bound
        ):
            print("-" * 80)
            print(
                f"--- Auto-threshold ({auto_threshold:.4f}) is within this range ---".center(
                    80
                )
            )
            print("-" * 80)
            gap_found = True

        print(f"{range_str:<20} | {count:<15} | {bar}")

    print("-" * 80)
    print(f"{'Overall:':<20} | {len(scores):<15} |")


def main():
    """Run the morpheme cleaning pipeline and analyze results."""
    print("Run pipeline SampoNLP...")
    start_time = time.time()

    # --- 1. Configuration ---
    # These parameters are passed to the tool. `max_iterations` and
    # `convergence_threshold` are used for automatic stopping.
    config = {
        "min_length": 1,
        "min_type_support": 3,
        "max_iterations": 100,
        "convergence_threshold": 1e-7,
    }

    LANGUAGE = "estonian"
    raw_file = "data/estonian_morphemes.txt"
    output_dir = "results/estonian_cleaned_final"

    try:
        cleaner = MorphemeCleaner(language=LANGUAGE, **config)

        results = cleaner.process(raw_morphemes_path=raw_file, output_dir=output_dir)

        end_time = time.time()
        duration = end_time - start_time

        # --- Final statistics ---
        print("\n" + "=" * 50)
        print("Pipeline is successfully completed!")
        print(
            f"   - Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)"
        )
        print(f"   - Found clean atomic morphemes: {results.morpheme_count}")
        print(f"   - Discarded tokens: {len(results.discarded)}")
        print(f"   - Results saved in folder: {output_dir}")
        print("=" * 50)

        print_length_statistics(results.morphemes, "Clean morphemes")

        discarded_tokens = [item[0] for item in results.discarded]
        print_length_statistics(discarded_tokens, "Discarded tokens")

        # Find the threshold that was automatically computed inside `process`
        # Most reliable way - find it in the discarded tokens log
        auto_threshold = 0.1  # Default value if something goes wrong
        try:
            # Look for the first entry discarded due to low score
            first_low_score_reason = next(
                entry[1]
                for entry in results.discarded
                if "Low atomicity score" in entry[1]
            )
            # Extract the threshold that was used for this decision
            # Logic depends on how we find the threshold in `pipeline.py`
            # Let's assume we can extract it from `results`

            # --- MORE RELIABLE METHOD ---
            # We need `process` to return the computed threshold.
            # Until then, we can only recalculate it.
            from samponlp.pipeline import _calculate_otsu_threshold

            calculated_threshold = _calculate_otsu_threshold(results.final_scores)
            auto_threshold = calculated_threshold

        except StopIteration:
            print(
                "No tokens found discarded due to low score. Histogram may be inaccurate."
            )

        print_detailed_score_distribution(results.final_scores, auto_threshold)

    except Exception as e:
        print(f"\n An error occurred during pipeline execution: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
