import requests

"""
Tests de l'authentification avec l'API Users-DB.

Ce module contient des fonctions de test pour vérifier le comportement de l'API Users-DB
lors de l'authentification avec des identifiants valides et invalides.

Fonctions de test :
    - test_authenticate_valid_credentials: Vérifie si l'authentification avec des identifiants valides
      renvoie un code de statut 200 et inclut un jeton (token) dans la réponse JSON.
    - test_authenticate_invalid_credentials: Vérifie si l'authentification avec des identifiants invalides
      renvoie un code de statut 401.

Exemple d'utilisation :
    - Exécuter ces fonctions de test à l'aide d'un framework de test comme pytest.

Note :
    - Assurez-vous que l'API Users-DB est accessible à l'URL spécifiée dans les fonctions de test.
    - Les identifiants utilisés dans les tests sont des exemples, assurez-vous de les ajuster en fonction
      de la configuration réelle de l'API.
    - Ces tests dépendent de l'état et de la configuration de l'API Users-DB, assurez-vous que l'API
      est opérationnelle avant d'exécuter ces tests.

"""

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





