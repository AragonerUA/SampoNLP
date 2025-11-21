# samponlp/stats.py
from collections import Counter
from typing import Set

from tqdm import tqdm


def _calculate_frequencies(
    root_candidates: Set[str], corpus_path: str, min_frequency: int
) -> Set[str]:
    """
    Step 2a: Counts how often the root candidates appear as whole words in the corpus.
    Returns only those that occur more frequently than `min_frequency`.
    """
    print(
        f"\nStarting frequency counting for {len(root_candidates)} root candidates..."
    )

    word_counts = Counter()

    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="  Corpus analysis (roots)"):
            words = line.strip().lower().split()
            word_counts.update(words)

    valid_roots = {
        root for root in root_candidates if word_counts.get(root, 0) >= min_frequency
    }

    print(
        f"{len(valid_roots)} out of {len(root_candidates)} roots passed the statistical check."
    )
    return valid_roots


def _calculate_productivity(
    affix_candidates: Set[str], corpus_path: str, min_productivity: int
) -> Set[str]:
    """
    Step 2b: Measures the “productivity” of affixes.
    Productivity is how many distinct words in the corpus start or end with a given affix.
    """
    print(
        f"\nStarting productivity measurement for {len(affix_candidates)} affix candidates..."
    )

    productivity_scores = {affix: set() for affix in affix_candidates}

    prefixes = {aff for aff in affix_candidates if len(aff) <= 10}
    suffixes = {aff for aff in affix_candidates if len(aff) <= 10}

    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="  Corpus analysis (affixes)"):
            words = line.strip().lower().split()
            for word in words:
                for i in range(1, min(len(word), 11)):
                    prefix = word[:i]
                    if prefix in prefixes:
                        productivity_scores[prefix].add(word)

                for i in range(1, min(len(word), 11)):
                    suffix = word[-i:]
                    if suffix in suffixes:
                        productivity_scores[suffix].add(word)

    valid_affixes = {
        affix
        for affix, words in productivity_scores.items()
        if len(words) >= min_productivity
    }

    print(
        f"{len(valid_affixes)} out of {len(affix_candidates)} affixes passed the statistical check."
    )
    return valid_affixes
