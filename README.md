# airflow_image_processing
Airflow configured to be deployed with Docker containing DAG and scripts for images loading and processing.

 airflow_image_processing
Airflow configured to be deployed with Docker containing DAG and scripts for images loading and processing.

This app does 2 things:
>- First script takes images from the web using Imsea API and load them into Minio bucket with raw images;
>- Second script takes this raw images from first bucket, crop them and load into bucket with transformed images.

All this this works in Docker and rules by Airflow.

Docker-compose file includes airflow, redis, postgres, flowers, docker-proxy (need to give airflow permitions to work with local docker.sock) and minio images.

Each scripts has it's own Dockerfile, because of they are pretend to be DAG tasks with different parameters. That's why you should create dcoker script images before rinnung docker-compose.

# WARNING

After cloning this repository and entering it  you should create this directories:
>- ./airflow_home/logs
>- ./airflow_home/plugins

Secondary, you should build docker containers of:
>- ./scripts/load_script
>- ./scripts/transform_script

And last thing - you need `.env` file, which contains all environment variables from `docker-compose` file.

## Remember

Before running this project you shoild have buckets in minio to work with.

This app may note work on Apple Mac machines. In this way you should change entrypoint in Minio client to 'host.docker.internal'. That whould help.
