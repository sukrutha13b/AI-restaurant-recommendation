from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from api.routes.recommendations import router as recommendations_router
from api.routes.llm_recommendations import router as llm_recommendations_router
from api.routes.metadata import router as metadata_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Restaurant Recommendation Service")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    app.include_router(recommendations_router)
    app.include_router(llm_recommendations_router)
    app.include_router(metadata_router)

    # Serve static files from the 'frontend' directory
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if os.path.exists(frontend_path):
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")

        @app.get("/")
        async def read_index():
            return FileResponse(os.path.join(frontend_path, "index.html"))

    return app


app = create_app()


