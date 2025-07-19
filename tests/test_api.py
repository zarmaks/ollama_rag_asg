from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_ask_and_history():
    """Test /ask endpoint and then /history endpoint."""
    # Test /ask endpoint
    res = client.post("/ask", json={"question": "anything"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data

    # Test /history endpoint
    hist = client.get("/history")
    assert hist.status_code == 200
    assert isinstance(hist.json(), list)


def test_ask_endpoint():
    """Test the /ask endpoint with a sample question."""
    response = client.post("/ask", json={"question": "What is CloudSphere Platform?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_history_endpoint():
    """Test the /history endpoint."""
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_history_with_limit():
    """Test the /history endpoint with a limit parameter."""
    response = client.get("/history?n=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_ask_invalid_json():
    """Test the /ask endpoint with invalid JSON."""
    response = client.post("/ask", json={"wrong_field": "test"})
    assert response.status_code == 422  # Validation error


def test_history_invalid_limit():
    """Test the /history endpoint with invalid limit."""
    response = client.get("/history?n=invalid")
    assert response.status_code == 422  # Validation error
