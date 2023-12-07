from fastapi.testclient import TestClient
from authentification import app

client = TestClient(app)

def test_authenticate():
    response = client.post("/auth", auth=("test", "secret63"))
    assert response.status_code == 200
    assert "token" in response.json()
