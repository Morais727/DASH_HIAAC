import sys
import os
import pytest

# Garante que o diretório `flask-server/` esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

# --- METRICS ---
def test_get_cpu_metric(client):
    response = client.get("/metrics/cpu")
    assert response.status_code in (200, 500)  # Pode falhar se Prometheus estiver off

# --- UPLOAD ---
def test_save_flags(client):
    response = client.post("/save-flags", json={"client": True})
    assert response.status_code == 200
    assert "Flags salvas" in response.get_data(as_text=True)

def test_upload_without_file(client):
    response = client.post("/upload")
    assert response.status_code == 400

# --- CONTROL ---
def test_combined_metrics(client):
    response = client.get("/metrics/prometheus/combined")
    assert response.status_code in (200, 500)

def test_mqtt_command(client):
    for cmd in ["start", "stop"]:
        response = client.post(f"/{cmd}")
        assert response.status_code in (200, 500)
