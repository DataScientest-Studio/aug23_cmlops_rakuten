from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import os
import shutil

def retrieve_and_save_data(text_data, image_data):
    temp_dir = "/app/temp"
    temp_text_path = os.path.join(temp_dir, "temp_text.txt")
    temp_image_path = os.path.join(temp_dir, "temp_image.jpg")

    with open(temp_text_path, "w") as text_file:
        text_file.write(text_data)

    with open(temp_image_path, "wb") as image_file:
        image_file.write(image_data)

    # Prédiction
    prdtypecode, thematique = predict(text_data, temp_image_path)

    return temp_text_path, temp_image_path, prdtypecode, thematique

def validate_and_integrate_data(prediction_result, target_csv_dir="/path/to/training/csv"):
    temp_text_path, temp_image_path, prdtypecode, thematique = prediction_result


    is_validation_successful = True

    if is_validation_successful:
        # Si la validation est réussie, renvoyez le résultat de la prédiction
        target_text_path = os.path.join(target_csv_dir, "new_data_text.txt")
        target_image_path = os.path.join(target_csv_dir, "new_data_image.jpg")
        target_csv_path = os.path.join(target_csv_dir, "training_data.csv")

        # Déplacez ou copiez les fichiers vers le dossier d'entraînement
        shutil.move(temp_text_path, target_text_path)
        shutil.move(temp_image_path, target_image_path)

         # Ajoutez les informations dans le fichier CSV
        with open(target_csv_path, "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([text_data, target_image_path, prdtypecode, thematique])

        return {"prdtypecode": prdtypecode, "thematique": thematique, "message": "Validation réussie. Données intégrées."}
    else:
        # Si la validation échoue, vous pouvez prendre des mesures spécifiques ou renvoyer None
        # Dans cet exemple, les fichiers temporaires ne sont pas déplacés, vous pouvez les supprimer si nécessaire
        if os.path.exists(temp_text_path):
            os.remove(temp_text_path)
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        return {"message": "Validation échouée. Données supprimées."} 

def integrate_data(**kwargs):
    # Logique pour intégrer les données dans le dossier CSV d'entraînement
    temp_text_path = kwargs['ti'].xcom_pull(task_ids='retrieve_data_task')[0]
    temp_image_path = kwargs['ti'].xcom_pull(task_ids='retrieve_data_task')[1]

    target_csv_dir = "/app/data/training/csv"
    target_text_path = os.path.join(target_csv_dir, "new_data_text.txt")
    target_image_path = os.path.join(target_csv_dir, "new_data_image.jpg")

    # Déplacez ou copiez les fichiers vers le dossier d'entraînement
    shutil.move(temp_text_path, target_text_path)
    shutil.move(temp_image_path, target_image_path)

# Définissez votre DAG Airflow
default_args = {
    'owner': 'admin',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'RECUP_DATA',
    default_args=default_args,
    schedule_interval=timedelta(weeks=1),  # Déclenchez chaque semaine
)

# Tâche pour récupérer et sauvegarder les données
retrieve_data_task = PythonOperator(
    task_id='retrieve_data_task',
    python_callable=retrieve_and_save_data,
    provide_context=True,
    dag=dag,
)

# Tâche pour la validation par l'administrateur
validate_data_task = PythonOperator(
    task_id='validate_data_task',
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)

# Tâche pour intégrer les données dans le dossier d'entraînement
integrate_data_task = PythonOperator(
    task_id='integrate_data_task',
    python_callable=integrate_data,
    provide_context=True,
    dag=dag,


)

# Définissez l'ordre des tâches
retrieve_data_task >> validate_data_task >> integrate_data_task
