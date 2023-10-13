import pandas as pd
import tensorflow as tf
import numpy as np
import itertools
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D,Input, Dropout, LSTM, Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import ResNet50
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from runbert import tokenize, bert_model_creation, compile_bert, train_bert, predict_bert
from transformers import BertTokenizer, TFBertModel


#(63) Resnet 50 avec couche de 256 neurones


#Ajouter module pre-processing 


# Charger les données d'entraînement
X_path = "/Users/flavien/Desktop/224_X_Train_4D/224_X_Train_4D.npy"
X_train = np.load(X_path)

# Charger le DataFrame
df_path = "/Users/flavien/Desktop/projet_RAKUTEN/DF/sorted_df.csv"
df = pd.read_csv(df_path)

# Prétraitement de la colonne "prdtypecode"
label_encoder = LabelEncoder()
df['prdtypecode'] = label_encoder.fit_transform(df['prdtypecode'])

# Prétraitement des données
y = df["prdtypecode"].values
y = to_categorical(y)  # Convertir les étiquettes en vecteurs one-hot
X_train, X_val, y_train, y_val = train_test_split(X_train, y, test_size = 0.2, random_state = 42)


#A modifier pour garder 256
param_dense = [64,128,256,512]
param_couches = ['oui','non']
# Générer toutes les combinaisons possibles
parameter_combinations = list(itertools.product(param_dense,param_couches))
# Liste des combinaisons déjà réalisées
combinaisons_realisees = [
   (64, 'oui'),(64, 'non'),(128,'oui'), (128, 'non'),(256, 'non'), (512, 'non')
    # Ajoutez les autres combinaisons déjà réalisées ici
]

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


for combination in parameter_combinations:
    unit1, couches = combination
    combination_name = f"{unit1}_{couches}"
    if combination in combinaisons_realisees:
        print(f"Combinaison déjà réalisée : {combination_name}")
        continue
    print(f"Combinaison en cours : {combination_name}")

    # Création du modèle ResNet-50
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=X_train.shape[1:])

    # Ajout des couches supplémentaires
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    if couches == 'oui':
        x = Dense(unit1, activation = "relu")(x)
        predictions = Dense(27, activation = "softmax")(x)
    else:
        predictions = Dense(27, activation = "softmax")(x)

    model = Model(inputs = base_model.input, outputs = predictions)

    # Geler les poids du modèle de base
    for layer in base_model.layers:
        layer.trainable = False

    # Compiler le modèle
    model.compile(loss='categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

    # Entraînement du modèle avec augmentation de données
    batch_size = 32
    steps_per_epoch = len(X_train) // batch_size

    history = model.fit(
        X_train, y_train,
        batch_size = batch_size,
        steps_per_epoch = steps_per_epoch,
        validation_data = (X_val, y_val),
        epochs = 5
    )

    # Sauvegarde du modèle
    model.save(f"/Users/flavien/Desktop/projet_RAKUTEN/CNN_ResNet_sans_distortion/resnet_ss_augment_{str(combination_name)}.h5")

    # Prédire les classes des données de validation
    predictions = model.predict(X_val)
    predicted_labels = np.argmax(predictions, axis = 1)

    
