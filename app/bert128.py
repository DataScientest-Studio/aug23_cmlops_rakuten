#(58) RNN - BERT 128 neurones
# Chargement du tokenizer BERT
import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D,Input, Dropout, LSTM, Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from runbert import tokenize, bert_model_creation, compile_bert, train_bert, predict_bert
from transformers import BertTokenizer, TFBertModel


#Ajouter module pre-processing 

df = pd.read_csv(r'C:\Users\PatriciaWintrebert\Projects\Rakuten MLOps\MLOps_API\data\Df_Encoded.csv', index_col=0)

x = df["description_complete_prétraite"]
y = df["prdtypecode"]
# Encoder les labels en valeurs numériques
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
# Diviser les données en ensembles d'entraînement et de test
x_train, x_test, y_train, y_test = train_test_split(x, y_encoded, test_size = 0.2, random_state = 42)

tokenizer = None
try:
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
except OSError as e:
    print("Erreur lors du chargement des fichiers du modèle BERT :", str(e))
    print("Veuillez vous assurer que les fichiers du modèle BERT sont téléchargés.")
if tokenizer:
    # Tokenisation des textes d'entraînement
    x_train_tokens = tokenizer.batch_encode_plus(
        x_train,
        truncation = True,
        padding = True,
        max_length = 256,
        return_tensors = 'tf'
    )
    x_train_input_ids = x_train_tokens['input_ids']
    x_train_attention_mask = x_train_tokens['attention_mask']
    # Tokenisation des textes de test
    x_test_tokens = tokenizer.batch_encode_plus(
        x_test,
        truncation = True,
        padding = True,
        max_length = 256,
        return_tensors = 'tf'
    )
x_test_input_ids = x_test_tokens['input_ids']
x_test_attention_mask = x_test_tokens['attention_mask']
# Création du modèle BERT
input_ids = Input(shape = (256,), dtype=tf.int32, name = "input_ids")
attention_mask = Input(shape = (256,), dtype=tf.int32, name = "attention_mask")
bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
bert_outputs = bert_model(input_ids, attention_mask = attention_mask)
# Ajout de couches supplémentaires pour la classification
x = bert_outputs.pooler_output
x = Dropout(0.1)(x)
x = Dense(256, activation = 'relu')(x)
x = Dropout(0.1)(x)
output = Dense(len(label_encoder.classes_), activation = 'softmax')(x)
model = Model(inputs=[input_ids, attention_mask], outputs = output)
# Compiler le modèle
optimizer = Adam(learning_rate = 2e-5)
model.compile(loss='sparse_categorical_crossentropy', optimizer = optimizer, metrics = ['accuracy'])
# Ajouter EarlyStopping avec min_delta
early_stopping = EarlyStopping(monitor = 'val_loss', patience = 2, min_delta = 0, restore_best_weights = True)
# Entraînement du modèle avec EarlyStopping
history = model.fit(
    [x_train_input_ids, x_train_attention_mask],
    y_train,
    epochs = 10,
    batch_size = 16,
    validation_split = 0.2,
    callbacks = [early_stopping]
    )
# Évaluer le modèle sur les données de test
predictions = model.predict([x_test_input_ids, x_test_attention_mask])
predicted_labels = np.argmax(predictions, axis = 1)