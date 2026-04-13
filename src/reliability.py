"""
Reliability & Testing System for VibeFinder.

Provides four capabilities integrated into the main recommendation pipeline:
  A. validate_user_prefs  — input guardrails before any scoring runs
  B. log_session          — structured JSONL logging after every run
  C. run_consistency_check — determinism test: same profile → same top results
  D. run_accuracy_audit    — checks #1 recommendation matches stated genre or mood
"""

import json
import os
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "session_log.jsonl")

_REQUIRED_KEYS = {"genre", "mood", "energy", "likes_acoustic"}


# ── A. Input Guardrails ───────────────────────────────────────────────────────

def validate_user_prefs(prefs: Dict) -> Tuple[bool, List[str]]:
    """
    Validates a user preferences dict before it reaches the recommender.

    Checks:
      - All required keys are present: genre, mood, energy, likes_acoustic
      - energy is a number (int or float) in [0.0, 1.0]
      - likes_acoustic is a bool

    Returns:
        (is_valid, errors) — errors is an empty list when is_valid is True.
    """
    errors = []

    missing = _REQUIRED_KEYS - prefs.keys()
    for key in sorted(missing):
        errors.append(f"Missing required key: '{key}'")

    if "energy" in prefs:
        energy = prefs["energy"]
        if isinstance(energy, bool) or not isinstance(energy, (int, float)):
            errors.append(
                f"'energy' must be a number, got {type(energy).__name__}"
            )
        elif not (0.0 <= float(energy) <= 1.0):
            errors.append(
                f"'energy' must be between 0.0 and 1.0, got {energy}"
            )

    if "likes_acoustic" in prefs:
        if not isinstance(prefs["likes_acoustic"], bool):
            errors.append(
                f"'likes_acoustic' must be True or False, "
                f"got {type(prefs['likes_acoustic']).__name__}"
            )

    return (len(errors) == 0, errors)


# ── B. Structured Logging ─────────────────────────────────────────────────────

def log_session(
    profile_name: str,
    user_prefs: Dict,
    results: List[Tuple[Dict, float, str]],
    log_file: Optional[str] = None,
) -> None:
    """
    Appends one JSON line to logs/session_log.jsonl for each recommendation run.
    Creates the logs/ directory automatically if it does not exist.

    Args:
        profile_name: Human-readable name for this user profile.
        user_prefs:   The preferences dict passed to the recommender.
        results:      Output of recommend_songs() — list of (song, score, reasons).
        log_file:     Override the log path (used in tests). Defaults to LOG_FILE.
    """
    target = log_file or LOG_FILE
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)

    top_recs = [
        {
            "title": song["title"],
            "artist": song["artist"],
            "score": round(score, 4),
        }
        for song, score, _ in results
    ]

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profile_name": profile_name,
        "user_prefs": user_prefs,
        "top_recommendations": top_recs,
        "total_songs_scored": len(results),
    }

    with open(target, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ── C. Consistency Checker ────────────────────────────────────────────────────

def run_consistency_check(
    profile_name: str,
    user_prefs: Dict,
    songs: List[Dict],
    recommend_fn: Callable,
    runs: int = 3,
    top_n: int = 3,
) -> Dict:
    """
    Runs recommend_fn() `runs` times with identical inputs and checks that the
    top-`top_n` song titles are the same across every run.

    Because the scoring algorithm is deterministic (no randomness), this should
    always pass. A failure would indicate a bug in the scoring logic.

    Args:
        profile_name:  Label for reporting.
        user_prefs:    Preferences dict to test.
        songs:         Full song catalog.
        recommend_fn:  The recommend_songs function to call.
        runs:          How many times to run (default 3).
        top_n:         How many top results to compare (default 3).

    Returns:
        Dict with keys: profile, passed, runs, consistent, top_n, detail.
    """
    all_runs = []
    for _ in range(runs):
        results = recommend_fn(user_prefs, songs, k=top_n)
        top_titles = [song["title"] for song, _, _ in results]
        all_runs.append(top_titles)

    consistent = all(run == all_runs[0] for run in all_runs)
    detail = (
        "All runs returned identical top results."
        if consistent
        else f"Inconsistency detected: {all_runs}"
    )

    return {
        "profile": profile_name,
        "passed": consistent,
        "runs": runs,
        "consistent": consistent,
        "top_n": top_n,
        "detail": detail,
    }


# ── D. Accuracy Auditor ───────────────────────────────────────────────────────

def run_accuracy_audit(
    profile_name: str,
    user_prefs: Dict,
    songs: List[Dict],
    recommend_fn: Callable,
) -> Dict:
    """
    Checks that the #1 recommended song matches the user's stated genre OR mood.

    A mismatch surfaces scoring bias (e.g., a high-energy song beating a genre
    match because the energy weight is pulling it up).

    Args:
        profile_name:  Label for reporting.
        user_prefs:    Preferences dict to audit.
        songs:         Full song catalog.
        recommend_fn:  The recommend_songs function to call.

    Returns:
        Dict with keys: profile, passed, top_song, detail.
    """
    results = recommend_fn(user_prefs, songs, k=1)

    if not results:
        return {
            "profile": profile_name,
            "passed": False,
            "top_song": None,
            "detail": "No recommendations returned.",
        }

    top_song, _, _ = results[0]
    genre_match = top_song["genre"].lower() == user_prefs["genre"].lower()
    mood_match = top_song["mood"].lower() == user_prefs["mood"].lower()
    passed = genre_match or mood_match

    if passed:
        matched = []
        if genre_match:
            matched.append("genre")
        if mood_match:
            matched.append("mood")
        detail = f"Top song '{top_song['title']}' matches {' and '.join(matched)}."
    else:
        detail = (
            f"Top song '{top_song['title']}' (genre={top_song['genre']}, "
            f"mood={top_song['mood']}) matches neither the stated genre "
            f"'{user_prefs['genre']}' nor mood '{user_prefs['mood']}'."
        )

    return {
        "profile": profile_name,
        "passed": passed,
        "top_song": top_song["title"],
        "detail": detail,
    }
