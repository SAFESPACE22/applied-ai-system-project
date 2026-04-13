# VibeFinder AI Feature Plan: Reliability & Testing System

## Overview

The existing VibeFinder project uses rule-based weighted scoring to recommend music. This plan adds a **Reliability & Testing System** as the required AI feature — no external API needed — that is fully integrated into the main application logic.

**AI Feature Chosen:** Reliability or Testing System
> "You include ways to measure or test how well your AI performs. Example: A script that checks if your AI gives consistent answers."

---

## What Gets Added

### `src/reliability.py` — Core reliability module

**A. Input Guardrails** (`validate_user_prefs`)
- Validates that all required keys exist: `genre`, `mood`, `energy`, `likes_acoustic`
- Checks that `energy` is a float in `[0.0, 1.0]`
- Checks that `likes_acoustic` is a bool
- Returns `(is_valid: bool, errors: list[str])`
- Called by `main.py` before any recommendation is made — bad inputs are caught early

**B. Structured Logging** (`log_session`)
- Appends one JSON entry per recommendation run to `logs/session_log.jsonl`
- Fields: `timestamp`, `profile_name`, `user_prefs`, `top_recommendations` (title, artist, score), `total_songs_scored`
- Creates `logs/` directory automatically if missing

**C. Consistency Checker** (`run_consistency_check`)
- Runs a given profile through `recommend_songs()` N times (default 3)
- Compares the top-3 results across all runs — must be identical (deterministic scoring)
- Returns pass/fail + details

**D. Accuracy Auditor** (`run_accuracy_audit`)
- For each profile, checks that the #1 recommendation matches the stated genre OR mood
- Reports pass/fail per profile and surfaces bias (e.g., genre dominance)

---

### Modified `src/main.py`

- Before each profile: `validate_user_prefs()` — skip invalid profiles with a clear error message
- After each profile: `log_session()` — silently write structured log entry
- New `--check` flag: runs consistency check + accuracy audit on all built-in profiles

---

### New `tests/test_reliability.py`

Eight pytest tests — no API key, no mocking needed:

| Test | What It Verifies |
|---|---|
| `test_validate_valid_prefs_passes` | Correct prefs dict passes validation |
| `test_validate_missing_key_fails` | Missing `mood` key returns an error |
| `test_validate_energy_out_of_range_fails` | `energy=1.5` returns an error |
| `test_validate_energy_wrong_type_fails` | `energy="high"` returns an error |
| `test_validate_likes_acoustic_wrong_type_fails` | `likes_acoustic="yes"` returns an error |
| `test_consistency_check_passes` | Same profile always gives same top-3 (determinism) |
| `test_log_session_creates_valid_jsonl` | Log file gets a parseable JSON line |
| `test_accuracy_audit_pop_profile` | Top result for pop/happy profile is pop or happy |

---

## Files Summary

| File | Action |
|---|---|
| `src/reliability.py` | **Create** |
| `src/main.py` | **Modify** (add validation, logging, `--check` flag) |
| `tests/test_reliability.py` | **Create** |
| `logs/.gitkeep` | **Create** (track folder, gitignore log files) |
| `src/recommender.py` | No change |
| `tests/test_recommender.py` | No change |
| `requirements.txt` | No change |

---

## How the Feature Integrates (Not Standalone)

The reliability module runs inside `main.py`'s normal execution path:

```
python -m src.main
  → for each profile:
      validate_user_prefs(prefs)     ← guardrail: skip bad inputs
      recommend_songs(...)            ← existing scoring logic
      log_session(...)                ← write to logs/session_log.jsonl
  → print formatted results as before

python -m src.main --check
  → run_consistency_check() on all profiles
  → run_accuracy_audit() on all profiles
  → print pass/fail report
```

---

## How to Run

```bash
# Run existing tests (all should still pass)
pytest tests/test_recommender.py

# Run new reliability tests (no API key needed)
pytest tests/test_reliability.py

# Normal recommendation run (now includes guardrails + logging)
python -m src.main

# Reliability check mode
python -m src.main --check
```

---

## Why This Satisfies the Assignment

- **Useful with AI:** Tests and validates the behavior of the AI recommender system
- **Integrated into main logic:** Guardrails and logging run on every execution of `main.py`
- **Logging and guardrails:** Structured JSONL log + input validation on every run
- **Reproducible:** Pure Python, no API keys, install only what's already in `requirements.txt`
- **Clear setup:** `pip install -r requirements.txt` then `python -m src.main`
