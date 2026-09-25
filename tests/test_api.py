import os

os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["TYPESAFE_API_KEY"] = "test-typesafe-key"

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ok"


def test_home_page():
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_static_css():
    with TestClient(app) as client:
        response = client.get("/static/styles.css")

        assert response.status_code == 200


def test_static_javascript():
    with TestClient(app) as client:
        response = client.get("/static/app.js")

        assert response.status_code == 200