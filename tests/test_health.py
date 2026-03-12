"""Tests for /api/v1/ health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
