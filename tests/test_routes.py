import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_notes(client):
    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data  # Проверяем наличие ключа "notes" в JSON-ответе
    assert isinstance(data["notes"], list)  # Проверяем, что "notes" - это список
    assert all(
        "id" in note and "title" in note for note in data["notes"]
    )  # Проверяем, что каждая заметка в списке имеет "id" и "title"
