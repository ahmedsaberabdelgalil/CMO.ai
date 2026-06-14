import uvicorn
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.observability import (
    RequestContextMiddleware,
    init_sentry,
    setup_logging,
)

from app.core.config import settings

setup_logging(settings.LOG_LEVEL)
init_sentry()

app = FastAPI(
    title="CMO.ai API",
    description="AI-powered marketing platform API",
    version="1.0.0",
)

# ── Observability ─────────────────────────────────────────────
app.add_middleware(RequestContextMiddleware)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")

# Generated images (image agent writes to uploads/images/)
_uploads = Path("uploads")
_uploads.mkdir(parents=True, exist_ok=True)
(_uploads / "images").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads)), name="uploads")


'''
Easy Auth 
username: ahmedsaber@example.com
password: SecurePassword123!
ahmedsaber@test.com

'''


# ── Health checks ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe — process is up."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe — verifies database connectivity."""
    from app.db.session import async_engine

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "error", "detail": str(exc)},
        )
