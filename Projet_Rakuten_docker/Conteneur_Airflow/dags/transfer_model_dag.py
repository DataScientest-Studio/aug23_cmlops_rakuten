from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator

"""
DAG pour le transfert et le remplacement d'un fichier modèle.

Ce DAG, nommé 'transfer_model_dag', a été conçu pour automatiser le processus de transfert
et de remplacement d'un fichier modèle entre un conteneur d'entraînement et un stockage externe
à l'aide de Docker et rclone.

Arguments par défaut :
    owner (str): Propriétaire du DAG.
    depends_on_past (bool): Indique si une tâche doit dépendre de l'exécution réussie de la précédente.
    start_date (datetime): Date de début d'exécution du DAG.
    email_on_failure (bool): Indique si les notifications par e-mail doivent être envoyées en cas d'échec.
    email_on_retry (bool): Indique si les notifications par e-mail doivent être envoyées lors d'une tentative de réexécution.
    retries (int): Nombre de tentatives de réexécution en cas d'échec d'une tâche.
    retry_delay (timedelta): Délai entre les tentatives de réexécution.

Tâches :
    - copy_model_task: Tâche Docker pour copier le fichier modèle du conteneur d'entraînement vers un répertoire partagé.
    - transfer_model_task: Tâche Docker pour effectuer le transfert et le remplacement du modèle avec rclone.

Chemins des fichiers :
    - source_model_path: Chemin du fichier modèle dans le conteneur d'entraînement.
    - destination_model_path: Chemin du fichier modèle dans le répertoire partagé.
    - rclone_destination_path: Chemin de destination pour le transfert rclone.

Note :
    - Assurez-vous que les images Docker 'entrainement' et 'rclone' sont correctement configurées.
    - Le DAG est configuré pour un déclenchement manuel (schedule_interval=None).
    - Les notifications par e-mail en cas d'échec sont désactivées (email_on_failure=False).
    - Les tâches utilisent DockerOperator pour exécuter des commandes Docker.

"""

# Définir les arguments du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Créer le DAG
dag = DAG(
    'transfer_model_dag',
    default_args=default_args,
    description='DAG pour transférer et remplacer un fichier modèle',
    schedule_interval=None,  # Définir à None pour le déclenchement manuel
)

# Chemins des fichiers
source_model_path = '/app/mlruns/models/model_fusion_O.py'
destination_model_path = '/rclone/drive/combined_model_trained_after_resume.h5'
rclone_destination_path = 'destination:Projet_rakuten_MLOPS:Model/combined_model_trained_after_resume.h5'

# Étape 1 : Tâche pour copier le fichier modèle du conteneur d'entraînement vers un répertoire partagé
copy_model_task = DockerOperator(
    task_id='copy_model_task',
    image='entrainement',
    command=f'cp {source_model_path} {destination_model_path}',
    network_mode='my-network',
    dag=dag,
)

# Étape 2 : Tâche pour effectuer le transfert et le remplacement du modèle avec rclone
transfer_model_task = DockerOperator(
    task_id='transfer_model_task',
    image='rclone',
    command=f'rclone copy --update {destination_model_path} {rclone_destination_path}',
    network_mode='my-network',
    dag=dag,
)

# Définir l'ordre des tâches
copy_model_task >> transfer_model_task
