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

**What was tested:**

| Test | What it checks |
|---|---|
| `test_validate_valid_prefs_passes` | A correct prefs dict passes all guardrails |
| `test_validate_missing_key_fails` | Missing `mood` key is caught with a clear error |
| `test_validate_energy_out_of_range_fails` | `energy=1.5` is rejected |
| `test_validate_energy_wrong_type_fails` | `energy="high"` (string) is rejected |
| `test_validate_likes_acoustic_wrong_type_fails` | `likes_acoustic="yes"` (string) is rejected |
| `test_log_session_creates_valid_jsonl` | Log file is created and contains parseable JSON |
| `test_consistency_check_passes_for_deterministic_scorer` | Same profile x3 always returns identical top-3 |
| `test_accuracy_audit_pop_profile` | Top result for pop/happy profile is pop or happy |

**Results: 10/10 tests pass** (2 original + 8 new)

**What worked well:**
The consistency test confirmed that the scoring algorithm is fully deterministic — no randomness, no floating-point surprises across runs. The accuracy audit passed for all three profiles, meaning the genre weight (+2.0) is doing its job: the best genre match always surfaces first.

**What was surprising:**
During the accuracy audit experiment, a pop song (Gym Hero) ranked #3 for the "Deep Intense Rock" profile — purely because of its high energy and intense mood. This confirmed the known bias: energy and mood can overcome genre for songs that sit close enough on those dimensions. It's a useful signal that the scoring weights may need tuning for edge cases.

**What was learned:**
Writing tests before you know what will fail is harder than it sounds. The guardrail tests required thinking through all the ways a user could pass bad data — wrong type, wrong range, missing entirely — before any of those bugs had actually appeared. That kind of proactive thinking is exactly what makes production code more reliable.

---

## Reflection

Building VibeFinder taught me that AI systems are not magic — they are decisions encoded in numbers. Every weight in the scoring formula is a design choice that carries real consequences: weighting genre at +2.0 creates a filter bubble, and weighting energy higher loosens it. The same tradeoff plays out in every real recommendation system, just at a much larger scale with learned weights instead of handcrafted ones.

Adding the reliability layer changed how I think about what "done" means for an AI project. A system that produces output is not the same as a system you can trust. Logging, guardrails, and automated testing are not extras — they are what separate a demo from something you would actually rely on.

The biggest takeaway: the most important questions in AI are not "does it work?" but "how do I know it works, and what happens when it doesn't?"

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
