from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Restaurant Recommendation Service"
    environment: str = "development"

    # Gemini / LLM settings (placeholders for future phases)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

