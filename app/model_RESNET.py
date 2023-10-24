from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

# Chargement du modèle lors de l'initialisation
model = load_model('/Users/flavien/Desktop/Model_RESNET256_OC/resnet_model.h5')

# La liste des codes de catégorie
liste_prdtypecode = [10, 40, 50, 60, 1140, 1160, 1180, 1280, 1281, 1300,
                    1301, 1302, 1320, 1560, 1920, 1940, 2060, 2220, 2280,
                    2403, 2462, 2522, 2582, 2583, 2585, 2705, 2905]

liste_thématique = ['Livres_magazines','Jeux_vidéos','Jeux_vidéos','Jeux_vidéos',
            'Collections', 'Collections', 'Collections', 'Jeux_enfants',
            'Jeux_enfants', 'Jeux_vidéos', 'Jeux_enfants', 'Jeux_enfants',
            'Jeux_enfants', 'Mobilier_intérieur', 'Mobilier_intérieur', 'Alimentation',
            'Mobilier_intérieur', 'Animaux', 'Livres_magazines', 'Livres_magazines',
            'Jeux_vidéos', 'Papeterie', 'Mobilier_extérieur', 'Mobilier_extérieur',
            'Mobilier_extérieur', 'Livres_magazines', 'Jeux_vidéos']

# Création d'un dictionnaire pour associer chaque prdtypecode à sa thématique
mapping_prdtypecode_thematique = dict(zip(liste_prdtypecode, liste_thématique))

def prepare_image(image_file):
    # Charger l'image depuis l'objet UploadFile
    image = Image.open(image_file.file)

    # Assurer que l'image est en RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Redimensionner l'image à 224x224
    image = image.resize((224, 224))

    # Convertir l'image en array et normaliser les valeurs à [0,1]
    image_array = np.asarray(image) / 255.0

    # Etendre les dimensions pour correspondre à l'input du modèle
    image_ready = np.expand_dims(image_array, axis=0)

    return image_ready

def predict_category(image_file):
    image_ready = prepare_image(image_file)
    predictions = model.predict(image_ready)
    predicted_class = np.argmax(predictions, axis=1)[0]

    # Obtenir la catégorie et la thématique associée
    category = liste_prdtypecode[predicted_class]
    thematique = mapping_prdtypecode_thematique[category]

    return category, thematique


