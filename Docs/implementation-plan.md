# Implementation Plan: AI-Powered Restaurant Recommendation System - Phase 2

This document outlines the design and implementation details for Phase 2 (Filter & Candidate Generation Engine) of the Zomato-inspired AI-Powered Restaurant Recommendation System.

## User Review Required
> [!IMPORTANT]
> **Constraint Relaxation Limits:** To prevent infinite loops during relaxation (e.g. if a location contains fewer than 10 restaurants in total), we will cap the relaxation iterations at 10, or stop when `min_rating` reaches `1.0`.
> **Cuisines Substring Search:** Since cuisines are pipe-separated strings in the database, we will filter them using SQL `LIKE` or list containment in Python to allow flexible matching (e.g., matching "Italian" for "italian|pizza").

## Open Questions
- None. (The sorting keys and relaxation parameters are explicitly specified).

## Proposed Changes
We will create and update the following files:

### Project Directory Layout
```text
project_root/
├── src/
│   ├── filter_engine.py       # [NEW] Contains SQL querying, sorting, and relaxation logic
│   └── config.py              # [MODIFY] Add filter configuration thresholds
├── tests/
│   └── test_filter_engine.py  # [NEW] Tests filter constraints, relaxation, and sorting keys
└── Docs/
    ├── walkthrough_phase2.md  # [NEW] Phase 2 walkthrough report
    └── implementation-plan.md # [MODIFY] Update with Phase 2
```

### Component Breakdown

#### 1. Configuration: [src/config.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/src/config.py) [MODIFY]
- Add threshold constants:
  - `RELAXATION_TARGET_COUNT = 10`
  - `RATING_RELAX_STEP = 0.2`
  - `BUDGET_RELAX_PERCENT = 0.10`

#### 2. Candidate Generation: [src/filter_engine.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/src/filter_engine.py) [NEW]
- Define `get_candidates(...)` matching:
  - `location`: Case-insensitive text match.
  - `cuisines`: List of cuisines or string. Match any requested cuisine using substring matching (e.g. `cuisines LIKE '%cuisine%'`).
  - `min_rating`: Numerical threshold.
  - `max_budget`: Average cost threshold.
  - `online_order`: Optional boolean.
  - `book_table`: Optional boolean.
- **Deduplication / Relaxation Loop**:
  - Run SQL query. If returned count is `< 10`, decrease `min_rating` by `0.2` and increase `max_budget` by `10%` (`max_budget * 1.1`).
  - Cap loop at `10` iterations or when `min_rating` drops to `1.0`.
- **Ranking / Sorting**:
  - Calculate `popularity_score = (rating * 0.6) + (log1p(votes) * 0.4)` (using standard numpy / math log).
  - Sort list of candidate dicts/DataFrame by `rating` desc, `votes` desc, `popularity_score` desc.

#### 3. Verification: [tests/test_filter_engine.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/tests/test_filter_engine.py) [NEW]
- Create unit tests for:
  - Filtering by location (case-insensitive) and cuisines.
  - Minimum rating and budget constraints.
  - Online ordering and table booking Boolean flags.
  - Checking constraint relaxation triggers correctly when matches are `< 10`.
  - Checking correct multi-key sorting (rating -> votes -> popularity).

---

## Verification Plan

### Automated Tests
- Run `pytest tests/test_filter_engine.py`

### Manual Verification
- Query `get_candidates` with extremely strict criteria (e.g., Koramangala, rating > 4.8, budget < 200) to verify relaxation triggers and logs relaxation steps.
