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


def test_get_single_note(client):
    response = client.get("/notes/1")  # Предполагаем, что есть заметка с id=1
    assert response.status_code == 200
    data = response.json()
    assert (
        "id" in data and "title" in data
    )  # Проверяем, что в ответе есть "id" и "title"


def test_get_notes_with_query_params(client):
    response = client.get(
        "/notes?limit=10&offset=0"
    )  # Предполагаем, что есть 10 заметок
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) == 10  # Проверяем, что вернулось ровно 10 заметок
