# VibeFinder — AI Music Recommender with Reliability System

A content-based music recommender built in Python that suggests songs based on a user's genre, mood, and energy preferences — now enhanced with an integrated Reliability & Testing System as an advanced AI feature.

---

## Original Project: VibeFinder 1.0 (Modules 1–3)

**VibeFinder 1.0** was built during Modules 1–3 as a content-based music recommender simulation. Its goal was to represent songs and user taste profiles as structured data, then apply a weighted scoring algorithm to rank songs from a catalog of 18 tracks. The system demonstrated how real platforms like Spotify use audio features — genre, mood, energy, acousticness — to surface relevant music, making every recommendation fully explainable with a numeric score and written reasons.

---

## What This Project Does and Why It Matters

This project extends VibeFinder 1.0 with a **Reliability & Testing System** — a required advanced AI feature — woven directly into the main application. Every time the recommender runs, it now:

- **Validates inputs** before scoring begins, catching bad data early
- **Logs every session** to a structured JSON file for traceability
- **Tests its own consistency** by running the same profile multiple times and verifying identical results
- **Audits its own accuracy** by checking that the top recommendation actually matches what the user asked for

This matters because even a simple rule-based AI can produce wrong or inconsistent results. Adding guardrails, logging, and self-testing turns VibeFinder from a demo script into a system you can actually trust and debug.

---

## Architecture Overview

```
User Input (profile name + preferences)
        |
        v
  [Guardrails]  validate_user_prefs()
  src/reliability.py  — catches bad types, missing keys, out-of-range energy
        |
        v
  [Recommender Engine]  recommend_songs()
  src/recommender.py  — scores all 18 songs, returns ranked top-k
        |
        v
  [Logger]  log_session()
  src/reliability.py  — appends JSONL entry to logs/session_log.jsonl
        |
        v
  Formatted table output to terminal

  -- separately, via --check flag --

  [Consistency Checker]  run_consistency_check()
  Same profile run x3, top-3 titles must match

  [Accuracy Auditor]  run_accuracy_audit()
  #1 result must match stated genre OR mood

  -- validated by --

  [Automated Tests]  tests/test_reliability.py
  8 pytest tests covering all four reliability functions
```

For a visual version, see [DIAGRAM.md](DIAGRAM.md) — renders automatically on GitHub.

---

## Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/SAFESPACE22/applied-ai-system-project.git
cd applied-ai-system-project
```

**2. (Optional) Create a virtual environment**
```bash
python -m venv .venv

# Mac / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the recommender** (normal mode)
```bash
python -m src.main
```

**5. Run the reliability report** (check mode)
```bash
python -m src.main --check
```

**6. Run all tests**
```bash
python -m pytest
```

> **Note for Windows users:** Use `python -m pytest` instead of just `pytest` if you get a "command not found" error.

---

## Sample Interactions

### Example 1 — Normal run: High-Energy Pop profile

**Input (defined in `src/main.py`):**
```python
{"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False}
```

**Output:**
```
============================================================
  Profile: High-Energy Pop
============================================================
+---+----------------+---------------+-------+----------------------------------------------------------+
| # | Title          | Artist        | Score | Reasons                                                  |
+===+================+===============+=======+==========================================================+
| 1 | Sunrise City   | Neon Echo     |  3.92 | genre match (+2.0), mood match (+1.0), energy sim (+0.92)|
| 2 | Gym Hero       | Max Pulse     |  2.97 | genre match (+2.0), energy similarity (+0.97)            |
| 3 | Rooftop Lights | Indigo Parade |  1.86 | mood match (+1.0), energy similarity (+0.86)             |
| 4 | Back Roads     | Dusty Miles   |  1.70 | mood match (+1.0), energy similarity (+0.70)             |
| 5 | Storm Runner   | Voltline      |  0.99 | energy similarity (+0.99)                                |
+---+----------------+---------------+-------+----------------------------------------------------------+
  [Logged] Session saved to logs/session_log.jsonl
```

---

### Example 2 — Normal run: Chill Lofi profile

**Input:**
```python
{"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True}
```

**Output:**
```
============================================================
  Profile: Chill Lofi
============================================================
+---+--------------------+----------------+-------+---------------------------------------------------------------+
| # | Title              | Artist         | Score | Reasons                                                       |
+===+====================+================+=======+===============================================================+
| 1 | Library Rain       | Paper Lanterns |  4.45 | genre match (+2.0), mood match (+1.0), energy sim (+0.95),    |
|   |                    |                |       | acoustic bonus (+0.5)                                         |
| 2 | Midnight Coding    | LoRoom         |  4.38 | genre match (+2.0), mood match (+1.0), energy sim (+0.88),    |
|   |                    |                |       | acoustic bonus (+0.5)                                         |
| 3 | Focus Flow         | LoRoom         |  3.40 | genre match (+2.0), energy similarity (+0.90), acoustic (+0.5)|
+---+--------------------+----------------+-------+---------------------------------------------------------------+
  [Logged] Session saved to logs/session_log.jsonl
```

---

### Example 3 — Reliability check mode

**Command:**
```bash
python -m src.main --check
```

**Output:**
```
============================================================
  RELIABILITY REPORT
============================================================

[1] Consistency Check  (same profile x3 runs — top-3 must match)

  PASS  High-Energy Pop
        All runs returned identical top results.
  PASS  Chill Lofi
        All runs returned identical top results.
  PASS  Deep Intense Rock
        All runs returned identical top results.

[2] Accuracy Audit  (#1 recommendation must match genre OR mood)

  PASS  High-Energy Pop -> 'Sunrise City'
        Top song 'Sunrise City' matches genre and mood.
  PASS  Chill Lofi -> 'Library Rain'
        Top song 'Library Rain' matches genre and mood.
  PASS  Deep Intense Rock -> 'Thunderclap'
        Top song 'Thunderclap' matches genre and mood.

============================================================
  Overall: ALL CHECKS PASSED
============================================================
```

---

### Example 4 — Guardrail catching bad input

If a profile with an invalid energy value were added:
```python
{"genre": "jazz", "mood": "relaxed", "energy": 1.8, "likes_acoustic": True}
```

**Output:**
```
============================================================
  Profile: Bad Profile
============================================================
  [INVALID] 'energy' must be between 0.0 and 1.0, got 1.8
  Skipping this profile.
```
The recommender never runs — the bad data is caught before any scoring happens.

---

## Design Decisions

**Why a Reliability & Testing System instead of RAG or an agent?**
The existing recommender is a deterministic, rule-based algorithm — adding a language model on top would require an API key and introduce external dependencies that make the project harder to reproduce. A reliability system was the most meaningful upgrade: it addresses a real problem (can I trust this output?) without changing what the recommender fundamentally does.

**Why integrate reliability into `main.py` instead of a separate script?**
The assignment required the feature to change how the system behaves, not just exist alongside it. By calling `validate_user_prefs()` and `log_session()` inside the main run loop, the reliability system is active on every execution — not something a user has to remember to run separately.

**Why JSONL (JSON Lines) for logging?**
Each line is a self-contained, valid JSON object. This makes the log file easy to parse with one line of Python (`json.loads(line)`), easy to `grep`, and safe to append to concurrently without corrupting the file.

**Why pass `recommend_fn` as a parameter to the consistency checker?**
Dependency injection makes the checker testable without touching a real CSV file or importing the recommender module differently depending on context. Tests can pass any function that returns the same shape of output.

**Trade-offs made:**
- The catalog is 18 songs — large enough to demonstrate real behavior, small enough to understand every result by hand
- Genre has the highest weight (+2.0), which creates a "filter bubble" effect documented in the model card. This was left intentional to make the bias visible and discussable
- No diversity penalty — the system can recommend multiple songs from the same artist. This is a known limitation, not an oversight

---

## Testing Summary

### Automated Tests — 10/10 passed

```
platform win32 -- Python 3.11.9, pytest-9.0.2
collected 10 items

tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score PASSED  [ 10%]
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string PASSED  [ 20%]
tests/test_reliability.py::test_validate_valid_prefs_passes PASSED               [ 30%]
tests/test_reliability.py::test_validate_missing_key_fails PASSED                [ 40%]
tests/test_reliability.py::test_validate_energy_out_of_range_fails PASSED        [ 50%]
tests/test_reliability.py::test_validate_energy_wrong_type_fails PASSED          [ 60%]
tests/test_reliability.py::test_validate_likes_acoustic_wrong_type_fails PASSED  [ 70%]
tests/test_reliability.py::test_log_session_creates_valid_jsonl PASSED           [ 80%]
tests/test_reliability.py::test_consistency_check_passes_for_deterministic_scorer PASSED  [ 90%]
tests/test_reliability.py::test_accuracy_audit_pop_profile PASSED                [100%]

10 passed in 0.12s
```

**10 out of 10 tests passed. The recommender produced correct, consistent, well-formatted output across all profiles and all reliability checks.**

### Reliability Report — 6/6 checks passed

The `--check` flag runs 6 live checks (3 consistency + 3 accuracy) against the real catalog:

```
[1] Consistency Check  (same profile x3 — top-3 must match)
  PASS  High-Energy Pop   — All runs returned identical top results.
  PASS  Chill Lofi        — All runs returned identical top results.
  PASS  Deep Intense Rock — All runs returned identical top results.

[2] Accuracy Audit  (#1 recommendation must match genre OR mood)
  PASS  High-Energy Pop   -> 'Sunrise City'   matches genre and mood.
  PASS  Chill Lofi        -> 'Library Rain'   matches genre and mood.
  PASS  Deep Intense Rock -> 'Thunderclap'    matches genre and mood.

Overall: ALL CHECKS PASSED
```

### Guardrail Tests — 4/4 bad inputs blocked

Running the validator live against intentionally broken inputs:

```
[BLOCKED] Missing mood key:      Missing required key: 'mood'
[BLOCKED] Energy out of range:   'energy' must be between 0.0 and 1.0, got 1.8
[BLOCKED] Energy wrong type:     'energy' must be a number, got str
[BLOCKED] Acoustic wrong type:   'likes_acoustic' must be True or False, got str
```

All four invalid inputs were caught before the recommender ever ran.

### Logging — verified live

After a normal run, `logs/session_log.jsonl` contains one JSON entry per profile. Sample entry:

```json
{
  "timestamp": "2026-04-13T03:43:44.766062+00:00",
  "profile_name": "Deep Intense Rock",
  "user_prefs": { "genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": false },
  "top_recommendations": [
    { "title": "Thunderclap",    "artist": "Ironside",  "score": 3.99 },
    { "title": "Storm Runner",   "artist": "Voltline",  "score": 3.96 },
    { "title": "Gym Hero",       "artist": "Max Pulse", "score": 1.98 },
    { "title": "Bass Drop City", "artist": "Voltage",   "score": 1.0  },
    { "title": "Neon Jungle",    "artist": "Cipher",    "score": 0.9  }
  ],
  "total_songs_scored": 5
}
```

### What worked, what didn't, and what was learned

**What worked:** The scoring algorithm is fully deterministic — 3 runs of the same profile returned byte-for-byte identical results every time. The guardrails caught every malformed input type that was thrown at them. The JSONL log is clean and parseable without any post-processing.

**What was surprising:** During the accuracy audit, Gym Hero (a pop song) ranked #3 for the "Deep Intense Rock" profile. It shares neither the rock genre nor the intense mood with... actually it *does* match intense mood — but it is not a rock song. It crept into the list purely on energy similarity (0.98) and mood match (+1.0). This is the genre-dominance bias working in reverse: when there are only two songs in a genre, non-genre songs with strong mood and energy scores fill the lower slots. The audit PASSED because the #1 result (Thunderclap) correctly matched both rock and intense — but it surfaced a real edge case worth watching.

**What didn't work perfectly:** The consistency checker currently only looks at the top-3 song titles. If two songs have identical scores (a tie), sort order could vary across Python versions. This did not happen with the current catalog, but it is a fragile assumption for a larger dataset.

---

## Reflection

### What this project taught me about AI and problem-solving

Building VibeFinder taught me that AI systems are not magic — they are decisions encoded in numbers. Every weight in the scoring formula is a design choice that carries real consequences: weighting genre at +2.0 creates a filter bubble, and weighting energy higher loosens it. The same tradeoff plays out in every real recommendation system, just at a much larger scale with learned weights instead of handcrafted ones.

Adding the reliability layer changed how I think about what "done" means for an AI project. A system that produces output is not the same as a system you can trust. Logging, guardrails, and automated testing are not extras — they are what separate a demo from something you would actually rely on.

### Limitations and biases in this system

- **Genre dominance:** Genre is worth +2.0, the highest single weight. Songs matching the user's genre will almost always rank first, even if their mood or energy is a poor fit. This creates a filter bubble — a rock fan will only ever see rock songs at the top.
- **Thin catalog:** With 18 songs, some genres (classical, country) have only one entry. Users with niche tastes receive lower-quality recommendations simply because the catalog doesn't represent them.
- **No diversity logic:** The system can recommend multiple songs from the same artist back-to-back without any penalty.
- **Single-profile assumption:** A user can only express one genre and one mood. Real listening is more complex — someone might want chill music at night and high-energy music in the morning.

### Could this AI be misused? How would you prevent it?

The recommender itself is low-risk, but the principle it demonstrates — scoring and ranking people or content by weighted features — scales to harmful applications. The same architecture could rank job candidates by encoded demographic proxies, or filter news by engagement weights that amplify outrage. To prevent misuse: make weights auditable and public, require human review for high-stakes decisions, regularly audit outputs for disparate impact, and give users visibility into *why* they received a particular result (VibeFinder already does this with its reasons column).

### What surprised me while testing reliability

I expected the hardest part to be writing the tests. The actually hard part was deciding *what counts as correct*. For the accuracy audit, "the top song must match genre OR mood" seemed obvious — but Gym Hero ranking #3 on a rock profile made me question whether the scoring weights themselves were correct, not just the test. Testing reliability forced me to define what the system *should* do, which is a harder question than whether it *does* run.

### Collaboration with AI during this project

**One instance where AI was helpful:** When designing the reliability module, the AI suggested using dependency injection — passing `recommend_fn` as a parameter to `run_consistency_check()` instead of importing it directly inside the function. This was not something I had considered, but it made the function immediately testable without mocking file I/O or module imports. It was a small change that had a large impact on code quality.

**One instance where AI was flawed:** Early in the project, the AI generated a version of `recommend_songs()` where the `ranked = sorted(...)` line was indented *inside* the for loop, meaning it re-sorted and returned after scoring only the first song — the rest of the catalog was never evaluated. The function returned plausible-looking output (one song instead of five), which made the bug easy to miss. It took reading the code carefully, line by line, to catch it. This was a reminder that AI-generated code needs to be read and understood, not just run.

---

## Project Structure

```
vibefinder/
├── src/
│   ├── main.py           # CLI entry point (normal + --check mode)
│   ├── recommender.py    # Scoring engine: load_songs, score_song, recommend_songs
│   └── reliability.py    # Reliability system: guardrails, logging, checker, auditor
├── tests/
│   ├── test_recommender.py   # Original scoring tests
│   └── test_reliability.py   # 8 reliability tests
├── data/
│   └── songs.csv         # 18-song catalog
├── logs/
│   └── session_log.jsonl # Auto-generated after each run (gitignored)
├── PLAN.md               # Project plan and feature breakdown
├── DIAGRAM.md            # System diagram (Mermaid, renders on GitHub)
├── model_card.md         # AI model documentation and bias analysis
└── requirements.txt      # pandas, pytest, tabulate, streamlit
```

---

## Dependencies

```
pandas
pytest
tabulate
streamlit
```

Install with: `pip install -r requirements.txt`
