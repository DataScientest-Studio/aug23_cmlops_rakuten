from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.applications import ResNet50

# --- CLASSES FOR DATA LOADING ---

class DataLoader(ABC):
    """
    Classe de base pour le chargement des données.
    """
    
    @abstractmethod
    def load(self, path: str):
        """
        Méthode abstraite pour charger des données depuis un chemin donné.

        :param str path: Chemin vers le fichier de données.
        """
        pass

class NPYLoader(DataLoader):
    def load(self, path: str):
        """
        Charge les données depuis un fichier .npy.

        :param str path: Chemin vers le fichier .npy.
        :return: Données chargées.
        """
        return np.load(path)

class CSVLoader(DataLoader):
    def load(self, path: str):
        """
        Charge les données depuis un fichier .csv.

        :param str path: Chemin vers le fichier .csv.
        :return: DataFrame pandas.
        """
        return pd.read_csv(path)

# --- CLASS FOR DATA PROCESSING ---

class DataProcessor:
    @staticmethod
    def process_data(df, column_name):
        """
        Traite les données en encodant les labels.

        :param df: DataFrame à traiter.
        :param str column_name: Nom de la colonne à encoder.
        :return: Labels encodés.
        """
        label_encoder = LabelEncoder()
        df[column_name] = label_encoder.fit_transform(df[column_name])
        y = df[column_name].values
        y = to_categorical(y)
        return y

# --- CLASSES FOR MODEL CREATION AND TRAINING ---

class ModelConfig:
    def __init__(self, output_units, activation_output, optimizer, loss, metrics):
        """
        Configuration du modèle.

        :param int output_units: Nombre d'unités de sortie.
        :param str activation_output: Activation pour la couche de sortie.
        :param str optimizer: Optimiseur.
        :param str loss: Fonction de perte.
        :param list metrics: Liste des métriques.
        """
        self.output_units = output_units
        self.activation_output = activation_output
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics

class ModelCreator:
    def create_model(self, config: ModelConfig, input_shape, units, include_extra_layer):
        """
        Crée un modèle ResNet50 avec une configuration donnée.

        :param ModelConfig config: Configuration du modèle.
        :param tuple input_shape: Forme d'entrée du modèle.
        :param int units: Nombre d'unités pour la couche dense supplémentaire.
        :param bool include_extra_layer: Si True, ajoute une couche dense supplémentaire.
        :return: Modèle créé.
        """
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        if include_extra_layer:
            x = Dense(units, activation="relu")(x)
        predictions = Dense(config.output_units, activation=config.activation_output)(x)

        model = Model(inputs=base_model.input, outputs=predictions)
        for layer in base_model.layers:
            layer.trainable = False
        
        model.compile(loss=config.loss, optimizer=config.optimizer, metrics=config.metrics)
        return model

class ModelTrainer:
    @staticmethod
    def train_model(model, x_train, y_train, x_val, y_val, epochs=5):
        """
        Entraîne le modèle avec les données fournies.

        :param model: Modèle à entraîner.
        :param np.array x_train: Données d'entraînement.
        :param np.array y_train: Labels d'entraînement.
        :param np.array x_val: Données de validation.
        :param np.array y_val: Labels de validation.
        :param int epochs: Nombre d'époques pour l'entraînement.
        :return: Historique de l'entraînement.
        """
        batch_size = 32
        steps_per_epoch = len(x_train) // batch_size
        history = model.fit(
            x_train, y_train,
            batch_size=batch_size,
            steps_per_epoch=steps_per_epoch,
            validation_data=(x_val, y_val),
            epochs=epochs
        )
        return history

# --- CLASS FOR MODEL SAVING ---

class ModelSaver:
    @staticmethod
    def save_model(model, path):
        """
        Sauvegarde le modèle dans un fichier.

        :param model: Modèle à sauvegarder.
        :param str path: Chemin pour sauvegarder le modèle.
        """
        model.save(path)


# --- IMPLEMENTATION ---

# Load data
x_loader = NPYLoader()
csv_loader = CSVLoader()

x_train_path = "/Users/flavien/Desktop/224_X_Train_4D/224_X_Train_4D.npy"
df_path = "/Users/flavien/Desktop/RAKUTEN/projet_RAKUTEN/DF/Df_Encoded.csv"

X_train = x_loader.load(x_train_path)
df = csv_loader.load(df_path)

# Process data
y = DataProcessor.process_data(df, "prdtypecode")
X_train, X_val, y_train, y_val = train_test_split(X_train, y, test_size=0.2, random_state=42)

# Model configuration
model_config = ModelConfig(
    output_units=27,
    activation_output="softmax",
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Model creation, training, and saving
model_creator = ModelCreator()

units, extra_layer = 256, 'oui'
model = model_creator.create_model(model_config, X_train.shape[1:], units, extra_layer == 'oui')
history = ModelTrainer.train_model(model, X_train, y_train, X_val, y_val)

# Modify this path as per your requirement
save_path = "/Users/flavien/Desktop/Model_RESNET256_OC/resnet_model.h5"
ModelSaver.save_model(model, save_path)
