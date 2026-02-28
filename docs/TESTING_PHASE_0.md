# Phase 0 Testing Guide

## Automated tests (pytest)

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run the test suite from the project root:
   - `pytest`
3. Expected:
   - The `test_health_endpoint_returns_ok` test passes.

## Manual testing

1. Start the FastAPI app:
   - `uvicorn api.main:app --reload`
2. Open the browser at:
   - `http://127.0.0.1:8000/health`
3. Verify:
   - The response status is `200 OK`.
   - The JSON body is `{"status": "ok"}`.

