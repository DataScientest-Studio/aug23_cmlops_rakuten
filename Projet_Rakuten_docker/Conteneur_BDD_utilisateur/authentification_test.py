import requests

def test_authenticate_valid_credentials():
    url = "http://users-db:8001/auth"
    response = requests.post(url, auth=('admin', 'admin63'))
    assert response.status_code == 200
    assert "token" in response.json()

def test_authenticate_invalid_credentials():
    url = "http://users-db:8001/auth"
    response = requests.post(url, auth=('admin', 'wrongpassword'))
    assert response.status_code == 401
    # Autres assertions peuvent être ajoutées selon le besoin





