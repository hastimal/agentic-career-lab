"""Configuration settings for OpenCareer Agents."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google Cloud & Vertex AI settings
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    gemini_model: str = "gemini-1.5-flash"

    # Local Ollama & Gemma settings (Privacy Preserving)
    ollama_base_url: str = "http://localhost:11434"
    gemma_model: str = "gemma4:12b"

    # App Settings
    app_title: str = "OpenCareer Agents"
    debug: bool = False


settings = Settings()
