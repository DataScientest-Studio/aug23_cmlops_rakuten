# pip install langdetect
# pip install transformers
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.preprocessing import LabelEncoder
import nltk

# Librairies pour traitement de texte
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextProcessor:
    def __init__(self):
        """
        Initialise un objet TextProcessor pour le traitement du texte.

        Cette classe est utilisée pour nettoyer et prétraiter le texte en utilisant diverses techniques
        telles que la suppression des balises HTML, le découpage en tokens, la suppression des mots vides et le stemming.

        Args:
            Aucun argument nécessaire lors de l'initialisation.

        Attributes:
            stopwords_fr (set): Ensemble de mots vides en français.
            stopwords_en (set): Ensemble de mots vides en anglais.
            stopwords_de (set): Ensemble de mots vides en allemand.
            stemmer (SnowballStemmer): Un stemmer utilisé pour la racinisation des mots en français.
        """
        self.stopwords_fr = set(stopwords.words('french'))
        self.stopwords_en = set(stopwords.words('english'))
        self.stopwords_de = set(stopwords.words('german'))
        self.stemmer = SnowballStemmer('french')

    def preprocess_text(self, text):
        """
        Prétraite le texte en supprimant les balises HTML, les caractères spéciaux, et en appliquant le stemming.

        Args:
            text (str): Le texte à prétraiter.

        Returns:
            str: Le texte prétraité.
        """
        if isinstance(text, str):
            text = self._clean_text(text)
            tokens = self._tokenize(text)
            tokens = self._remove_stopwords(tokens)
            tokens = self._stemming(tokens)
            preprocessed_text = ' '.join(tokens)
            if not preprocessed_text:
                return 'a'
            return preprocessed_text

    def _clean_text(self, text):
        """
        Supprime les balises HTML et les caractères spéciaux du texte.

        Args:
            text (str): Le texte à nettoyer.

        Returns:
            str: Le texte nettoyé.
        """
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\b(cm|mm|kg|g|l|ml|oz|lb|in)\b', '', text)
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\d{1,2}\s+\w+\s+\d{2,4}', '', text)
        text = re.sub(r'\d+', '', text)
        return text.lower()

    def _tokenize(self, text):
        """
        Découpe le texte en tokens (mots).

        Args:
            text (str): Le texte à découper.

        Returns:
            list: Une liste de tokens.
        """
        return word_tokenize(text)

    def _remove_stopwords(self, tokens):
        """
        Supprime les mots vides de la liste de tokens.

        Args:
            tokens (list): Une liste de tokens.

        Returns:
            list: Une liste de tokens sans les mots vides.
        """
        return [word for word in tokens if word.lower() not in self.stopwords_fr and word.lower() not in self.stopwords_en and word.lower() not in self.stopwords_de]

    def _stemming(self, tokens):
        """
        Applique la racinisation (stemming) aux tokens.

        Args:
            tokens (list): Une liste de tokens.

        Returns:
            list: Une liste de tokens après stemming.
        """
        return [self.stemmer.stem(word) for word in tokens]

class DataProcessor:
    def __init__(self):
        """
        Initialise un objet DataProcessor pour le traitement des données.

        Cette classe est utilisée pour prétraiter les données en utilisant la classe TextProcessor
        et pour encoder les étiquettes en catégories d'entiers.

        Args:
            Aucun argument nécessaire lors de l'initialisation.

        Attributes:
            text_processor (TextProcessor): Un objet TextProcessor pour le prétraitement du texte.
            label_encoder (LabelEncoder): Un encodeur d'étiquettes pour convertir les étiquettes en catégories d'entiers.
        """
        self.text_processor = TextProcessor()
        self.label_encoder = LabelEncoder()

    def preprocess_data(self, df):
        """
        Prétraite les données en nettoyant et en prétraitant le texte, et encode les étiquettes.

        Args:
            df (pandas.DataFrame): Le DataFrame contenant les données.

        Returns:
            pandas.DataFrame: Le DataFrame avec le texte prétraité et les étiquettes encodées.
        """
        df['description_complete'] = df['designation'].fillna('') + ' ' + df['description'].fillna('')
        df['description'] = df['description'].fillna('')
        df['description_complete'] = df['description_complete'].apply(self._replace_unnecessary_description)
        df['description_complete'].fillna('', inplace=True)
        df['description_complete_prétraite'] = df['description_complete'].apply(self.text_processor.preprocess_text)
        X = df['description_complete_prétraite']
        y = df['prdtypecode']

        # Convertir les étiquettes en catégories d'entiers
        y_encoded = self.label_encoder.fit_transform(y)
        df['prdtypecode_encoded'] = y_encoded

        return df

    def _replace_unnecessary_description(self, text):
        """
        Remplace les descriptions inutiles par des valeurs nulles.

        Args:
            text (str): La description à vérifier.

        Returns:
            str or None: La description ou une valeur nulle si la description est inutile.
        """
        valeur_bidon = "Attention !!! Ce produit est un import si les informations 'langues' et 'sous-titres' n'apparaissent pas sur cette fiche produit c'est que l'éditeur ne nous les a pas fournies. Néanmoins dans la grande majorité de ces cas il n'existe ni langue ni sous-titres en français sur ces imports."
        if valeur_bidon in str(text):
            return np.nan
        return text

if __name__ == '__main__':
    data_processor = DataProcessor()
    df = pd.read_csv('/content/drive/MyDrive/X_train_update.csv', index_col=0)
    df = data_processor.preprocess_data(df)