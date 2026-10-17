from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    retriever_mode: Literal["fake", "dense"] = "fake"
    llm_mode: Literal["stub", "openai"] = "stub"
    database_url: str | None = None
    openai_api_key: SecretStr | None = None
    # Comma-separated. A str because pydantic-settings reads lists as JSON
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
