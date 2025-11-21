# tests/test_pipeline.py

import pytest
import os
import numpy as np
from samponlp import MorphemeCleaner, CleaningResults
from samponlp._core import run_scoring_iteration
from samponlp.pipeline import _calculate_otsu_threshold

# --- Test fixtures ---

@pytest.fixture
def dirty_morpheme_file(tmp_path):
    """Creates a temporary “dirty” file for testing classification and type support."""
    content = (
        "-ban\n-be\n-kal\nleg-\n"
        "ház\nasztal\nváros\nvárosház\n"
        "Aba\nAdy\n1984\n!!!\n.docx-es\n"
        "a\nt\n-t\n[aeiou]\n"
        "xyzq\n"
    )
    file_path = tmp_path / "dirty.txt"
    file_path.write_text(content)
    return str(file_path)

# --- Tests ---

def test_initial_classification_and_scoring(dirty_morpheme_file):
    cleaner = MorphemeCleaner(min_length=2, min_type_support=2)
    
    candidates, initial_scores, junk = cleaner._initial_classification_and_scoring(dirty_morpheme_file)

    expected_survivors = {
        "ban", "be", "kal", "leg",
        "ház", "asztal", "város", "városház"
    }
    assert expected_survivors.issubset(candidates)
    assert "xyzq" not in candidates
    
    junk_tokens = {item[0] for item in junk}
    expected_junk_subset = {"Aba", "Ady", "1984", "xyzq"}
    assert expected_junk_subset.issubset(junk_tokens)

def test_scoring_iteration_logic():
    candidates = {"ház", "ban", "házban"}
    initial_scores = {
        "ház": 1.0 / 3.0,
        "ban": 1.0 / 3.0,
        "házban": 1.0 / 6.0
    }
    
    new_scores = run_scoring_iteration(candidates, initial_scores)

    assert new_scores["ház"] >= initial_scores["ház"]
    assert new_scores["ban"] >= initial_scores["ban"]
    assert new_scores["házban"] < initial_scores["házban"]
    
    explanation_power = initial_scores["ház"] + initial_scores["ban"]
    expected_new_score = (1.0 / 6.0) / (1.0 + explanation_power)
    assert abs(new_scores["házban"] - expected_new_score) < 1e-9

def test_multicomponent_decomposition():
    candidates = {"ház", "unk", "ban", "házunkban"}
    initial_scores = {
        "ház": 1.0 / 3.0,
        "unk": 1.0 / 3.0,
        "ban": 1.0 / 3.0,
        "házunkban": 1.0 / 9.0
    }

    new_scores = run_scoring_iteration(candidates, initial_scores)

    assert new_scores["ház"] >= initial_scores["ház"]
    assert new_scores["unk"] >= initial_scores["unk"]
    assert new_scores["ban"] >= initial_scores["ban"]
    assert new_scores["házunkban"] < initial_scores["házunkban"]

def test_otsu_threshold_calculation():
    scores = {
        **{f"low_score_{i}": np.random.normal(0.05, 0.01) for i in range(100)},
        **{f"high_score_{i}": np.random.normal(0.25, 0.02) for i in range(50)}
    }
    
    threshold = _calculate_otsu_threshold(scores)
    
    assert 0.1 < threshold < 0.2