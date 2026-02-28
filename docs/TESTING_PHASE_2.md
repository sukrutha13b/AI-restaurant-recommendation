# Phase 2 Testing Guide – Core Recommendation Engine

This guide covers both automated pytest tests and manual testing via the debug
API endpoint introduced in Phase 2.

---

## Automated Tests (pytest)

### Run all tests (from project root, `.venv` activated)

```bash
cd d:\Projects\Cursor_projects\AI-restaurant-recommendation
.venv\Scripts\activate
pytest tests/ -v
```

### Test modules

| Module | What it tests |
|---|---|
| `tests/core/test_preferences.py` | `UserPreferences` normalization (city, cuisines) and validation (rating, price, top_n bounds) |
| `tests/core/test_filters.py` | Individual filter functions and `apply_all_filters` composition |
| `tests/core/test_scoring.py` | Score weights (60/30/10), votes capping, and `rank_restaurants` ordering |
| `tests/core/test_pipeline.py` | End-to-end: top_n, filter combinations, empty results, ordering, immutability |

All Phase 0 and Phase 1 tests (`tests/test_health.py`, `tests/data/`) continue to pass unchanged.

---

## Manual Testing – Debug `/candidates` Endpoint

### Step 1 – Start the server

```bash
uvicorn api.main:app --reload
```

> **Note**: The first request to `/candidates` will trigger a one-time Hugging Face
> dataset download (cached after the first run).

### Step 2 – Open the interactive docs

Navigate to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The Swagger UI lets you try all parameters interactively.

---

### Step 3 – Test cases (curl)

#### Basic health check (regression)
```bash
curl http://127.0.0.1:8000/health
# Expected: {"status": "ok"}
```

#### No filters – top 5 by score
```bash
curl "http://127.0.0.1:8000/candidates?top_n=5"
```
Verify: 5 restaurants returned, `score` field populated, ordered descending.

#### City filter
```bash
curl "http://127.0.0.1:8000/candidates?city=Bangalore&top_n=5"
```
Verify: all returned restaurants have `city` containing "bangalore".

#### Rating filter
```bash
curl "http://127.0.0.1:8000/candidates?min_rating=4.5&top_n=5"
```
Verify: all returned restaurants have `rating >= 4.5`.

#### Price bucket filter
```bash
curl "http://127.0.0.1:8000/candidates?max_price_bucket=2&top_n=10"
```
Verify: all returned restaurants have `price_range` ≤ 2 (no nulls).

#### Cuisine filter
```bash
curl "http://127.0.0.1:8000/candidates?cuisines=North+Indian&top_n=5"
```
Verify: all returned restaurants have `"North Indian"` in their cuisines list.

#### Combined filters
```bash
curl "http://127.0.0.1:8000/candidates?city=Bangalore&min_rating=4.0&max_price_bucket=3&cuisines=North+Indian&top_n=5"
```
Verify: restaurants satisfy ALL four criteria, `count` matches `len(restaurants)`.

#### No-match scenario
```bash
curl "http://127.0.0.1:8000/candidates?city=Atlantis&min_rating=5.0"
```
Verify: `count == 0`, `restaurants == []`.

---

### What to look for in the response

```json
{
  "count": 5,
  "filters_applied": { "city": "Bangalore", ... },
  "restaurants": [
    {
      "id": "...",
      "name": "...",
      "city": "bangalore",
      "cuisines": ["North Indian"],
      "price_range": 2,
      "rating": 4.3,
      "votes": 1200,
      "score": 0.5892
    },
    ...
  ]
}
```

- `score` decreases monotonically from first to last restaurant.
- `filters_applied` echoes the parameters you sent.
- `count` equals `len(restaurants)`.
