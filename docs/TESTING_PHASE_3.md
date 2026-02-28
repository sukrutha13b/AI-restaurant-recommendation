# Phase 3 Manual Testing Guide (Gemini LLM Integration)

This guide walks you through testing the new intelligence layer using the official Gemini API (`google-genai`).

## 1. Environment Setup

To test the LLM integration, you need a Gemini API Key.
1. Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Open the `.env` file in the project root.
3. Add your key:
```env
# .env inside project root
environment=development
gemini_api_key="AIzaSyYourRealKeyHere..."
gemini_model="gemini-2.5-flash"
```

## 2. Server Restart

Because we installed new dependencies (`google-genai` and `pydantic-settings`), you must restart your Uvicorn server:

```powershell
.venv\Scripts\activate
# Stop the old server with CTRL+C, then restart:
uvicorn api.main:app --reload --port 8000
```

## 3. Testing the Endpoint

We created a new `POST /recommendations` endpoint. You can test it best via the interactive Swagger UI.

1. Open http://127.0.0.1:8000/docs
2. Expand the `POST /recommendations` section and click **Try it out**.
3. Paste the following JSON request body:

### Scenario A: Strict Filters
```json
{
  "cuisines": ["Mexican"],
  "min_rating": 4.0,
  "top_n": 3
}
```

**Expected Result:**
The response should contain 3 restaurants. Crucially, look at the new `explanation` and `llm_score` fields on each restaurant. You should see a tailored 1-3 sentence explanation directly mentioning "Mexican" food and the high rating.

### Scenario B: General Quality (No Hard Filters)
```json
{
  "top_n": 3
}
```

**Expected Result:**
The system will pull the top 15 statistically best restaurants across the whole dataset, feed them to Gemini, and Gemini will pick the 3 that sound most like fine-dining or romantic spots, providing an explanation for why they fit an anniversary.

### Scenario C: Fallback Test (Missing Context)
```json
{
  "city": "Bangalore",
  "top_n": 5
}
```

**Expected Result:**
If `context_description` is omitted (or if the LLM API fails), the pipeline safely falls back to the deterministic output from Phase 2 (score descending). `explanation` and `llm_score` will be `null`.

## Troubleshooting

- **500 Error / Crash:** Check the Uvicorn terminal logs. If it says `gemini_api_key` is missing, ensure your `.env` file is set up correctly in the root directory.
- **No explanations?** If `explanation` is null despite providing a context, check the terminal logs for warnings like `LLM re-ranking failed`. This usually means the API key is invalid or you hit a rate limit.
