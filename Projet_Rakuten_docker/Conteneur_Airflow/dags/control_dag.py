from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Définir les arguments par défaut pour le DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définir le DAG
dag = DAG(
    'test_dag',
    default_args=default_args,
    description='DAG for test',
    catchup=False,
    schedule_interval=None,
    is_paused_upon_creation=False,
)

def run_authentification_test():
    import subprocess
    result = subprocess.run(['python', '/app/data2/authentification_test.py'], capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Erreur lors de l'exécution du test d'authentification : {result.stderr}")
    print(result.stdout.decode('utf-8'))

authentification_test_task = PythonOperator(
    task_id='run_authentification_test',
    python_callable=run_authentification_test,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_task',
    dag=dag,
)

# Définir l'ordre d'exécution des tâches
authentification_test_task >> end_task