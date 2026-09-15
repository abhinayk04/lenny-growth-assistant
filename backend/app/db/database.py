from pathlib import Path
from sqlalchemy import create_engine, text

from app.config.settings import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


def check_database_connection() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True


def init_db() -> None:
    """Ensure database schema tables are created."""
    schema_path = Path(__file__).parent / "schema.sql"
    if schema_path.exists():
        sql = schema_path.read_text(encoding="utf-8")
        with engine.begin() as connection:
            connection.execute(text(sql))
