"""测试 /health 端点。"""


async def test_health_returns_200(client):
    """验证健康检查端点返回 200 和正确的字段。"""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "database" in data
    assert "redis" in data
    assert data["database"] in ("connected", "disconnected")
    assert data["redis"] in ("connected", "disconnected")
