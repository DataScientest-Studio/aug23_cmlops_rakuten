from keras.models import load_model
from transformers import BertTokenizer, TFBertModel
from keras.applications.resnet50 import preprocess_input, ResNet50
from PIL import Image
import numpy as np
import os
import json
import csv

# Charger le tokenizer BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

# Charger le modèle ResNet50 pour l'extraction des caractéristiques
base_model = ResNet50(weights='imagenet', include_top=False)

def preprocess_text(text, max_length=128):
    """
    Prétraite un texte pour qu'il soit adapté à un modèle BERT.

    Args:
        text (str): Le texte à traiter.
        max_length (int, optional): Longueur maximale du texte traité. Par défaut à 128.

    Returns:
        numpy.ndarray: Tableau numpy contenant le texte prétraité.
    """
    tokens = tokenizer.encode_plus(text, 
                                   add_special_tokens=True,
                                   max_length=max_length,
                                   return_tensors='tf',
                                   padding='max_length', 
                                   truncation=True)["input_ids"]
    return tokens.numpy().squeeze()

def preprocess_image(image_path):
    """
    Prétraite une image pour qu'elle soit adaptée à un modèle ResNet50.

    Args:
        image_path (str): Chemin de l'image à traiter.

    Returns:
        numpy.ndarray: Tableau numpy contenant les caractéristiques de l'image extraites par ResNet50.
    """
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img)
    img_array = preprocess_input(img_array) 
    img_array = np.expand_dims(img_array, 0)
    # Transformez l'image en utilisant ResNet50 pour obtenir les caractéristiques
    features = base_model.predict(img_array)
    return features


def preprocess_image_for_display(image_path):
    """
    Prétraite une image pour qu'elle soit adaptée à l'affichage et retourne l'image redimensionnée sous forme de matrice 4D (1, 224, 224, 3).

    Args:
        image_path (str): Chemin de l'image à traiter.

    Returns:
        numpy.ndarray: Tableau numpy contenant l'image redimensionnée sous forme de matrice 4D (1, 224, 224, 3).
    """
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img)
    preprocessed_img_array = preprocess_input(img_array)
    # Ajoutez une dimension pour obtenir la forme (1, 224, 224, 3)
    preprocessed_img_array = np.expand_dims(preprocessed_img_array, axis=0)
    return preprocessed_img_array






# Charger le modèle fusionné
combined_model_path = "/app/drive/combined_model_trained_after_resume.h5"
combined_model = load_model(combined_model_path, custom_objects={'TFBertModel': TFBertModel})

# Liste des prdtypecode et thématiques
liste_prdtypecode = [10, 40, 50, 60, 1140, 1160, 1180, 1280, 1281, 1300,
                     1301, 1302, 1320, 1560, 1920, 1940, 2060, 2220, 2280,
                     2403, 2462, 2522, 2582, 2583, 2585, 2705, 2905]

liste_thématique = ['Livres_magazines','Jeux_vidéos','Jeux_vidéos','Jeux_vidéos',
                    'Collections', 'Collections', 'Collections', 'Jeux_enfants',
                    'Jeux_enfants', 'Jeux_vidéos', 'Jeux_enfants', 'Jeux_enfants',
                    'Jeux_enfants', 'Mobilier_intérieur', 'Mobilier_intérieur', 
                    'Alimentation', 'Mobilier_intérieur', 'Animaux', 'Livres_magazines',
                    'Livres_magazines', 'Jeux_vidéos', 'Papeterie', 'Mobilier_extérieur', 
                    'Mobilier_extérieur', 'Mobilier_extérieur', 'Livres_magazines', 'Jeux_vidéos']

def predict(text, image_path):
    """
    Prédit le code de type de produit (prdtypecode) et la thématique en fonction d'un texte et d'une image.

    Cette fonction utilise un modèle de fusion qui combine BERT pour l'analyse de texte et ResNet50 pour l'analyse d'images.

    Args:
        text (str): Texte à analyser.
        image_path (str): Chemin de l'image à analyser.

    Returns:
        tuple: Un tuple contenant le prdtypecode et la thématique prédits.
    """
    text_data = preprocess_text(text)
    image_data = preprocess_image(image_path)
    
    predictions = combined_model.predict({"text_input": np.array([text_data]), "image_input": image_data})
    
    predicted_index = np.argmax(predictions, axis=1)[0]
    
    return liste_prdtypecode[predicted_index], liste_thématique[predicted_index]




