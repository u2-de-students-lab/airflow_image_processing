# airflow_image_processing
Airflow configured to be deployed with Docker containing DAG and scripts for images loading and processing.

This app does 2 things:
>- First script takes images from the web using Imsea API and load them into Minio bucket with raw images;
>- Second script takes this raw images from first bucket, crop them and load into bucket with transformed images.

All this this works in Docker and rules by Airflow.

Docker-compose file includes airflow, redis, postgres, flowers, docker-proxy (need to give airflow permitions to work with local socker.sock) and minio images.

Each scripts has it's own Dockerfile, because of they are pretend to be DAG tasks with different parameters.

