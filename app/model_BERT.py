import re
import numpy as np
import tensorflow as tf
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import BertTokenizer, TFBertModel

#  nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Charger le modèle BERT
model_bert = tf.keras.models.load_model('/Users/flavien/Desktop/Model_BERT128_OC/Bert_model.h5', custom_objects={'TFBertModel': TFBertModel})

# Définition des stopwords pour le français, l'anglais et l'allemand
stopwords_fr = set(stopwords.words('french'))
stopwords_en = set(stopwords.words('english'))
stopwords_de = set(stopwords.words('german'))

# Fonction de prétraitement des textes
def preprocess_text(text):
    if isinstance(text, str):
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\b\w{1,2}\b', '', text)
        text = re.sub(r'\b(cm|mm|kg|g|l|ml|oz|lb|in)\b', '', text)
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
        text = re.sub(r'\d{1,2}-\d{1,2}-\d{2,4}', '', text)
        text = re.sub(r'\d{1,2}\s+\w+\s+\d{2,4}', '', text)
        text = re.sub(r'\d+', '', text)
        text = text.lower()
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.lower() not in stopwords_fr and word.lower() not in stopwords_en and word.lower() not in stopwords_de]
        stemmer = SnowballStemmer('french')
        tokens = [stemmer.stem(word) for word in tokens]
        preprocessed_text = ' '.join(tokens)
        return preprocessed_text
    else:
        return ""

# Fonction pour prédire la catégorie d'un texte en utilisant le modèle BERT
def modele_bert(text):
    text_preprocessed = preprocess_text(text)
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    X_tokens = tokenizer.encode_plus(text_preprocessed, truncation=True, padding='max_length', max_length=128, return_tensors='tf')
    X_tokens_input_ids = X_tokens['input_ids']
    X_tokens_attention_mask = X_tokens['attention_mask']
    pred_bert = model_bert.predict([X_tokens_input_ids, X_tokens_attention_mask])
    predicted_labels = np.argmax(pred_bert, axis=-1)
    return predicted_labels[0]

def convert_prediction_to_thematique_and_code(prediction):
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

    if 0 <= prediction < len(liste_prdtypecode):
        prd_type_code = liste_prdtypecode[prediction]
        thématique = liste_thématique[prediction]
        return prd_type_code, thématique
    else:
        raise ValueError(f"Prediction {prediction} is out of expected range.")