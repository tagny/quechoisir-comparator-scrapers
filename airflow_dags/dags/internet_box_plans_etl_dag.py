"""This DAG is used to run the ETL (Extract, Transform, Load)
pipeline for internet box plans"""

from datetime import datetime

import pendulum
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG
from docker.types import Mount

ENV_FILE = "internet_box_plans_etl_dag.env"
CONFIG_FILE = "config/extract_action_sequence.yml"

HOST_SA_KEY_PATH = "/tmp/service_account_key.json"
CONTAINER_SA_KEY_PATH = "/tmp/service_account_key.json"

sa_key_mount = Mount(
    source=HOST_SA_KEY_PATH,
    target=CONTAINER_SA_KEY_PATH,
    type="bind",  # Use 'bind' for mounting host directories/files
    read_only=True,  # Recommended for config files/secrets
)

DAG_NAME = "quechoisir_internet_box_plans_etl"

# DAG configuration
with DAG(
    dag_id=DAG_NAME,
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["tagny", "quechoisir", "internet_box_plans"],
) as dag:
    today_date = datetime.now().strftime("%Y/%m/%d")
    # Define the start task
    start_task = BashOperator(
        task_id="0_start_pipeline",
        bash_command='echo "Starting ETL... wd=$(pwd)"'
        f" && ls {HOST_SA_KEY_PATH}"
        f' && [ -f "{HOST_SA_KEY_PATH}" ] && echo "Service account key found'
        f' at {HOST_SA_KEY_PATH}" && exit 0 || echo "Service account key not'
        f' found at {HOST_SA_KEY_PATH}" && exit 1',
    )

    end_task = BashOperator(task_id="4_end_pipeline", bash_command="echo 'Ending ETL!'")

    extract_task_id = f"1_extract_{DAG_NAME}"
    transform_task_id = f"2_transform_{DAG_NAME}"
    load_task_id = f"3_load_{DAG_NAME}"

    extract_task = DockerOperator(
        task_id=extract_task_id,
        dag=dag,
        image="tagny/quechoisir-internet-box-plans-etl:latest",
        container_name=f"airflow-task-{extract_task_id}",
        auto_remove="force",
        env_file=ENV_FILE,
        # --- Mounts Configuration ---
        mounts=[sa_key_mount],
        command=[
            f"uv run -m etl extract -c {CONFIG_FILE} -k {CONTAINER_SA_KEY_PATH}",
        ],
    )

    transform_task = DockerOperator(
        task_id=transform_task_id,
        dag=dag,
        image="tagny/quechoisir-internet-box-plans-etl:latest",
        container_name=f"airflow-task-{transform_task_id}",
        auto_remove="force",
        env_file=ENV_FILE,
        # --- Mounts Configuration ---
        mounts=[sa_key_mount],
        command=[
            f"uv run -m etl transform -d {today_date} -k {CONTAINER_SA_KEY_PATH}",
        ],
    )

    load_task = DockerOperator(
        task_id=load_task_id,
        dag=dag,
        image="tagny/quechoisir-internet-box-plans-etl:latest",
        container_name=f"airflow-task-{load_task_id}",
        auto_remove="force",
        env_file=ENV_FILE,
        # --- Mounts Configuration ---
        mounts=[sa_key_mount],
        command=[
            f"uv run -m etl load -d {today_date} -k {CONTAINER_SA_KEY_PATH}",
        ],
    )

    start_task >> extract_task >> transform_task >> load_task >> end_task
