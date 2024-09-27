from fastapi.testclient import TestClient
from api import app

CLIENT = TestClient(app)

def test_home_endpoint():
    response = CLIENT.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}