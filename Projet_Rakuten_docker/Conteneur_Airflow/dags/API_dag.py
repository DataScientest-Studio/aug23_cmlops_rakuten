from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
import os
import pandas as pd
import numpy as np

"""
Script Apache Airflow pour fusionner des fichiers CSV et NPY dans un DAG.

Ce script crée un DAG nommé 'api_dag' utilisant Apache Airflow. Le DAG comprend une tâche
appelée 'merge_files_conteneur_api' qui ajoute les nouvelles données dans les fichiers CSV et NPY dans le répertoire
'/app/data' aux fichiers existants. Une fois la fusion effectuée, les fichiers traités
sont supprimés.

Le script utilise des fonctions telles que merge_files_conteneur_api pour effectuer la fusion,
supprimer les fichiers traités et afficher des informations de débogage.

Arguments par défaut :
    owner (str): Propriétaire du DAG.
    depends_on_past (bool): Indique si une tâche doit dépendre de l'exécution réussie de la précédente.
    start_date (datetime): Date de début d'exécution du DAG.
    email_on_failure (bool): Indique si les notifications par e-mail doivent être envoyées en cas d'échec.
    email_on_retry (bool): Indique si les notifications par e-mail doivent être envoyées lors d'une tentative de réexécution.
    retries (int): Nombre de tentatives de réexécution en cas d'échec d'une tâche.
    retry_delay (timedelta): Délai entre les tentatives de réexécution.

Note :
    - Assurez-vous d'avoir les modules requis installés.
    - Les déclarations print utilisées pour le débogage peuvent être désactivées
      en production.
    - Ce script suppose une structure de fichier spécifique dans '/app/data'.

"""
# Définir les arguments par défaut pour le DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 14),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définir le DAG avec catchup=False pour éviter l'exécution des tâches manquées
dag = DAG(
    'api_dag',
    default_args=default_args,
    description='DAG pour remplacer les fichiers entre les conteneurs Docker',
    catchup=False,
    is_paused_upon_creation=False,
)

# Tâche préliminaire pour fusionner les fichiers dans Conteneur_API
def merge_files_conteneur_api(**kwargs):
    # Récupérer le chemin des fichiers à fusionner
    csv_filepath = "/app/drive/CSV_Rakuten_MLOPS.csv"
    npy_filepath = "/app/drive/matrice_photo_4D.npy"
      
    # Récupérer la liste des nouveaux fichiers dans /app/data
    new_files_directory = "/app/data"
    new_csv_files = [file for file in os.listdir(new_files_directory) if file.endswith(".csv")]
    new_npy_files = [file for file in os.listdir(new_files_directory) if file.endswith(".npy")]

    # Ajoutez ces lignes pour déboguer
    print("Fichiers CSV dans /app/data :", new_csv_files)
    print("Fichiers NPY dans /app/data :", new_npy_files)

    # Assurez-vous que les fichiers ont le même nom avant de les fusionner
    matching_files = set(os.path.splitext(file)[0] for file in new_csv_files) & set(os.path.splitext(file)[0] for file in new_npy_files) 
    # Afficher les fichiers qui composent matching_files
    print("Fichiers correspondants dans new_csv_files :", matching_files.intersection(new_csv_files))
    print("Fichiers correspondants dans new_npy_files :", matching_files.intersection(new_npy_files))


    # Utiliser les noms de fichiers correspondants pour charger les nouveaux CSV et numpy 
    new_csv_list = [pd.read_csv(os.path.join(new_files_directory, file + ".csv")) for file in matching_files] 
    new_npy_list = [np.load(os.path.join(new_files_directory, file + ".npy")) for file in matching_files]  

    print("Taille de new_npy_list:", len(new_npy_list))
    print("Contenu de new_npy_list:", new_npy_list)

    print("Nouveaux fichiers CSV:", new_csv_files)
    print("Nouveaux fichiers NPY:", new_npy_files)

    # Charger le CSV existant
    existing_csv = pd.read_csv(csv_filepath)
    
    # Convertir chaque DataFrame dans new_csv_list en DataFrame individuel
    new_csv_list_as_dataframes = [pd.DataFrame(data) for data in new_csv_list]
    
    # Fusionner les DataFrames et ajouter une nouvelle ligne
    merged_csv = pd.concat([existing_csv] + new_csv_list_as_dataframes, ignore_index=True)
    
    # Charger uniquement les 10 dernières lignes du fichier existant
    existing_npy = np.memmap(npy_filepath, dtype='float32', mode='r', shape=(10, 224, 224, 3))[-10:]
    print("Forme de existing_npy avant la fusion:", existing_npy.shape)
    
    # Assurez-vous que la nouvelle ligne du fichier numpy est une liste
    new_npy_list_as_list = new_npy_list[0].tolist()

    # Ajouter la ligne du nouveau fichier npy à la fin
    merged_npy = np.concatenate([existing_npy, new_npy_list_as_list], axis=0)
    
    # Sauvegarder les fichiers fusionnés dans le Conteneur_API
    merged_csv.to_csv(csv_filepath, index=False)
    np.save(npy_filepath, merged_npy)

    # Supprimer uniquement les fichiers qui ont été traités
    for file in matching_files:
        # Revenir à la source des fichiers
        source_file = file.split('.')[0]  # Supposons que le fichier est au format "nom_unique.csv" ou "nom_unique.npy"
        
        # Supprimer les fichiers correspondants à la source
        csv_source_file = f"{source_file}.csv"
        npy_source_file = f"{source_file}.npy"
    
        # Supprimer le fichier CSV source
        csv_source_path = os.path.join(new_files_directory, csv_source_file)
        if os.path.exists(csv_source_path):
            os.remove(csv_source_path)
        else:
            print(f"Le fichier {csv_source_path} n'existe pas.")
    
        # Supprimer le fichier NPY source
        npy_source_path = os.path.join(new_files_directory, npy_source_file)
        if os.path.exists(npy_source_path):
            os.remove(npy_source_path)
        else:
            print(f"Le fichier {npy_source_path} n'existe pas.")
    
        # Supprimer le fichier traité
        file_path = os.path.join(new_files_directory, file + ".csv")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Le fichier {file_path} n'existe pas.")

        file_path = os.path.join(new_files_directory, file + ".npy")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Le fichier {file_path} n'existe pas.")
    
    # Vider matching_files à la fin du traitement
    matching_files.clear()
    
    return print('Ajout des lignes aux fichiers effectuées et suppression des fichiers traités')

# Ajouter la tâche préliminaire au DAG
task_merge_files_conteneur_api = PythonOperator(
    task_id='merge_files_conteneur_api',
    python_callable=merge_files_conteneur_api,
    provide_context=True,
    dag=dag,
)

# Définir l'ordre d'exécution des tâches
task_merge_files_conteneur_api
