from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator

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