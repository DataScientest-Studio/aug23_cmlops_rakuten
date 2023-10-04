import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.plotting import figure, show
from bokeh.models.tools import HoverTool
from bokeh.models import  LabelSet, ColumnDataSource
from bokeh.models import ColumnDataSource, HoverTool, FactorRange
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import itertools
from PIL import Image

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import re
from nltk.stem import SnowballStemmer


def main():
    st.title("")
    
     # Menu latéral
    # Utiliser st.sidebar pour créer un menu latéral avec une taille de texte plus grande
    st.sidebar.markdown("<p style='font-size: 24px; font-weight: bold; text-align: center", unsafe_allow_html=True)
    menu_options = ["Accueil", "Présentation du projet", 
                    "Analyse exploratoire", "Démo"]
    st.sidebar.markdown("# Sommaire")
    choice = st.sidebar.radio("", menu_options)
    
    # Ajouter des sections en fonction du choix de l'utilisateur
    if choice == "Accueil":
       st.title("Projet RAKUTEN ")
       st.image("./Rakuten-Global-Logo.jpg")
       st.write("""
    
    Flavien SAUX
    
    https://github.com/Flav63s

    https://www.linkedin.com/in/flavien-s-712596190/

    Chadi BOULOS

    https://github.com/Chadiboulos

    https://www.linkedin.com/in/chadi-boulos-6b05aa2a/

    Constantin NZWESSA

    https://github.com/Consti23

    https://www.linkedin.com/in/constantin-nzwessa-322121250/

    Michael DEVAUX

    https://github.com/MichaelD24

    https://www.linkedin.com/in/micha%C3%ABl-devaux-362760139/

""")


    elif choice == "Présentation du projet":
        st.header("Objectif")
        st.write("L'algorithme qu'on a créé va nous aider à classifier un produit automatiquement dans la bonne catégorie en se basant sur l'image et la description disponibles")
        st.header("Défis")
        paragraphe1 = """
        ● Fiches produits créées par le client: Descriptif de taille aléatoire Images de taille et qualité différentes Fautes d'orthographe, différentes langue :
        
            - Descriptif de taille aléatoire
            - Images de taille et qualité différentes
            - Fautes d'orthographe, différentes langues"""

        st.write("")
        st.write(paragraphe1)
        "● L'algorithme doit être capable de traiter à la fois un format image et texte."
        

    elif choice == "Analyse exploratoire":
        st.header("Répartition des produits par catégorie")
        df = pd.read_csv('/Users/chadiboulos/Documents/Streamlit/Df_Encoded.csv')
        df_grouped = df.groupby('prdtypecode').agg({'img_pd':'count'}).reset_index(drop=False)
        prdtypecodes = [str(code) for code in df_grouped.prdtypecode]
        frequencies = [str(code) for code in df_grouped.img_pd]
        p = figure(x_range=prdtypecodes, width=1000, height=400, x_axis_label='catégories', y_axis_label='fréquence', tools = ["box_select", "wheel_zoom"])
        p.axis.major_label_orientation = 'vertical'
        p.vbar(x=prdtypecodes, top=frequencies, width=0.9)
        h = HoverTool(tooltips=[("(catégorie, fréquence)","(@x, @top)")])
        p.add_tools(h)
        st.bokeh_chart(p, use_container_width=True)
        
        
        st.header("Descriptif manquant par catégorie")
        df_nan = df[df['description'].isna()]
        df_nan_grouped = df_nan.groupby('prdtypecode').agg({'img_pd':'count'}).reset_index(drop=False)
        prdtypecodes_nan = [str(code) for code in df_nan_grouped.prdtypecode]
        frequencies_nan = [str(code) for code in df_nan_grouped.img_pd]
        p=figure(x_range=prdtypecodes_nan, width=800, height=400, x_axis_label='catégories', y_axis_label='fréquence en %', tools = ["box_select", "wheel_zoom"])
        p.axis.major_label_orientation = 'vertical'
        p.vbar(x=prdtypecodes_nan, top=frequencies_nan, width=0.9)
        h = HoverTool(tooltips=[("(catégorie, fréquence)","(@x, @top)")])
        p.add_tools(h)
        st.bokeh_chart(p, use_container_width=True)

        st.header("Familiarisation avec les catégories")
        selected_options = st.multiselect('Sélectionner une ou plusieurs catégories que vous souhaitez découvrir:', prdtypecodes)
        nb_selections = len(selected_options)
        
        if nb_selections == 0:
            st.write("")
            
        else:
            nb_rows = (nb_selections + 2) //3
            nb_cols = min(3, nb_selections)

            df['description_words'] = df['description_complete_prétraite'].str.split()
            word_counts_by_category = df.groupby('prdtypecode')['description_words'].apply(lambda x : pd.Series(x).explode().value_counts())
            df_word_counts = word_counts_by_category.reset_index().rename(columns = {'level_1': 'word', 'description_words' : 'count'})
            top_words_by_category = df_word_counts.groupby('prdtypecode').head(10)


            if nb_rows==1 and nb_cols==1:
                data = top_words_by_category[top_words_by_category['prdtypecode'] == int(selected_options[0])]
                fig, ax = plt.subplots()
                sns.barplot(data = data, x='count', y='word')
                ax.set_xlabel('Fréquence')
                ax.set_ylabel('Top Mots')
                ax.set_title(f'Catégorie {selected_options}')

            elif nb_rows == 1:
                fig, axes = plt.subplots(nb_rows, nb_cols, figsize=(9, 6))
                # axes = [axes]
                for i, axi in enumerate(axes):
                    data = top_words_by_category[top_words_by_category['prdtypecode'] == int(selected_options[i])]
                    sns.barplot(data = data, x='count', y='word', ax = axi)
                    axi.set_xlabel('Fréquence')
                    axi.set_ylabel('Top Mots')
                    axi.set_title(f'Catégorie {selected_options[i]}')

            else:
                fig, axes = plt.subplots(nb_rows, nb_cols, figsize = (9 , 6))
                for i, axi in enumerate(axes.flat):
                    if i < nb_selections:
                        data = top_words_by_category[top_words_by_category['prdtypecode'] == int(selected_options[i])]
                        sns.barplot(data = data, x='count', y='word', ax = axi)
                        axi.set_xlabel('Fréquence')
                        axi.set_ylabel('Top Mots')
                        axi.set_title(f'Catégorie {selected_options[i]}')
                    else:
                        axi.axis('off')

            # Suppression des sous-graphiques inutilisés
            if nb_selections < nb_rows * nb_cols:
                for i in range(nb_selections, nb_rows * nb_cols):
                    fig.delaxes(axes.flat[i])
            plt.tight_layout()
            st.pyplot(fig)
        
    elif choice == "Démo":
        model_cnn = load_model('/Users/chadiboulos/Documents/Rakuten/cnn_model.h5')
        model_bert = tf.keras.models.load_model('/Users/chadiboulos/Downloads/model_bert.h5', custom_objects={'TFBertModel': TFBertModel})
        model_fusion = load_model("/Users/chadiboulos/Documents/Rakuten/modele_fusion.h5")
        
        df = pd.read_csv('/Users/chadiboulos/Documents/Rakuten/Df_Encoded.csv')
        X_cnn = np.load("/Users/chadiboulos/Documents/Rakuten/224_X_Train_4D.npy")
        
        cnn_mean = np.load('/Users/chadiboulos/Documents/Streamlit/cnn_mean.npy')
        cnn_std = np.load('/Users/chadiboulos/Documents/Streamlit/cnn_std.npy')
        bert_mean = np.load('/Users/chadiboulos/Documents/Streamlit/bert_mean.npy')
        bert_std = np.load('/Users/chadiboulos/Documents/Streamlit/bert_std.npy')
        
        # Définition des stopwords pour le français et l'anglais
        stopwords_fr = set(stopwords.words('french'))
        stopwords_en = set(stopwords.words('english'))
        stopwords_de = set(stopwords.words('german'))

        # Fonction de prétraitement des textes
        def preprocess_text(text):
            # Vérifier si le texte n'est pas null, NaN ou float
            if isinstance(text, str):
                # Supprimer les balises HTML
                text = BeautifulSoup(text, "html.parser").get_text()
                # Supprimer les parenthèses et leur contenu
                text = re.sub(r'\([^)]*\)', '', text)
                # Supprimer les URLs
                text = re.sub(r'http\S+|www\S+', '', text)
                # Supprimer les adresses e-mail
                text = re.sub(r'\S+@\S+', '', text)
                # Supprimer la ponctuation
                text = re.sub(r'[^\w\s]', '', text)
                # Supprimer les unités de mesure
                text = re.sub(r'\b\w{1,2}\b', '', text)
                # Supprimer les unités de mesure
                text = re.sub(r'\b(cm|mm|kg|g|l|ml|oz|lb|in)\b', '', text)
                # Supprimer les dates
                text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)  # Supprimer les dates au format jj/mm/aaaa ou mm/jj/aaaa
                text = re.sub(r'\d{1,2}-\d{1,2}-\d{2,4}', '', text)  # Supprimer les dates au format jj-mm-aaaa ou jj-mm-aaaa
                text = re.sub(r'\d{1,2}\s+\w+\s+\d{2,4}', '', text)  # Supprimer les dates au format jj Mois aaaa ou Mois jj, aaaa
                # Enlever les chiffres
                text = re.sub(r'\d+', '', text)
                text = " ".join(text.split())
                # Convertir en minuscules
                text = text.lower()
                # Tokenisation des mots
                tokens = word_tokenize(text)
                # Suppression des stopwords
                tokens = [word for word in tokens if word.lower() not in stopwords_fr and word.lower() not in stopwords_en and word.lower() not in stopwords_de]
                # Stemming
                stemmer = SnowballStemmer('french')
                tokens = [stemmer.stem(word) for word in tokens]
                # Post-lemmatisation
                tagged_tokens = nltk.pos_tag(tokens)
                pos_words = [word for word, tag in tagged_tokens if tag.startswith('N') or tag.startswith('V') or tag.startswith('J') or tag.startswith('R')]
                # Reconstitution du texte prétraité
                preprocessed_text = ' '.join(tokens)
                return preprocessed_text
            else:
                return ""
        
        def modele_cnn(image_array):
            im_reshaped = np.expand_dims(image_array, axis=0)
            predictions = model_cnn.predict(im_reshaped)
            predicted_label = np.argmax(predictions, axis=-1)
            return predicted_label[0]
            
        def modele_bert(text):
            text_preprocessed = preprocess_text(text)
            tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
            X_tokens = tokenizer.encode_plus(text_preprocessed, truncation=True, padding='max_length', max_length=128, return_tensors='tf')
            X_tokens_input_ids = X_tokens['input_ids']
            X_tokens_attention_mask = X_tokens['attention_mask']
            pred_bert = model_bert.predict([X_tokens_input_ids, X_tokens_attention_mask])
            predicted_labels = np.argmax(pred_bert, axis=-1)
            return predicted_labels[0]
            
        def modele_cnn_fusion(image_array):
            cnn_layers = model_cnn.layers[:-1]
            cnn_intermediate_model = tf.keras.models.Model(inputs=model_cnn.inputs, outputs=cnn_layers[-1].output)
            im_reshaped = np.expand_dims(image_array, axis=0)
            cnn_intermediate_output = cnn_intermediate_model.predict(im_reshaped)
            #normalized_cnn_intermediate_output = (cnn_intermediate_output - cnn_mean) / (cnn_std + 1e-8)
            #return normalized_cnn_intermediate_output
            return cnn_intermediate_output
        
        def modele_bert_fusion(text):
            bert_layers = model_bert.layers[:-1]
            bert_intermediate_model = tf.keras.models.Model(inputs=model_bert.inputs, outputs=bert_layers[-1].output)
            text_preprocessed = preprocess_text(text)
            tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
            X_tokens = tokenizer.encode_plus(text_preprocessed, truncation=True, padding='max_length', max_length=128, return_tensors='tf')
            X_tokens_input_ids = X_tokens['input_ids']
            X_tokens_attention_mask = X_tokens['attention_mask']
            bert_intermediate_output = bert_intermediate_model.predict([X_tokens_input_ids, X_tokens_attention_mask])
            return bert_intermediate_output
            
        def modele_fusion(image_array, text):
            cnn_intermediate_output = modele_cnn_fusion(image_array)
            normalized_cnn_intermediate_output = (cnn_intermediate_output - cnn_mean) / (cnn_std + 1e-8)
            bert_intermediate_output = modele_bert_fusion(text)
            normalized_bert_intermediate_output = (bert_intermediate_output - bert_mean) / (bert_std + 1e-8)
            merged_output = np.concatenate((normalized_cnn_intermediate_output, normalized_bert_intermediate_output), axis=1)
            predictions = model_fusion.predict(merged_output)
            predicted_labels = np.argmax(predictions, axis=1)
            return predicted_labels[0]

        def encoded_to_prdtypecode(x):
            liste_encodee = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
                           25,26,27]
            # liste_encodee_str = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24',
            #                 '25','26','27']
        # liste_prdtypecode = ['10', '40', '50', '60', '1140', '1160', '1180', '1280', '1281', '1300',
        #             '1301', '1302', '1320', '1560', '1920', '1940', '2060', '2220', '2280',
        #             '2403', '2462', '2522', '2582', '2583', '2585', '2705', '2905']
        
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
            indice = liste_encodee.index(x)
            prd_type_code = liste_prdtypecode[indice]
            thématique = liste_thématique[indice]
            return prd_type_code, thématique

#resultat = list(map(encoded_to_prdtypecode, x))


        option = st.selectbox('Choisir un test que vous souhaitez effectuer:', ['Charger une photo de produit', 'Ecrire un descriptif de produit', 'Charger une photo et écrire un descriptif de produit', 'Sélectionner un échantillon du dataset existant'])
        
        # Option: Upload Photo
        if option == 'Charger une photo de produit':
            uploaded_file = st.file_uploader('Choisir une image', type=['jpg', 'png', 'jpeg'])


            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                image = image.resize((224,224))
                image_array = np.array(image)
                st.image(image, caption='Image chargée', use_column_width=True)

                # Run the image through 'model_cnn' and display the result
                result_cnn = modele_cnn(image_array)
                result_prdtypecode, result_thematique = encoded_to_prdtypecode(result_cnn)
                st.write('Catégorie prédite:', result_prdtypecode)
                st.write('Thématique correspondante:', result_thematique)

                

        # Option: Write Text
        elif option == 'Ecrire un descriptif de produit':
            text_input = st.text_area('Saisir votre texte ici', height=100)
            if st.button('Prédiction (BERT)'):
                result_bert = modele_bert(text_input)
                result_prdtypecode, result_thematique = encoded_to_prdtypecode(result_bert)
                st.write('Catégorie prédite:', result_prdtypecode)
                st.write('Thématique correspondante:', result_thematique)


        # Option: Upload Photo and Text
        elif option == 'Charger une photo et écrire un descriptif de produit':
            uploaded_file = st.file_uploader('Choisir une image', type=['jpg', 'png', 'jpeg'])
            text_input = st.text_area('Saisir le descriptif', height=100)
            if st.button('Prédiction (Modèle de fusion)'):
                image = Image.open(uploaded_file)
                image = image.resize((224,224))
                image_array = np.array(image)
                result_fusion = modele_fusion(image_array, text_input)
                result_prdtypecode, result_thematique = encoded_to_prdtypecode(result_fusion)
                st.write('Catégorie prédite:', result_prdtypecode)
                st.write('Thématique correspondante:', result_thematique)

        # Option: Select Random Samples
        else:
            selection = st.number_input('Sélectionner un échantillon du dataset existant:', value=1, step=1)
            random_numbers = np.random.randint(2, 84001, size=int(selection))
            df = df.iloc[random_numbers]
            X_cnn = X_cnn[random_numbers]
            x = df["description_complete_prétraite"]
            X_text = x.astype(str).tolist()
            tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
            X_tokens = tokenizer.batch_encode_plus(X_text,truncation=True,padding='max_length',max_length=128,return_tensors='tf')
            X_tokens_input_ids = X_tokens['input_ids']
            X_tokens_attention_mask = X_tokens['attention_mask']
            cnn_layers = model_cnn.layers[:-1]
            cnn_intermediate_model = tf.keras.models.Model(inputs=model_cnn.inputs, outputs=cnn_layers[-1].output)
            cnn_intermediate_output = cnn_intermediate_model.predict(X_cnn)
            bert_layers = model_bert.layers[:-1]
            bert_intermediate_model = tf.keras.models.Model(inputs=model_bert.inputs, outputs=bert_layers[-1].output)
            bert_intermediate_output = bert_intermediate_model.predict([X_tokens_input_ids, X_tokens_attention_mask])
            normalized_cnn_intermediate_output = (cnn_intermediate_output - cnn_mean) / (cnn_std + 1e-8)
            normalized_bert_intermediate_output = (bert_intermediate_output - bert_mean) / (bert_std + 1e-8)
            merged_output = np.concatenate((normalized_cnn_intermediate_output, normalized_bert_intermediate_output), axis=1)
            predictions = model_fusion.predict(merged_output)
            predicted_labels = np.argmax(predictions, axis=1)
            # result_prdtypecode, result_thematique = list(map(encoded_to_prdtypecode, predicted_labels))
            # st.write('Catégorie prédite:', result_prdtypecode)
            # st.write('Thématique correspondante:', result_thematique)
            result_list = list(map(encoded_to_prdtypecode, predicted_labels))
            st.dataframe(df['designation'])            
            st.write('Catégorie prédite:', [res[0] for res in result_list])
            st.write('Thématique correspondante:', [res[1] for res in result_list])

            

if __name__ == "__main__":
    main()








