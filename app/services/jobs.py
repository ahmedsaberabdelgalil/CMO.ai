"""
Lightweight in-process async job manager.

Long-running agent work (image / video generation via Runway) can exceed a
comfortable request timeout. These helpers let an endpoint kick off the work as
a background asyncio task and return immediately with a job id the client can
poll.

Notes / limitations:
- State lives in-process, so it is per-worker. For multi-worker / multi-instance
  deployments swap this for Redis/RQ/Celery — the API surface (create/get) is
  intentionally small to make that migration easy.
- Finished jobs are kept for a short TTL and then garbage-collected.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

JobStatus = str  # "pending" | "running" | "succeeded" | "failed"

_RESULT_TTL_SECONDS = 60 * 30  # keep finished jobs for 30 minutes


@dataclass
class Job:
    id: str
    kind: str
    owner_id: int | None
    status: JobStatus = "pending"
    result: Any = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "job_id": self.id,
            "kind": self.kind,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def _gc(self) -> None:
        now = time.time()
        stale = [
            jid
            for jid, job in self._jobs.items()
            if job.status in ("succeeded", "failed")
            and now - job.updated_at > _RESULT_TTL_SECONDS
        ]
        for jid in stale:
            self._jobs.pop(jid, None)
            self._tasks.pop(jid, None)

    def create(
        self,
        kind: str,
        coro_factory: Callable[[], Awaitable[Any]],
        owner_id: int | None = None,
    ) -> Job:
        """Register a job and start running it in the background."""
        self._gc()
        job = Job(id=uuid.uuid4().hex, kind=kind, owner_id=owner_id)
        self._jobs[job.id] = job

        async def _runner() -> None:
            job.status = "running"
            job.updated_at = time.time()
            try:
                job.result = await coro_factory()
                job.status = "succeeded"
            except Exception as exc:  # noqa: BLE001 - surfaced via job.error
                job.error = str(exc)
                job.status = "failed"
            finally:
                job.updated_at = time.time()

        self._tasks[job.id] = asyncio.create_task(_runner())
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)


# Shared singleton used by the API routes.
job_manager = JobManager()
