# samponlp/pipeline.py

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np
from tqdm import tqdm

from .samponlp import run_scoring_iteration


def _calculate_otsu_threshold(scores: Dict[str, float]) -> float:
    """
    Calculate the optimal threshold using Otsu's method.
    """
    if not scores:
        return 0.1
    score_values = np.array(list(scores.values()))
    min_val, max_val = score_values.min(), score_values.max()
    if np.isclose(min_val, max_val):
        return 0.1
    hist, bin_edges = np.histogram(score_values, bins=256, range=(min_val, max_val))
    hist = hist.astype(float)
    total_pixels = hist.sum()
    if total_pixels == 0:
        return 0.1
    hist /= total_pixels
    best_threshold_idx = 0
    max_variance = 0.0
    w0 = 0.0
    sum0 = 0.0
    total_mean = np.sum(np.arange(256) * hist)
    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = 1.0 - w0
        if w1 == 0:
            break
        sum0 += t * hist[t]
        mean0 = sum0 / w0
        mean1 = (total_mean - sum0) / w1
        variance = w0 * w1 * (mean0 - mean1) ** 2
        if variance > max_variance:
            max_variance = variance
            best_threshold_idx = t
    otsu_threshold = bin_edges[best_threshold_idx]
    return float(otsu_threshold)


@dataclass
class CleaningResults:
    """
    Data structure for storing and saving cleaning results.
    """

    morphemes: List[str]
    discarded: List[Tuple[str, str]]
    final_scores: Dict[str, float]

    @property
    def morpheme_count(self) -> int:
        return len(self.morphemes)

    def save_to_files(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        cleaned_path = os.path.join(output_dir, "cleaned_morphemes.txt")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            for morpheme in self.morphemes:
                f.write(morpheme + "\n")
        print(f"Clean morpheme list saved to: {cleaned_path}")
        discarded_path = os.path.join(output_dir, "discarded_log.tsv")
        with open(discarded_path, "w", encoding="utf-8") as f:
            f.write("Token\tReason\n")
            for token, reason in self.discarded:
                f.write(f"{token}\t{reason}\n")
        print(f"Discarded tokens log saved to: {discarded_path}")
        scores_path = os.path.join(output_dir, "final_scores.json")
        with open(scores_path, "w", encoding="utf-8") as f:
            json.dump(self.final_scores, f, ensure_ascii=False, indent=2)
        print(f"Final scores saved to: {scores_path}")

    @classmethod
    def load_from_files(cls, output_dir: str):
        print(f"Loading results from directory: {output_dir}")
        with open(
            os.path.join(output_dir, "cleaned_morphemes.txt"), "r", encoding="utf-8"
        ) as f:
            morphemes = [line.strip() for line in f]
        with open(
            os.path.join(output_dir, "discarded_log.tsv"), "r", encoding="utf-8"
        ) as f:
            lines = f.readlines()[2:]
            discarded = [tuple(line.strip().split("\t", 1)) for line in lines]
        with open(
            os.path.join(output_dir, "final_scores.json"), "r", encoding="utf-8"
        ) as f:
            final_scores = json.load(f)
        return cls(morphemes=morphemes, discarded=discarded, final_scores=final_scores)


class MorphemeCleaner:
    """
    Main class for running the morpheme cleaning pipeline.
    """

    def __init__(self, language: str = "uralic", **kwargs):
        self.language = language
        self.config = {
            "min_length": kwargs.get("min_length", 1),
            "min_type_support": kwargs.get("min_type_support", 3),
            "max_iterations": kwargs.get("max_iterations", 20),
            "convergence_threshold": kwargs.get("convergence_threshold", 1e-5),
        }

        self._one_char_whitelists = {
            "finnish": {"n", "t"},
            "estonian": {"d", "s", "t"},
            "hungarian": {"t", "k", "m", "d", "i", "a", "s"},
            "uralic": {"n", "t", "d", "s", "k", "m", "i", "a"},
        }
        self.one_char_whitelist = self._one_char_whitelists.get(
            self.language, self._one_char_whitelists["uralic"]
        )

        self._allowed_chars_regex = {
            "finnish": re.compile(r"^[a-zäöšž]+$"),
            "estonian": re.compile(r"^[a-zäöüõšž]+$"),
            "hungarian": re.compile(r"^[a-záéíóöőúüű]+$"),
            "uralic": re.compile(r"^[a-zäöüõšžáéíóöőúüű]+$"),
        }
        self.allowed_chars_pattern = self._allowed_chars_regex.get(
            self.language, self._allowed_chars_regex["uralic"]
        )

        print(f"Initialized MorphemeCleaner (IMDP) with parameters: {self.config}")
        print(f"Using whitelist for 1-char morphemes: {self.one_char_whitelist}")
        print(
            f"Using alphabet validation pattern: {self.allowed_chars_pattern.pattern}"
        )

    def _initial_classification_and_scoring(
        self, raw_morphemes_path: str
    ) -> Tuple[Set[str], Set[str], Dict[str, float], List[Tuple[str, str]]]:
        root_candidates_pre: Set[str] = set()
        affix_candidates_pre: Set[str] = set()
        junk_discarded: List[Tuple[str, str]] = []

        with open(raw_morphemes_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        print(f"\n--- Step 1.1: Initial filtering of {len(lines)} lines ---")
        for line in tqdm(lines, desc="Step 1.1: Filtering"):
            token = line.strip().split(maxsplit=1)[0]
            original_token = token
            reason = ""

            if not token:
                continue

            morpheme = original_token.lstrip("-").rstrip("-").lower()
            is_affix = original_token.startswith("-") or original_token.endswith("-")

            if not self.allowed_chars_pattern.match(morpheme):
                reason = "Characters not from target alphabet"

            elif re.search(r"[][\^$]", token):
                reason = "Regular expression"
            elif not any(c.isalpha() for c in token):
                reason = "Punctuation or number"
            elif "." in token:
                reason = "URL or file"
            elif token.isnumeric():
                reason = "Number"
            elif token.isupper() and len(token) > 1:
                reason = "Abbreviation"
            elif token[0].isupper():
                reason = "Proper noun"

            if reason:
                junk_discarded.append((original_token, reason))
                continue

            is_valid_len = False
            if len(morpheme) >= self.config["min_length"]:
                is_valid_len = True
            elif len(morpheme) == 1 and morpheme in self.one_char_whitelist:
                is_valid_len = True

            if not is_valid_len:
                junk_discarded.append((original_token, "Too short or invalid"))
                continue

            if is_affix:
                affix_candidates_pre.add(morpheme)
            else:
                root_candidates_pre.add(morpheme)

        initial_candidates = root_candidates_pre | affix_candidates_pre

        print(
            f"\n--- Step 1.2: Type-support filtering ({len(initial_candidates)} candidates) ---"
        )

        corpus_string = " ".join(initial_candidates)
        final_candidates: Set[str] = set()
        min_support = self.config["min_type_support"]

        for token in tqdm(initial_candidates, desc="Step 1.2: Type-support"):
            if corpus_string.count(token) >= min_support:
                final_candidates.add(token)
            else:
                junk_discarded.append((token, f"Low type-support (<{min_support})"))

        final_roots = {c for c in final_candidates if c in root_candidates_pre}
        final_affixes = {c for c in final_candidates if c in affix_candidates_pre}

        initial_scores = {token: 1.0 / len(token) for token in final_candidates}

        print(
            f"Step 1 complete: {len(final_roots)} roots, {len(final_affixes)} affixes passed filters."
        )
        return final_roots, final_affixes, initial_scores, junk_discarded

    def process(self, raw_morphemes_path: str, output_dir: str) -> CleaningResults:
        root_candidates, affix_candidates, scores, junk = (
            self._initial_classification_and_scoring(raw_morphemes_path)
        )

        print("\n--- Step 2: Running iterative score updates ---")

        for i in range(self.config["max_iterations"]):
            print(f"\n>> Iteration {i + 1}/{self.config['max_iterations']}:")

            new_scores = run_scoring_iteration(
                root_candidates, affix_candidates, scores, self.one_char_whitelist
            )

            max_change = 0.0
            for token in scores:
                change = abs(scores[token] - new_scores.get(token, 0.0))
                if change > max_change:
                    max_change = change

            scores = new_scores
            print(f"   Maximum score change in this iteration: {max_change:.8f}")

            if max_change < self.config["convergence_threshold"]:
                print(f"   Algorithm converged. Stopping at iteration {i + 1}.")
                break

        print("\n--- Step 3: Final threshold-based filtering ---")

        auto_threshold = _calculate_otsu_threshold(scores)
        print(f"   Automatically determined threshold (Otsu): {auto_threshold:.4f}")

        atomic_morphemes = []
        for token in tqdm(sorted(scores.keys()), desc="Final filtering"):
            score = scores[token]
            if score >= auto_threshold:
                atomic_morphemes.append(token)
            else:
                junk.append((token, f"Low atomicity score ({score:.4f})"))

        final_morphemes = sorted(atomic_morphemes)
        all_discarded = sorted(junk, key=lambda x: x[0])

        print("\n--- Summary and saving ---")
        results = CleaningResults(
            morphemes=final_morphemes, discarded=all_discarded, final_scores=scores
        )
        results.save_to_files(output_dir)

        return results
