import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_text_without_user_id(async_client: AsyncClient):
    r = await async_client.post("/api/v1/analysis/text", json={"text": "hello from test"})
    assert r.status_code != 422
    # 200/201/202/4xx are acceptable, but NOT 422 for missing user_id