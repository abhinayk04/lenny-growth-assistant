from fastapi import FastAPI

from app.api.routes.sessions import router as sessions_router
from app.db.database import check_database_connection


app = FastAPI(
    title="Lenny Growth Assistant",
    version="0.1.0",
)


app.include_router(sessions_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


@app.get("/health/ready")
def readiness() -> dict[str, str]:
    check_database_connection()

    return {
        "status": "ready",
    }