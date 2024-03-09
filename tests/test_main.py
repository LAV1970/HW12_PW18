# tests/test_main.py
from fastapi.testclient import TestClient
from main import app


def test_read_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_read_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_read_about():
    client = TestClient(app)
    response = client.get("/about")
    assert response.status_code == 200
    assert response.json() == {"message": "About page"}


def test_create_note():
    client = TestClient(app)
    response = client.post(
        "/create_note", json={"title": "Test Note", "content": "Test Content"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Note created successfully"}


def test_invalid_request():
    client = TestClient(app)
    response = client.get("/nonexistent_route")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
