"""
Command line runner for the Music Recommender Simulation.

Usage:
  python -m src.main           Run recommendations for all built-in profiles.
  python -m src.main --check   Run the reliability report (consistency + accuracy audit).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs
from reliability import (
    validate_user_prefs,
    log_session,
    run_consistency_check,
    run_accuracy_audit,
)
from tabulate import tabulate


PROFILES = {
    "High-Energy Pop":  {"genre": "pop",  "mood": "happy",   "energy": 0.9,  "likes_acoustic": False},
    "Chill Lofi":       {"genre": "lofi", "mood": "chill",   "energy": 0.3,  "likes_acoustic": True},
    "Deep Intense Rock":{"genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
}


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    songs = load_songs(os.path.join(base_dir, "data", "songs.csv"))

    if "--check" in sys.argv:
        _run_reliability_report(songs)
        return

    for profile_name, user_prefs in PROFILES.items():
        print(f"\n{'='*60}")
        print(f"  Profile: {profile_name}")
        print(f"{'='*60}")

        # A. Guardrail: validate inputs before recommending
        is_valid, errors = validate_user_prefs(user_prefs)
        if not is_valid:
            for err in errors:
                print(f"  [INVALID] {err}")
            print("  Skipping this profile.\n")
            continue

        recommendations = recommend_songs(user_prefs, songs, k=5)

        table = []
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            table.append([rank, song["title"], song["artist"], f"{score:.2f}", explanation])
        print(tabulate(table, headers=["#", "Title", "Artist", "Score", "Reasons"], tablefmt="grid"))

        # B. Log every successful run
        log_session(profile_name, user_prefs, recommendations)
        print(f"  [Logged] Session saved to logs/session_log.jsonl\n")


def _run_reliability_report(songs) -> None:
    """Runs the consistency checker and accuracy auditor on all built-in profiles."""
    print("\n" + "=" * 60)
    print("  RELIABILITY REPORT")
    print("=" * 60)

    # C. Consistency check
    print("\n[1] Consistency Check  (same profile x3 runs — top-3 must match)\n")
    all_passed = True
    for profile_name, user_prefs in PROFILES.items():
        result = run_consistency_check(profile_name, user_prefs, songs, recommend_songs)
        status = "PASS" if result["passed"] else "FAIL"
        if not result["passed"]:
            all_passed = False
        print(f"  {status}  {profile_name}")
        print(f"        {result['detail']}")

    # D. Accuracy audit
    print("\n[2] Accuracy Audit  (#1 recommendation must match genre OR mood)\n")
    for profile_name, user_prefs in PROFILES.items():
        result = run_accuracy_audit(profile_name, user_prefs, songs, recommend_songs)
        status = "PASS" if result["passed"] else "FAIL"
        if not result["passed"]:
            all_passed = False
        print(f"  {status}  {profile_name} -> '{result['top_song']}'")
        print(f"        {result['detail']}")

    print("\n" + "=" * 60)
    overall = "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED — see details above"
    print(f"  Overall: {overall}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
