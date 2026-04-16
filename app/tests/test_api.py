from fastapi.testclient import TestClient

from src.main import build_app
from src.storage import MemoryStore


def make_client():
    return TestClient(build_app(storage=MemoryStore()))


def test_healthz():
    c = make_client()
    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_shorten_then_redirect():
    c = make_client()
    r = c.post("/shorten", json={"url": "https://example.com/a"})
    assert r.status_code == 200
    code = r.json()["code"]
    r2 = c.get(f"/r/{code}", follow_redirects=False)
    assert r2.status_code == 301
    assert r2.headers["location"].startswith("https://example.com")


def test_missing_code():
    c = make_client()
    assert c.get("/r/zzzzzzz").status_code == 404


def test_stats_increments():
    c = make_client()
    code = c.post("/shorten", json={"url": "https://a.test/"}).json()["code"]
    for _ in range(3):
        c.get(f"/r/{code}", follow_redirects=False)
    s = c.get(f"/stats/{code}").json()
    assert s["hits"] == 3


def test_cpu_endpoint():
    c = make_client()
    r = c.get("/cpu?rounds=100")
    assert r.status_code == 200
    assert r.json()["rounds"] == 100


def test_platform_header():
    c = make_client()
    r = c.get("/healthz")
    assert "x-platform" in r.headers
