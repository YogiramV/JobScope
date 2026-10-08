FROM apache/airflow:3.3.2-python3.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY airflow/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt