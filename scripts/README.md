# Bash scripts for automation

## Directory structure
```
scripts/
├── README.md                       # This file
├── install_chrome_webdriver.sh     # Install chrome webdriver
├── start_airflow.sh                # Start airflow in standalone mode
├── run_etl_dag.sh                  # Run a dag
└── start_script.sh                 # Start airflow in standalone mode and run a dag
```

## Usage

- `scripts/install_chrome_webdriver.sh`: install chrome webdriver
```bash
# Usage:
bash -x ./scripts/install_chrome_webdriver.sh
```
- `scripts/start_airflow.sh`: start airflow in standalone mode
```bash
# Usage:
bash -x ./scripts/start_airflow.sh <AIRFLOW_DAGS_DIR> <SERVICE_ACCOUNT_KEY_PATH>

# Example:
bash ./scripts/start_airflow.sh /home/tagny/github/quechoisir-comparator-scrapers/airflow_dags/dags .data/credentials/service_account_key.json
```
- `scripts/run_etl_dag.sh`: run a dag
```bash
# Usage:
bash -x ./scripts/run_etl_dag.sh <DAG_ID> <AIRFLOW_DAGS_DIR> <SERVICE_ACCOUNT_KEY_PATH>

# Example:
bash ./scripts/run_etl_dag.sh quechoisir_mobile_phone_plans_etl /home/tagny/github/quechoisir-comparator-scrapers/airflow_dags/dags .data/credentials/service_account_key.json
```
- `scripts/start_script.sh`: start airflow in standalone mode and run a dag
```bash
# Usage:
bash -x ./scripts/start_script.sh <DAG_ID> <AIRFLOW_DAGS_DIR> <SERVICE_ACCOUNT_KEY_PATH>

# Example:
bash ./scripts/start_script.sh quechoisir_mobile_phone_plans_etl /home/tagny/github/quechoisir-comparator-scrapers/airflow_dags/dags .data/credentials/service_account_key.json
```
