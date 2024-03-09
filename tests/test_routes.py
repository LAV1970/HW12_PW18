import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_notes(client):
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == {"message": "Get all notes"}
