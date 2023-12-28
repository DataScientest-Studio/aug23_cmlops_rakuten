import mlflow
import mlflow.keras
from transformers import BertTokenizer, TFBertModel
from keras.applications.resnet50 import ResNet50
from keras.layers import Input, Flatten, Concatenate, Dense
from keras.models import Model
from keras.callbacks import ModelCheckpoint
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Configuration de MLflow pour le suivi des expériences
mlflow.set_tracking_uri("http://localhost:5001")

def preprocess_text(text, max_length=128):
    """
    Prétraitement des textes en utilisant un tokenizer BERT.
    """
    tokens = tokenizer.encode_plus(text, add_special_tokens=True, max_length=max_length, return_tensors='tf', padding='max_length', truncation=True)["input_ids"]
    return tokens.numpy().squeeze()

def encode_labels(labels):
    """
    Encode les étiquettes textuelles en étiquettes numériques.
    """
    return label_encoder.fit_transform(labels)

def one_hot_encode(encoded_labels, classes_count):
    """
    Convertit les étiquettes numériques en codage one-hot.
    """
    return tf.keras.utils.to_categorical(encoded_labels, num_classes=classes_count)

# Initialisation des modèles et des tokenizers
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')

# Chargement et prétraitement des données
df = pd.read_csv("./Drive/CSV_Rakuten_MLOPS.csv")
texts_data = np.array([preprocess_text(text) for text in df['description_complete'].values], dtype=np.int32)
images_data = np.load("./Drive/matrice_photo_4D.npy")

# Prétraitement des images avec ResNet50
base_model = ResNet50(weights='imagenet', include_top=False)
for layer in base_model.layers:
    layer.trainable = False
image_features = base_model.predict(images_data)

# Création (ou récupération) d'une expérience MLflow
experiment_name = "Model_fusion_1"
try:
    experiment_id = mlflow.create_experiment(experiment_name)
except Exception as e:
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id

# Début du suivi d'expérience MLflow
with mlflow.start_run(experiment_id=experiment_id) as run:
    model_version = run.info.run_id
    model_name = f"combined_model_{model_version}"

    # Fusion des modèles de traitement d'images et de texte
    image_input = Input(shape=(7, 7, 2048), name="image_input")
    text_input = Input(shape=(128,), dtype=tf.int32, name="text_input")
    combined = Concatenate()([Flatten()(image_input), bert_model(text_input)[1]])
    combined_model = Model(inputs=[image_input, text_input], outputs=Dense(27, activation='softmax')(Dense(128, activation='relu')(combined)))
    combined_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Enregistrement des paramètres du modèle avec MLflow
    mlflow.log_param("optimizer", "adam")
    mlflow.log_param("loss_function", "categorical_crossentropy")
    mlflow.log_param("batch_size", 32)
    mlflow.log_param("epochs", 1)

    # Préparation des étiquettes et séparation des données
    label_encoder = LabelEncoder()
    labels_onehot = one_hot_encode(encode_labels(df['prdtypecode']), 27)
    train_texts, val_texts, train_images, val_images, train_labels, val_labels = train_test_split(texts_data, image_features, labels_onehot, test_size=0.2)

    # Entraînement du modèle avec suivi des métriques
    history = combined_model.fit({"image_input": train_images, "text_input": train_texts}, train_labels, validation_data=({"image_input": val_images, "text_input": val_texts}, val_labels), epochs=1, batch_size=32, callbacks=[ModelCheckpoint("/Users/flavien/Desktop/Fusion/weights-epoch{epoch:02d}-loss{val_loss:.2f}.h5", monitor='val_loss', verbose=1, save_best_only=False, save_weights_only=False, mode='auto', save_freq='epoch')])

    # Enregistrement des métriques d'entraînement avec MLflow
    for key, value in history.history.items():
        mlflow.log_metric(key, value[-1])

    # Sauvegarde du modèle entraîné avec MLflow
    mlflow.keras.log_model(combined_model, model_name)

    # Sauvegarde du modèle complet fusionné au format HDF5 (.h5)
    combined_model.save("/Users/flavien/Desktop/combined_model_trained_after_resume.h5")

    # Fin du suivi d'expérience MLflow
    mlflow.end_run()

