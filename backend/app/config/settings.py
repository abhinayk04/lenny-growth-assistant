import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://lenny:lenny_dev_password@localhost:5432/lenny",
    )

    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    ollama_base_url: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")


settings = Settings()
