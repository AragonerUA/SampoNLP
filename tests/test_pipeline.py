# tests/test_pipeline.py

import pytest

from samponlp.samponlp import run_scoring_iteration

# --- Test fixtures ---


@pytest.fixture
def dirty_morpheme_file(tmp_path):
    """Creates a temporary "dirty" file for testing classification and type support."""
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


def test_scoring_iteration_logic():
    """Test basic scoring iteration logic in Rust core."""
    root_candidates = {"ház", "ban", "házban"}
    affix_candidates = set()  # All are roots for this test
    initial_scores = {"ház": 1.0 / 3.0, "ban": 1.0 / 3.0, "házban": 1.0 / 6.0}

    new_scores = run_scoring_iteration(
        root_candidates, affix_candidates, initial_scores, set()  # empty whitelist
    )

    assert new_scores["ház"] >= initial_scores["ház"]
    assert new_scores["ban"] >= initial_scores["ban"]
    assert new_scores["házban"] < initial_scores["házban"]

    explanation_power = initial_scores["ház"] + initial_scores["ban"]
    expected_new_score = (1.0 / 6.0) / (1.0 + explanation_power)
    assert abs(new_scores["házban"] - expected_new_score) < 1e-9


def test_multicomponent_decomposition():
    """Test that Rust core finds 3+ part decompositions."""
    root_candidates = {"ház", "unk", "ban", "házunkban"}
    affix_candidates = set()  # All are roots for this test
    initial_scores = {
        "ház": 1.0 / 3.0,
        "unk": 1.0 / 3.0,
        "ban": 1.0 / 3.0,
        "házunkban": 1.0 / 9.0,
    }

    new_scores = run_scoring_iteration(
        root_candidates, affix_candidates, initial_scores, set()  # empty whitelist
    )

    assert new_scores["ház"] >= initial_scores["ház"]
    assert new_scores["unk"] >= initial_scores["unk"]
    assert new_scores["ban"] >= initial_scores["ban"]
    assert new_scores["házunkban"] < initial_scores["házunkban"]
