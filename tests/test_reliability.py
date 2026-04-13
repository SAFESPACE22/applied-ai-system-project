"""
Reliability test suite for VibeFinder.

Tests the four capabilities in src/reliability.py:
  - Input guardrails (validate_user_prefs)
  - Structured logging (log_session)
  - Consistency checker (run_consistency_check)
  - Accuracy auditor (run_accuracy_audit)

No API key or external service required — all tests are pure Python.
Run with: pytest tests/test_reliability.py
"""

import json
import os
import pytest

from src.recommender import recommend_songs
from src.reliability import (
    validate_user_prefs,
    log_session,
    run_consistency_check,
    run_accuracy_audit,
)


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_songs():
    """A small in-memory catalog used across multiple tests."""
    return [
        {
            "id": 1, "title": "Sunrise City", "artist": "Neon Echo",
            "genre": "pop", "mood": "happy",
            "energy": 0.82, "tempo_bpm": 118.0, "valence": 0.84,
            "danceability": 0.79, "acousticness": 0.18,
        },
        {
            "id": 2, "title": "Midnight Coding", "artist": "LoRoom",
            "genre": "lofi", "mood": "chill",
            "energy": 0.42, "tempo_bpm": 78.0, "valence": 0.56,
            "danceability": 0.62, "acousticness": 0.71,
        },
        {
            "id": 3, "title": "Storm Runner", "artist": "Voltline",
            "genre": "rock", "mood": "intense",
            "energy": 0.91, "tempo_bpm": 152.0, "valence": 0.48,
            "danceability": 0.66, "acousticness": 0.10,
        },
    ]


@pytest.fixture
def valid_prefs():
    return {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False}


# ── A. Guardrail tests ────────────────────────────────────────────────────────

def test_validate_valid_prefs_passes(valid_prefs):
    is_valid, errors = validate_user_prefs(valid_prefs)
    assert is_valid is True
    assert errors == []


def test_validate_missing_key_fails():
    prefs = {"genre": "pop", "energy": 0.8, "likes_acoustic": False}  # missing 'mood'
    is_valid, errors = validate_user_prefs(prefs)
    assert is_valid is False
    assert any("mood" in err for err in errors)


def test_validate_energy_out_of_range_fails():
    prefs = {"genre": "pop", "mood": "happy", "energy": 1.5, "likes_acoustic": False}
    is_valid, errors = validate_user_prefs(prefs)
    assert is_valid is False
    assert any("0.0" in err or "1.0" in err for err in errors)


def test_validate_energy_wrong_type_fails():
    prefs = {"genre": "pop", "mood": "happy", "energy": "high", "likes_acoustic": False}
    is_valid, errors = validate_user_prefs(prefs)
    assert is_valid is False
    assert any("energy" in err for err in errors)


def test_validate_likes_acoustic_wrong_type_fails():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": "yes"}
    is_valid, errors = validate_user_prefs(prefs)
    assert is_valid is False
    assert any("likes_acoustic" in err for err in errors)


# ── B. Logging tests ──────────────────────────────────────────────────────────

def test_log_session_creates_valid_jsonl(valid_prefs, sample_songs, tmp_path):
    results = recommend_songs(valid_prefs, sample_songs, k=3)
    log_file = str(tmp_path / "test_log.jsonl")

    log_session("Test Profile", valid_prefs, results, log_file=log_file)

    assert os.path.exists(log_file)
    with open(log_file, encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["profile_name"] == "Test Profile"
    assert "timestamp" in entry
    assert "top_recommendations" in entry
    assert len(entry["top_recommendations"]) == 3


# ── C. Consistency tests ──────────────────────────────────────────────────────

def test_consistency_check_passes_for_deterministic_scorer(valid_prefs, sample_songs):
    result = run_consistency_check(
        "Pop Profile", valid_prefs, sample_songs, recommend_songs, runs=3, top_n=2
    )
    assert result["passed"] is True
    assert result["consistent"] is True


# ── D. Accuracy audit tests ───────────────────────────────────────────────────

def test_accuracy_audit_pop_profile(sample_songs):
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False}
    result = run_accuracy_audit("High-Energy Pop", prefs, sample_songs, recommend_songs)
    assert result["passed"] is True
    # The top song should be from pop genre or happy mood
    assert result["top_song"] is not None
