import asyncio

import httpx


async def _get_healthz():
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=5) as c:
        r = await c.get("/healthz")
        r.raise_for_status()
        return r.json()


def test_healthz_contract():
    data = asyncio.run(_get_healthz())
    assert data == {"status": "ok"}
