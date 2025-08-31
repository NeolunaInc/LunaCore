import os

import httpx
import pytest


@pytest.mark.asyncio
async def test_healthz_contract():
    """Test healthz endpoint contract."""
    healthz_url = os.getenv("LUNACORE_HEALTHZ_URL")

    if healthz_url:
        # Use external URL
        async with httpx.AsyncClient(base_url=healthz_url, timeout=5) as client:
            response = await client.get("/healthz")
    else:
        # Use in-process ASGI app
        try:
            from orchestrator.app import app

            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/healthz")
        except ImportError:
            pytest.skip("No ASGI app available and no LUNACORE_HEALTHZ_URL set")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
