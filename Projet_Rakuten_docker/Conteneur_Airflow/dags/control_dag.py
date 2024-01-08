from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

"""
DAG de test pour l'authentification

Ce DAG, nommé 'test_dag', a été conçu pour effectuer un test d'authentification en exécutant
le script 'authentification_test.py' situé dans '/app/data/'. Il utilise Apache Airflow pour
planifier et exécuter cette tâche de test.

Arguments par défaut :
    owner (str): Propriétaire du DAG.
    depends_on_past (bool): Indique si une tâche doit dépendre de l'exécution réussie de la précédente.
    start_date (datetime): Date de début d'exécution du DAG.
    email_on_failure (bool): Indique si les notifications par e-mail doivent être envoyées en cas d'échec.
    email_on_retry (bool): Indique si les notifications par e-mail doivent être envoyées lors d'une tentative de réexécution.
    retries (int): Nombre de tentatives de réexécution en cas d'échec d'une tâche.
    retry_delay (timedelta): Délai entre les tentatives de réexécution.

Tâches :
    - run_authentification_test: Tâche Python exécutant le script 'authentification_test.py'. Si une erreur
      se produit lors de l'exécution, une exception est levée.
    - end_task: Tâche factice indiquant la fin du DAG.

Note :
    - Assurez-vous que le script 'authentification_test.py' est présent dans le répertoire '/app/data2/'.
    - La planification (schedule_interval) est définie sur None, ce qui signifie que le DAG doit être déclenché manuellement.
    - Les notifications par e-mail en cas d'échec sont désactivées (email_on_failure=False).
    - Ce DAG effectue un simple test d'authentification et peut être adapté en fonction des besoins.
"""

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
    result = subprocess.run(['python', '/app/data/authentification_test.py'], capture_output=True)
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
