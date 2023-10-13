import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D,Input, Dropout, LSTM, Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from runbert import tokenize, bert_model_creation, compile_bert, train_bert, predict_bert
from transformers import BertTokenizer, TFBertModel

# (68) Construction du modèle de fusion
# Charger le modèle Resnet pour les images
model_cnn = load_model('/content/drive/MyDrive/Colab_Notebooks/FICHIER_POUR_VERSIONS_OFFICIELLES/cnn_model.h5')

# Charger le modèle BERT
model_bert = tf.keras.models.load_model('/content/drive/MyDrive/Colab_Notebooks/FICHIER_POUR_VERSIONS_OFFICIELLES/model_bert.h5', custom_objects={'TFBertModel': TFBertModel})

# Charger le fichier CSV contenant les étiquettes
df_labels = pd.read_csv('/content/drive/MyDrive/Colab_Notebooks/FICHIER_POUR_VERSIONS_OFFICIELLES/Df_Encoded.csv')
# Extraire les étiquettes sous forme de tableau numpy
y = df_labels["LabelEncoded"].values

# Charger les données image pour le modèle CNN
X_cnn = np.load("/Users/flavien/Desktop/224_X_Train_4D/224_X_Train_4D.npy")

# Charger les input ids et attention mask
X_bert_input_ids = np.load('/Users/flavien/Desktop/projet_RAKUTEN/CNN_BERT/merged_input_ids.npy')
X_bert_attention_mask  = np.load('/Users/flavien/Desktop/projet_RAKUTEN/CNN_BERT/merged_attention_mask.npy')

# Récupérer toutes les couches du modèle CNN à l'exception de la dernière
cnn_layers = model_cnn.layers[:-1]
cnn_intermediate_model = tf.keras.models.Model(inputs=model_cnn.inputs, outputs=cnn_layers[-1].output)

# Récupérer toutes les couches du modèle BERT à l'exception de la dernière
bert_layers = model_bert.layers[:-1]
bert_intermediate_model = tf.keras.models.Model(inputs=model_bert.inputs, outputs=bert_layers[-1].output)

# Prédictions des modèles tronqués
cnn_intermediate_output = cnn_intermediate_model.predict(X_cnn)
bert_intermediate_output = bert_intermediate_model.predict([X_bert_input_ids, X_bert_attention_mask])

# Normalisation des prédictions
cnn_mean, cnn_std = tf.nn.moments(cnn_intermediate_output, axes=[0])
normalized_cnn_intermediate_output = (cnn_intermediate_output - cnn_mean) / (cnn_std + 1e-8)

bert_mean, bert_std = tf.nn.moments(bert_intermediate_output, axes=[0])
normalized_bert_intermediate_output = (bert_intermediate_output - bert_mean) / (bert_std + 1e-8)

# concaténation des prédictions image et text
batch_size = 1000
num_samples = len(cnn_intermediate_output)
num_batches = num_samples// batch_size#(vérif)
merged_output = []
for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = (i + 1) * batch_size
    cnn_batch = cnn_intermediate_output[start_idx:end_idx]
    bert_batch = bert_intermediate_output[start_idx:end_idx]
    merged_batch = np.concatenate((cnn_batch, bert_batch), axis=1)
    merged_output.append(merged_batch)
merged_output = np.concatenate(merged_output, axis=0)

# One hot encoding de y et transformation en integer
y_categ = to_categorical(y)
y_categ=y_categ[:84000,:].astype(int)

# Architecture du modèle de fusion
inputs = Input(shape=(merged_output.shape[1],), name="Input")
first_layer = Dense(units=merged_output.shape[1], activation='relu')
second_layer = Dense(units=64, activation='relu')
output_layer = Dense(units=27, activation='softmax')
x = first_layer(inputs)
x = second_layer(x)
outputs = output_layer(x)
model = Model(inputs=inputs, outputs=outputs)

# (69) entraînement du modèle de fusion

# callbacks
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=7,
    min_delta=0.01,
    verbose=1,
    mode='min'
)
reduce_learning_rate = ReduceLROnPlateau(
    monitor="val_loss",
    patience=3,
    min_delta=0.01,
    factor=0.3,
    cooldown=3,
    verbose=1
)

# Compiler le modèle de fusion
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(merged_output, y_categ, test_size=0.2, random_state=42)

# Entraînement du modèle
history = model.fit(
    X_train, y_train,
    batch_size=64,
    epochs=50,
    validation_data=(X_test, y_test),
    callbacks=[reduce_learning_rate, early_stopping]
)

# Enregistrer le modèle CNN en tant que fichier h5
model.save('/Users/flavien/Desktop/projet_RAKUTEN/CNN_BERT/modele_fusion.h5')

# Prédire les classes des données de validation
predictions = model.predict(X_test)
predicted_labels = np.argmax(predictions, axis=1)
y_test = np.argmax(y_test, axis=1)

# Sauvegarder les prédictions dans un fichier CSV
results_df = pd.DataFrame({'True Label': y_test, 'Predicted Label': predicted_labels})
results_df.to_csv(f'/Users/flavien/Desktop/projet_RAKUTEN/CNN_BERT/predictions_fusion.csv', index=False)
