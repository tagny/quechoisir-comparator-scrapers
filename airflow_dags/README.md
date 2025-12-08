# Airflow dags for quechoisir-mobile-phone-plans-etl

This package implements the Airflow dags for quechoisir-mobile-phone-plans-etl.

# project structure

- `mobile_phone_plans_etl_dag.py`: implements the mobile phone plans ETL dag running a docker container for each ETL step
- `pyproject.toml`: project configuration file
- `README.md`: this README file
- `.gitignore`: git ignore file
- `mobile_phone_plans_etl_dag.env.example`: example of environment variables file used by docker container to set environment variables
