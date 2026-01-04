# Airflow dags for quechoisir-mobile-phone-plans-etl

This package implements the Airflow dags for quechoisir-mobile-phone-plans-etl.

## Project structure

- `mobile_phone_plans_etl_dag.py`: implements the mobile phone plans ETL dag running a docker container for each ETL step
- `pyproject.toml`: project configuration file
- `README.md`: this README file
- `.gitignore`: git ignore file
- `mobile_phone_plans_etl_dag.env.example`: example of environment variables file used by docker container to set environment variables

## Installation

if the Apache Airflow home directory is not set, set it to `/opt/airflow`, then copy the dag and env files to the dags dir:

```bash
cp dags/*.py dags/*.env /opt/airflow/dags/
```