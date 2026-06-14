import asyncio

from app.services.jobs import JobManager


def test_job_succeeds():
    async def scenario():
        mgr = JobManager()

        async def work():
            await asyncio.sleep(0.01)
            return {"value": 42}

        job = mgr.create("test", work, owner_id=7)
        assert job.status in ("pending", "running")
        await asyncio.sleep(0.05)
        fetched = mgr.get(job.id)
        return fetched

    job = asyncio.run(scenario())
    assert job is not None
    assert job.status == "succeeded"
    assert job.result == {"value": 42}
    assert job.owner_id == 7


def test_job_failure_is_captured():
    async def scenario():
        mgr = JobManager()

        async def work():
            raise ValueError("boom")

        job = mgr.create("test", work)
        await asyncio.sleep(0.05)
        return mgr.get(job.id)

    job = asyncio.run(scenario())
    assert job.status == "failed"
    assert "boom" in (job.error or "")
