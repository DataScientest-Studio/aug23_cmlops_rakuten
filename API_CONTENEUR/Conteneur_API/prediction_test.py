import pytest
from script_de_prediction import predict, liste_prdtypecode, liste_thématique
import requests

def download_model(file_id, destination):
    URL = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(URL)
    open(destination, 'wb').write(response.content)

def test_predict():
    # Assurez-vous que le modèle est téléchargé
    model_file = 'models/combined_model_trained_after_resume.h5'
    download_model('1LgATG-amQRVQzXPi7MWaCgLhKP03VAL1', model_file)

    # Données de test
    test_text = "voiture"
    test_image_path = "photo_test.jpg"

    # Appel de la fonction de prédiction
    prdtypecode, thematique = predict(test_text, test_image_path)

    # Assertions pour vérifier si la fonction renvoie les résultats attendus
    assert prdtypecode in liste_prdtypecode
    assert thematique in liste_thématique
