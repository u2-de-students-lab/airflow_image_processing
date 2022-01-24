FROM apache/airflow:2.2.2
RUN pip install --no-cache-dir apache-airflow-providers-docker==2.3.0
USER root
RUN groupadd --gid 999 docker \
    && usermod -aG docker airflow
USER airflow
