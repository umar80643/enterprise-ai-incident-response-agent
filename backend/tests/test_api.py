from fastapi.testclient import TestClient
from app.main import app
def test_health():
    r=TestClient(app).get("/health")
    assert r.status_code==200 and r.json()["status"]=="ok"
def test_auth_required():
    r=TestClient(app).post("/api/v1/repositories/index",json={"name":"x","path":".","branch":"main"})
    assert r.status_code==401
