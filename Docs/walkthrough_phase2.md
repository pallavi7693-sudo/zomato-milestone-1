# Walkthrough: Phase 2 (Filter & Candidate Generation Engine)

Phase 2 implementation for the AI-Powered Restaurant Recommendation System is complete. We designed, coded, and verified the candidate filtering, constraint relaxation, sorting keys, database indexing, and test validation layer.

---

## 1. File Map of Changes
* [src/config.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/src/config.py): Modified to include relaxation targets and step constants:
  - `RELAXATION_TARGET_COUNT = 10`
  - `RATING_RELAX_STEP = 0.2`
  - `BUDGET_RELAX_PERCENT = 0.10`
* [src/filter_engine.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/src/filter_engine.py): Created the engine to interface with the SQLite database, containing:
  - `get_candidates(...)`: filters by location (case-insensitive), cuisines, rating, budget range (`min_budget` to `max_budget`), and Boolean flags. Exposes a `max_candidates` parameter (default 50) safeguarded at a maximum cap of 50.
  - Constraint Relaxation: decreases rating by `0.2` and symmetrically widens budget boundaries by `10%` if returned candidate count is `< 10`, capping at `10` steps or rating `<= 1.0`.
  - Popularity Score Calculation: `popularity_score = (rating * 0.6) + (log1p(votes) * 0.4)`.
  - Sorting: sorts candidates by `rating` desc, `votes` desc, `popularity_score` desc.
  - **Enhanced Output Format:** Returns a dictionary containing:
    ```json
    {
      "results": [...],
      "relaxation_applied": true/false,
      "relaxation_steps_applied": 1,
      "original_rating": 4.8,
      "final_rating": 4.2,
      "original_budget": 500.0,
      "final_budget": 800.0,
      "query_execution_ms": 0.55,
      "original_constraints": { ... },
      "final_constraints": { ... }
    }
    ```
* [src/ingestion.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/src/ingestion.py): Updated schema saving logic to automatically create case-insensitive indexes.
* [tests/test_filter_engine.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/tests/test_filter_engine.py): Implemented 11 test functions validating the filter engine's behaviors, metadata return formatting, and constraint compliance.

---

## 2. SQLite Database Indexes Created
To optimize performance and support scaling up to 100k+ restaurants, we configured the `location` column as `location TEXT COLLATE NOCASE` and created the following two standard indexes:
```sql
CREATE INDEX IF NOT EXISTS idx_restaurants_location 
ON restaurants(location);

CREATE INDEX IF NOT EXISTS idx_restaurants_filter 
ON restaurants(location, rating, cost);
```

---

## 3. Query Plan Verification
We ran `EXPLAIN QUERY PLAN` on the 5 benchmark queries to verify SQLite index usage:
* **Q1: Banashankari + Italian + Rating >= 4.0 + Budget <= 1500:** `SEARCH restaurants USING INDEX idx_restaurants_filter (location=? AND rating>?)`
* **Q2: Jayanagar + Biryani + Rating >= 4.2:** `SEARCH restaurants USING INDEX idx_restaurants_filter (location=? AND rating>?)`
* **Q3: Basavanagudi + Chinese + Budget <= 800:** `SEARCH restaurants USING INDEX idx_restaurants_filter (location=?)`
* **Q4: JP Nagar + Table Booking:** `SEARCH restaurants USING INDEX idx_restaurants_filter (location=?)`
* **Q5: Jayanagar Expensive High-End Dining:** `SEARCH restaurants USING INDEX idx_restaurants_filter (location=? AND rating>?)`

**Status: PASS** — SQLite performs rapid B-tree index searches using the standard indexes instead of sequential full-table scans.

---

## 4. Latency Comparison (Before vs. After Indexing)

| Query ID & Description | Latency Before Indexing (Full Scan) | Latency After Indexing (B-tree Search) | Performance Gain (Speedup) |
| :--- | :---: | :---: | :---: |
| **Q1:** Banashankari + Italian + Rating >= 4.0 + Budget <= 1500 | `1.48 ms` | `0.40 ms` | **3.71x** |
| **Q2:** Jayanagar + Biryani + Rating >= 4.2 | `1.89 ms` | `0.50 ms` | **3.81x** |
| **Q3:** Basavanagudi + Chinese + Budget <= 800 | `1.55 ms` | `0.48 ms` | **3.21x** |
| **Q4:** JP Nagar + Table Booking | `1.53 ms` | `0.56 ms` | **2.73x** |
| **Q5:** Jayanagar Expensive High-End Dining | `1.70 ms` | `0.64 ms` | **2.67x** |
| **Average Query Time** | **`1.63 ms`** | **`0.51 ms`** | **3.17x** |

---

## 5. Automated Tests
All 21 test cases (combining Phase 1 and Phase 2) passed successfully:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.0, pluggy-1.6.0
rootdir: C:\Users\palla\OneDrive\Desktop\Zomato milestone1
plugins: anyio-4.14.0
collected 21 items

tests\test_database.py ...                                               [ 14%]
tests\test_filter_engine.py .............                                [ 76%]
tests\test_ingestion.py .....                                            [100%]

============================= 21 passed in 0.78s ==============================
```
