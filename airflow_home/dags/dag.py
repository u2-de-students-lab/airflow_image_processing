import os
from datetime import datetime
from typing import Dict, List

import yaml
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.docker.operators.docker import DockerOperator


BASE_DIR = os.path.dirname(__file__)
LOAD_SCRIPT_IMAGE = 'image-load-script'
TRANSFORM_SCRIPT_IMAGE = 'image-transform-script'
RAW_BUCKET_NAME = 'raw-images'
TRANSFORM_BUCKET_NAME = 'transformed-images'
WIDTH = '254'
HEIGHT = '254'

ENVIRONMENT={
    'MINIO_SECRET_KEY': os.getenv('MINIO_SECRET_KEY'), 
    'MINIO_ACCESS_KEY': os.getenv('MINIO_ACCESS_KEY')
}

def load_config_from_yaml(file_path: str) -> Dict[str, List[str]]:
    with open(file_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


default_args = {
    'depends_on_past': False
}


def create_tasks(dag: DAG, search_request: str, search_date: str) -> None:
    task_dummy = DummyOperator(
        task_id=f'{search_request}',
        dag=dag
    )
    
    task_1 = DockerOperator(
        task_id=f'download_{search_request}_images',
        docker_url='tcp://docker-proxy:2375',
        image=LOAD_SCRIPT_IMAGE,
        command=f'{search_request} {RAW_BUCKET_NAME} {search_date}',
        environment=ENVIRONMENT,
        dag=dag
    )

    task_2 = DockerOperator(
        task_id=f'transform_{search_request}_images',
        docker_url='tcp://docker-proxy:2375',
        image=TRANSFORM_SCRIPT_IMAGE,
        command=(
            f'{search_request} {RAW_BUCKET_NAME} {TRANSFORM_BUCKET_NAME} '
            f'{search_date} {WIDTH} {HEIGHT}'
        ),
        environment=ENVIRONMENT,
        dag=dag
    )

    task_dummy.set_downstream(task_1)
    task_1.set_downstream(task_2)


with DAG(
    dag_id='airflow_image_processing',
    default_args=default_args,
    description='Find images, resize them and load into Minio',
    schedule_interval='@daily',
    start_date=datetime(2022, 1, 24, 2, 0, 0),
    catchup=False
) as dag:
    config_data = load_config_from_yaml(f'{BASE_DIR}/configuration/config.yaml')

    for search_data in config_data['dogs_breeds']:
        create_tasks(
            dag=dag, 
            search_request=search_data, 
            search_date='{{ ds }}'
        )
