import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, TFBertModel
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.layers import Input, Dropout, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import accuracy_score, precision_score, classification_report, confusion_matrix
from Clean_text import TextProcessor, DataProcessor

class BERTClassifier:
    """
    Un classificateur basé sur l'architecture BERT (Bidirectional Encoder Representations from Transformers)
    pour les tâches de classification de textes.

    Attributs
    ----------
    tokenizer : BertTokenizer
        Tokenizer pour encoder les données textuelles d'entrée.
    model : TFBertModel
        Modèle BERT pré-entraîné.
    label_encoder : LabelEncoder
        Encodeur pour transformer les étiquettes entre leur forme originale et encodée.

    Méthodes
    -------
    prepare_data(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        Pré-traite les données et les divise en ensembles d'entraînement et de test.
    """

    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
        self.label_encoder = LabelEncoder()

    def prepare_data(self, df):
        """
        Pré-traite les données à partir d'un DataFrame et divise le jeu de données en ensembles d'entraînement 
        et de test pour le texte et les étiquettes.

        Paramètres
        ----------
        df : pd.DataFrame
            Le DataFrame contenant les données à pré-traiter.

        Retourne
        -------
        Tuple[pd.Series, pd.Series, pd.Series, pd.Series]
            Les ensembles d'entraînement et de test pour le texte (X_train, X_test) et les étiquettes (y_train, y_test).
        """
        data_processor = DataProcessor()
        df = data_processor.preprocess_data(df)
        X = df['description_complete_prétraite']
        y = df['prdtypecode_encoded']
        y = self.label_encoder.fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        """
        Entraîne le modèle BERT sur les données d'entraînement fournies.

        Paramètres
        ----------
        X_train : pd.Series
            Les descriptions à utiliser pour l'entraînement.
        y_train : pd.Series
            Les étiquettes correspondantes pour chaque description dans X_train.

        Retourne
        -------
        model : tf.keras.Model
            Le modèle BERT entraîné.
        x_train_input_ids : tf.Tensor
            Les identifiants des tokens utilisés pour l'entraînement.
        x_train_attention_mask : tf.Tensor
            Les masques d'attention utilisés pour l'entraînement.

        Notes
        -----
        Cette méthode configure et compile le modèle BERT, puis l'entraîne sur les données d'entraînement.
        Elle utilise également un mécanisme d'arrêt précoce pour éviter la suradaptation.
        """
        x_train_tokens = self.tokenizer.batch_encode_plus(
            X_train,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors='tf'
        )
        x_train_input_ids = x_train_tokens['input_ids']
        x_train_attention_mask = x_train_tokens['attention_mask']

        input_ids = Input(shape=(128,), dtype=tf.int32, name="input_ids")
        attention_mask = Input(shape=(128,), dtype=tf.int32, name="attention_mask")
        bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
        bert_outputs = bert_model(input_ids, attention_mask=attention_mask)

        x = bert_outputs.pooler_output
        x = Dropout(0.1)(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.1)(x)
        num_classes = len(self.label_encoder.classes_)
        output = Dense(num_classes, activation='softmax')(x)

        model = Model(inputs=[input_ids, attention_mask], outputs=output)
        optimizer = Adam(learning_rate=2e-5)
        model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
        early_stopping = EarlyStopping(monitor='val_loss', patience=2, min_delta=0, restore_best_weights=True)

        model.fit(
            [x_train_input_ids, x_train_attention_mask],
            y_train,
            epochs=10,
            batch_size=64,
            validation_split=0.2,
            callbacks=[early_stopping]
        )

        return model, x_train_input_ids, x_train_attention_mask


    
    def evaluate_model(self, model, X_test, y_test):
        """
        Évalue le modèle BERT sur un ensemble de test.

        Paramètres
        ----------
        model : tf.keras.Model
            Le modèle BERT préalablement entraîné.
        X_test : pd.Series
            Les descriptions de l'ensemble de test.
        y_test : pd.Series
            Les étiquettes de l'ensemble de test.

        Retourne
        -------
        accuracy : float
            Le taux de précision du modèle.
        precision : float
            La précision pondérée du modèle.
        classification_rep : str
            Le rapport de classification détaillé.
        confusion : np.ndarray
            La matrice de confusion.
        x_test_input_ids : tf.Tensor
            Les identifiants des tokens utilisés pour l'ensemble de test.
        x_test_attention_mask : tf.Tensor
            Les masques d'attention utilisés pour l'ensemble de test.
        """

        # Tokenisation et encodage de l'ensemble de test
        x_test_tokens = self.tokenizer.batch_encode_plus(
            X_test,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors='tf'
        )
        x_test_input_ids = x_test_tokens['input_ids']
        x_test_attention_mask = x_test_tokens['attention_mask']

        # Prédiction avec le modèle
        predictions = model.predict([x_test_input_ids, x_test_attention_mask])
        predicted_labels = np.argmax(predictions, axis=1)

        # Évaluation des prédictions
        accuracy = accuracy_score(y_test, predicted_labels)
        precision = precision_score(y_test, predicted_labels, average='weighted')
        classification_rep = classification_report(y_test, predicted_labels)
        confusion = confusion_matrix(y_test, predicted_labels)

        # Enregistrement des résultats des prédictions
        results_df = pd.DataFrame({'True Label': y_test, 'Predicted Label': predicted_labels})
        results_df.to_csv('/Users/flavien/Desktop/Model_BERT128_OC/predictions_BERT.csv', index=False)

        # Sauvegarde du modèle
        model.save('/Users/flavien/Desktop/Model_BERT128_OC/model.h5')

        return accuracy, precision, classification_rep, confusion, x_test_input_ids, x_test_attention_mask

if __name__ == '__main__':
    # Lecture du dataset
    df = pd.read_csv('/Users/flavien/Desktop/RAKUTEN/projet_RAKUTEN/DF/Df_Encoded.csv', index_col=0)

    # Initialisation et préparation des données
    bert_classifier = BERTClassifier()
    X_train, X_test, y_train, y_test = bert_classifier.prepare_data(df)

    # Entraînement du modèle BERT
    model, x_train_input_ids, x_train_attention_mask = bert_classifier.train_model(X_train, y_train)

    # Évaluation du modèle
    accuracy, precision, classification_rep, confusion, x_test_input_ids, x_test_attention_mask = bert_classifier.evaluate_model(model, X_test, y_test)

    # Concaténation des tokens et masques d'attention des ensembles d'entraînement et de test
    all_input_ids = np.concatenate([x_train_input_ids.numpy(), x_test_input_ids.numpy()])
    all_attention_masks = np.concatenate([x_train_attention_mask.numpy(), x_test_attention_mask.numpy()])

    # Sauvegarde des tokens et masques d'attention
    np.save('/Users/flavien/Desktop/Model_BERT128_OC/all_input_ids.npy', all_input_ids)
    np.save('/Users/flavien/Desktop/Model_BERT128_OC/all_attention_masks.npy', all_attention_masks)

