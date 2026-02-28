## AI Restaurant Recommendation Service – Architecture (FastAPI + Gemini)

### 1. High-Level Overview

- **Goal**: Service that takes user preferences (price, place, rating, cuisine), uses the Zomato dataset from Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`), calls Gemini, and returns clear restaurant recommendations.
- **Backend**: Python + **FastAPI**
- **LLM**: **Google Gemini** (via Gemini API / Vertex AI, configurable)
- **Data Source**: Hugging Face dataset above
- **Testing**: **pytest** plus explicit **manual testing** steps per phase

---

### 2. Core Components

- **API Layer (`api/`)**
  - FastAPI app, request/response schemas, routing.
  - Endpoints:
    - `GET /health`
    - `POST /recommendations` (future)
    - Optional: `GET /metadata/filters` (future).

- **Core Recommendation Engine (`core/`)**
  - Preference normalization.
  - Rule-based filtering and scoring.
  - Orchestration of candidate selection and (later) LLM re-ranking.

- **Data Layer (`data/`)**
  - Ingestion of Hugging Face dataset.
  - Internal restaurant data model and query utilities.

- **LLM Orchestrator (`llm/`)**
  - Prompt construction and Gemini client.
  - Re-ranking and explanation generation.
  - Output validation and safety checks.

- **Configuration (`config/`)**
  - Centralized settings via Pydantic `BaseSettings`.
  - Handles environment, Gemini API configuration, limits.

- **Tests (`tests/`)**
  - pytest-based unit and integration tests.

- **Docs & Scripts (`docs/`, `scripts/`)**
  - Architecture and testing docs, helper scripts.

---

### 3. Project Phases (with Testing)

#### Phase 0 – Project Setup (IMPLEMENTED)

- **Goals**
  - Initialize FastAPI project skeleton and core folders.
  - Set up requirement management, basic config, and health check endpoint.
  - Configure pytest and simple automated + manual tests.

- **Key Tasks**
  - Create base structure:
    - `api/`, `core/`, `data/`, `llm/`, `config/`, `tests/`, `docs/`, `scripts/`.
  - Add `requirements.txt` with:
    - `fastapi`, `uvicorn[standard]`, `httpx`, `python-dotenv`, `datasets`, `pytest`, `pytest-asyncio`.
  - Implement FastAPI app in `api/main.py` with `GET /health`.
  - Add `config/settings.py` for app and Gemini-related settings (placeholders).
  - Add pytest test for `/health`.
  - Document Phase 0 testing in `docs/TESTING_PHASE_0.md`.

- **Testing**
  - **pytest**
    - `tests/test_health.py` verifies `/health` returns 200 and `{"status": "ok"}`.
  - **Manual**
    - Run app via `uvicorn api.main:app --reload`.
    - Hit `/health` in browser or via `curl` and verify status and body.

#### Phase 1 – Data Ingestion & Modeling

- **Goals**
  - Load and normalize the Zomato dataset.

- **Key Tasks**
  - Implement dataset loader for `ManikaSaini/zomato-restaurant-recommendation`.
  - Normalize schema and expose simple query functions.

- **Testing**
  - **pytest**: tests for loader behavior and repository queries (using fixtures).
  - **Manual**: temporary endpoint or script to inspect sample restaurants and filters.

#### Phase 2 – Core Recommendation Engine (Non-LLM)

- **Goals**
  - Build deterministic recommendation pipeline without Gemini.

- **Key Tasks**
  - User preference normalization and validation.
  - Hard filters (location, price, rating) and scoring logic.
  - Pipeline to return top-N candidate restaurants.

- **Testing**
  - **pytest**: unit tests for preferences, filters, scoring, and pipeline consistency.
  - **Manual**: debug endpoint returning raw candidate lists to inspect behavior.

#### Phase 3 – Gemini LLM Orchestration & Integration

- **Goals**
  - Integrate Gemini for re-ranking and explanations.

- **Key Tasks**
  - Implement Gemini client, prompt templates, and JSON output parsing.
  - Integrate into recommendation pipeline to augment ranking and add explanations.
  - Add fallbacks for LLM failures.

- **Testing**
  - **pytest**: mock-based tests for client wrapper, prompts, and parser edge cases.
  - **Manual**: live tests in dev with realistic user queries and evaluation of explanations.

#### Phase 4 – API Layer & Minimal UI

- **Goals**
  - Finalize external API and (optionally) minimal web UI.

- **Key Tasks**
  - Implement `POST /recommendations` and any metadata endpoints.
  - Optional basic front-end for interactive use.

- **Testing**
  - **pytest**: API tests via FastAPI `TestClient` (happy path, validation errors, LLM failures).
  - **Manual**: Postman/curl and UI-based journeys with representative scenarios.

#### Phase 5 – Observability, Performance & Cost Control

- **Goals**
  - Add logging, metrics, and performance/cost controls.

- **Key Tasks**
  - Structured logging, request tracing, and latency metrics.
  - Track LLM token usage and apply rate/usage limits as needed.
  - Implement caching and basic performance optimizations.

- **Testing**
  - **pytest**: tests for logging hooks, metrics emission, and caching behavior.
  - **Manual**: light load tests and inspection of logs/metrics dashboards.

#### Phase 6 – Hardening & Extensions

- **Goals**
  - Improve robustness and add advanced features.

- **Possible Extensions**
  - User personalization and history-aware recommendations.
  - Vector-based retrieval for free-text preferences.
  - Multi-city or geo-aware scoring.
  - Multiple Gemini models depending on latency/cost requirements.

- **Testing**
  - **pytest**: new suites per feature, with regression coverage.
  - **Manual**: scenario-based tests focusing on new capabilities.

---

### 4. Folder Structure (Current & Planned)

- `api/` – FastAPI app and routes.
- `core/` – recommendation engine and business logic.
- `data/` – dataset ingestion and repository utilities.
- `llm/` – Gemini client, prompts, and parsers.
- `config/` – application and environment configuration.
- `tests/` – pytest test suites.
- `docs/` – architecture and testing guides.
- `scripts/` – helper scripts (e.g., data exploration).
- `requirements.txt` – Python dependencies.
- `ARCHITECTURE.md` – this document.
- `README.md` – project overview and getting started.

