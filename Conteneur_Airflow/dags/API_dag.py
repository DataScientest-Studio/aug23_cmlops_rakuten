from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import shutil
import json
import numpy as np
import csv 
import requests




timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

def retrieve_and_save_data(text_data, image_data):
    temp_dir = "/app/temp"
    temp_text_path = os.path.join(temp_dir, "temp_text.txt")
    temp_image_path = os.path.join(temp_dir, "temp_image.jpg")

    with open(temp_text_path, "w") as text_file:
        text_file.write(text_data)

    with open(temp_image_path, "wb") as image_file:
        image_file.write(image_data)

    # Prédiction
    prdtypecode = predict(temp_text_path, temp_image_path)

    # Création d'un fichier JSON avec les informations
    json_data = {
        "prdtypecode": prdtypecode,
        "image_pd": temp_image_path,
        "description_complete": text_data,
    }
    
    json_path = os.path.join(temp_dir, f"classification_request_{timestamp}.json")
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)
    
    return json_path


def get_admin_decision(json_data):
    # Demandez à l'administrateur s'il souhaite valider, modifier la catégorie prdtypecode ou refuser les données
    user_input = input("Voulez-vous valider les données ? (valider / modifier / refuser): ").lower()

    if user_input == 'valider':
        return 'validate'
    elif user_input == 'modifier':
        return 'modify'
    elif user_input == 'refuser':
        return 'refuse'
    else:
        print("Entrée invalide. Veuillez choisir entre valider, modifier ou refuser.")
        return get_admin_decision(json_data)


def admin_validation():
    temp_dir = "/app/temp"
    files_to_remove = [] 
    
    # Si l'administrateur valide, copiez les informations dans le CSV et le dossier d'images
    target_csv_dir = "/Users/flavien/Desktop/API_RAKUTEN/API_CONTENEUR/Df_Encoded_test.csv:/app/data"
    target_csv_path = os.path.join(target_csv_dir, "Df_Encoded_test.csv")
    # Vous pouvez également copier l'image si nécessaire
    target_image_dir = "/Users/flavien/Desktop/API_RAKUTEN/API_CONTENEUR/224_X_Train_4D.npy:/app/data"
    target_image_path = os.path.join(target_image_dir, "224_X_Train_4D.npy")
    
    # Liste tous les fichiers JSON dans le répertoire temp et les trie
    json_files = sorted([f for f in os.listdir(temp_dir) if f.endswith(".json")])

    for json_file in json_files:
        json_path = os.path.join(temp_dir, json_file)

        # Lire les données du fichier JSON
        with open(json_path, "r") as json_file:
            json_data = json.load(json_file)
        # Obtenir la décision de l'administrateur
        admin_decision = get_admin_decision(json_data)

        if admin_decision == 'validate':
            # Prétraiter le texte
            preprocessed_text = preprocess_text(json_data['description_complete'])
            # Prétraiter l'image
            preprocessed_image = preprocess_image(json_data['image_pd'])
             
            shutil.copyfile(json_data['image_pd'], target_image_path)
            
            # Copier les informations avec le prdtypecode modifié dans le CSV
            with open(target_csv_path, "a", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([json_data['prdtypecode'], json_data['image_pd'], preprocessed_text])
            
            # Copier les informations avec le prdtypecode modifié dans le npy
            with open(target_image_path, "a", newline='') as np_file:
                np_writer = np.writer(np_file)
                np_writer.writerow([json_data['image_pd'], preprocessed_image])
            
            message = "Validation par l'administrateur effectuée. Données intégrées."

        elif admin_decision == 'modify':
            # Si l'administrateur souhaite modifier, demandez le nouveau code prdtypecode
            modified_prdtypecode = input("Entrez le nouveau code prdtypecode (un nombre de jusqu'à 4 chiffres) : ")

            # Le code doit être un nombre et avoir jusqu'à 4 chiffres
            while not modified_prdtypecode.isdigit() or len(modified_prdtypecode) > 4:
                print("Code invalide. Veuillez entrer un nombre d'au plus 4 chiffres.")
                modified_prdtypecode = input("Entrez le nouveau code prdtypecode (un nombre de jusqu'à 4 chiffres) : ")

            # Prétraiter le texte
            preprocessed_text = preprocess_text(json_data['description_complete'])
            # Prétraiter l'image
            preprocessed_image = preprocess_image(json_data['image_pd']) 
            
            # Copier les informations avec le prdtypecode modifié dans le CSV
            with open(target_csv_path, "a", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([modified_prdtypecode, json_data['image_pd'], preprocessed_text])

            # Copier le fichier image dans le dossier d'images
            target_image_dir = "/Users/flavien/Desktop/API_RAKUTEN/API_CONTENEUR/224_X_Train_4D.npy:/app/data"
            target_image_path = os.path.join(target_image_dir, f"image_{timestamp}.jpg")
            shutil.copyfile(json_data['image_pd'], target_image_path)

            # Ajouter la référence de l'image au CSV
            with open(target_csv_path, "a", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["", target_image_path, ""])
                
            # Copier les informations avec le prdtypecode modifié dans le npy
            with open(target_image_path, "a", newline='') as np_file:
                np_writer = np.writer(np_file)
                np_writer.writerow([json_data['image_pd'], preprocessed_image])

            message = "Modification de la catégorie prdtypecode effectuée. Données intégrées."
            
        elif admin_decision == 'refuse':
            message = "Validation par l'administrateur refusée. Données non intégrées."

        # Supprimer le fichier JSON une fois la décision prise
        # Ajoutez le chemin du fichier JSON à la liste pour suppression ultérieure
        files_to_remove.append(json_path)

        # Supprimez tous les fichiers JSON après le traitement de la boucle
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

        return {"admin_decision": admin_decision, "message": message}

    
# Définissez votre DAG Airflow
default_args = {
    'owner': 'admin',
    'start_date': datetime(2023, 12, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'RECUP_DATA',
    default_args=default_args,
    schedule_interval=timedelta(days=1),  # Déclenchez chaque jour
)

# Tâche pour récupérer et sauvegarder les données
retrieve_data_task = PythonOperator(
    task_id='retrieve_data_task',
    python_callable=retrieve_and_save_data,
    provide_context=True,
    dag=dag,
)

admin_validation_task = PythonOperator(
    task_id='admin_validation_task',
    python_callable=admin_validation,
    provide_context=True,
    dag=dag,
)


retrieve_data_task >> admin_validation_task
