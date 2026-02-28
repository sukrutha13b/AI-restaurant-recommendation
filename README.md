# AI Restaurant Recommendation Service

AI-powered restaurant recommendation service built with **FastAPI** and **Gemini**, using the Zomato dataset.

This project implements a multi-phase recommendation system featuring statistical ranking, LLM-based re-ranking, and advanced filtering.

## Features

- **Multi-City Search**: Search for restaurants across multiple cities simultaneously.
- **AI Re-ranking**: Uses Gemini (Flash or Pro) to provide personalized recommendations and explanations.
- **Caching Layer**: 
  - Shared memory cache for sub-millisecond dataset access.
  - Persistent disk cache for LLM responses to reduce latency and cost.
- **FastAPI Backend**: Modern, type-safe API with automatic OpenAPI documentation.
- **Dynamic Metadata**: Endpoints to discover available cities, cuisines, and LLM models.

## Tech Stack

- Python 3.11+
- FastAPI & Uvicorn
- Google Gemini API (`google-genai`)
- Diskcache (Persistent LLM cache)
- pytest (Comprehensive test suite)

## Getting Started

### 1. Setup Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 2. Configure API Keys

Create a `.env` file from `.env.example`:
```bash
GEMINI_API_KEY=your_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit UI

We provide a beautiful, interactive frontend using Streamlit. To launch it:
```bash
streamlit run streamlit_app.py
```
This will open the web interface in your default browser (usually at `http://localhost:8501`).

### 5. Run the Backend API (Optional)

If you need programmatic access, you can run the FastAPI server:
```bash
uvicorn api.main:app --reload
```
Then visit:
- `http://127.0.0.1:8000/docs` – Interactive API documentation.
- `http://127.0.0.1:8000/metadata/filters` – Discover available cities and cuisines.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the detailed phase breakdown and design patterns.
