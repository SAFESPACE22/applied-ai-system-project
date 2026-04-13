# VibeFinder System Diagram

> Render this diagram in GitHub, VS Code (Mermaid extension), or [app.diagrams.net](https://app.diagrams.net).

```mermaid
flowchart TD
    A([👤 User / CLI Input\nprofile_name + prefs dict]) --> B

    subgraph GUARD ["🛡️ Guardrails — src/reliability.py"]
        B[validate_user_prefs\ncheck keys · energy range · types]
        B -- invalid --> C([⚠️ Error Message\nskip profile])
        B -- valid --> D
    end

    subgraph ENGINE ["⚙️ Recommender Engine — src/recommender.py"]
        D[load_songs\nreads data/songs.csv]
        D --> E[score_song\ngenre +2.0 · mood +1.0\nenergy similarity · acoustic +0.5]
        E --> F[recommend_songs\nsort & return top-k]
    end

    subgraph LOG ["📋 Logger — src/reliability.py"]
        F --> G[log_session\nappend to logs/session_log.jsonl\ntimestamp · prefs · top results]
    end

    G --> H([🖥️ Formatted Output\ntabulated recommendations])

    subgraph CHECK ["🔬 Reliability Checker — src/reliability.py  ·  python -m src.main --check"]
        I[run_consistency_check\nsame profile × 3 runs\ntop-3 must match]
        J[run_accuracy_audit\n#1 result must match\nstated genre OR mood]
    end

    H -.->|human reviews output| K
    I --> K([📊 Pass / Fail Report\nprinted to terminal])
    J --> K

    subgraph TESTS ["🧪 Automated Tests — tests/test_reliability.py  ·  pytest"]
        L[8 unit tests\nguardrail edge cases\nconsistency · logging · accuracy]
    end

    L -.->|validates| GUARD
    L -.->|validates| CHECK
    L -.->|validates| LOG
```

## Component Key

| Component | File | Role |
|---|---|---|
| **Guardrails** | `src/reliability.py` | Validates user prefs before anything runs |
| **Recommender Engine** | `src/recommender.py` | Scores and ranks songs from `data/songs.csv` |
| **Logger** | `src/reliability.py` | Writes structured JSONL entry per run |
| **Reliability Checker** | `src/reliability.py` | Consistency + accuracy audit (`--check` flag) |
| **Automated Tests** | `tests/test_reliability.py` | 8 pytest tests, no API key needed |

## Data Flow

```
User Input → Guardrails → Recommender Engine → Logger → Terminal Output
                ↓
         (invalid input
          skipped here)
```
