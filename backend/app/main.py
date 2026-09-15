import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.messages import router as messages_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.ship30 import router as ship30_router
from app.config.settings import settings
from app.db.database import check_database_connection, init_db

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s",
)
logger = logging.getLogger("lenny_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    yield


app = FastAPI(
    title="Lenny Growth Assistant",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        code = detail["code"]
        message = detail.get("message", "An error occurred.")
    else:
        code = "HTTP_ERROR"
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Invalid request body: {exc.errors()}",
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    msg = str(exc)
    code = "LLM_UNAVAILABLE" if "LLM_UNAVAILABLE" in msg else "INVALID_INPUT"
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": code,
                "message": msg.replace("LLM_UNAVAILABLE: ", ""),
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    msg = str(exc)
    code = "SERVICE_UNAVAILABLE"
    if "OLLAMA_UNAVAILABLE" in msg:
        code = "OLLAMA_UNAVAILABLE"
    elif "LLM_UNAVAILABLE" in msg:
        code = "LLM_UNAVAILABLE"
    elif "DATABASE_UNAVAILABLE" in msg:
        code = "DATABASE_UNAVAILABLE"

    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": code,
                "message": msg.replace("OLLAMA_UNAVAILABLE: ", "").replace("LLM_UNAVAILABLE: ", ""),
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(f"Unhandled exception [req:{request_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred.",
                "request_id": request_id,
            }
        },
    )


app.include_router(sessions_router)
app.include_router(messages_router)
app.include_router(ship30_router)
app.include_router(artifacts_router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "model": settings.ollama_model if settings.llm_provider == "ollama" else settings.anthropic_model,
    }


@app.get("/health/ready")
def readiness() -> dict:
    try:
        check_database_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"failed: {e}"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "provider": settings.llm_provider,
        "model": settings.ollama_model if settings.llm_provider == "ollama" else settings.anthropic_model,
    }