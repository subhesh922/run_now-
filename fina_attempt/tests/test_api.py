# tests/test_api.py
import os, requests, pytest

API = os.getenv("DFMEA_API_URL", "http://localhost:8000/health")

def test_health_if_backend_running():
    try:
        r = requests.get(API, timeout=3)
    except Exception:
        pytest.skip("Backend not running; skipping /health test")
    assert r.status_code == 200
    assert r.json().get("ok") is True
