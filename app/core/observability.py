"""
Observability helpers: structured logging, request/timing middleware, and an
optional Sentry hook (only enabled when SENTRY_DSN is configured).
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("cmo")


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging once, with a concise structured-ish format."""
    root = logging.getLogger()
    if getattr(setup_logging, "_configured", False):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.handlers = [handler]
    root.setLevel(level.upper())
    # Quiet noisy libraries.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    setup_logging._configured = True  # type: ignore[attr-defined]


def init_sentry() -> bool:
    """Initialise Sentry if SENTRY_DSN is set and the SDK is installed."""
    from app.core.config import settings

    dsn = (settings.SENTRY_DSN or "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk  # type: ignore

        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.1)
        logger.info("Sentry error tracking enabled.")
        return True
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("SENTRY_DSN set but Sentry init failed: %s", exc)
        return False


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id, log each request, and add timing headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed id=%s %s %s after %.1fms",
                request_id,
                request.method,
                request.url.path,
                elapsed,
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-ms"] = f"{elapsed:.1f}"
        logger.info(
            "request id=%s %s %s -> %s %.1fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response
