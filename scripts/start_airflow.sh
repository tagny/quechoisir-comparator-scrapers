# !/bin/bash
# Script to run Airflow DAGs for the project
# Usage: bash -x ./scripts/start_airflow.sh <AIRFLOW_DAGS_DIR> <SERVICE_ACCOUNT_KEY_PATH>
# Example: bash ./scripts/start_airflow.sh /home/tagny/github/quechoisir-comparator-scrapers/airflow_dags/dags .data/credentials/service_account_key.json
docker system prune -f

source airflow_dags/.venv/bin/activate

# Set a temporary date variable (Airflow execution date format is typically YYYY-MM-DD)
LOG_DIR="./.logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/start_airflow_sh.log"

# Function to log messages with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

AIRFLOW_DAGS_DIR=$1
if [ -z "$AIRFLOW_DAGS_DIR" ]; then
    log "Error: AIRFLOW_DAGS_DIR is not set. Please provide the path to the airflow dags directory."
    exit 1
fi

# Service account key check
SERVICE_ACCOUNT_KEY_PATH=$2
SERVICE_ACCOUNT_KEY_PATH_FOR_CONTAINER="/tmp/service_account_key.json"
if [ -z "$SERVICE_ACCOUNT_KEY_PATH" ]; then
    log "Error: SERVICE_ACCOUNT_KEY_PATH is not set. Please provide the path to the service account key file."
    exit 1
elif [ ! -f "$SERVICE_ACCOUNT_KEY_PATH" ]; then
    log "Error: SERVICE_ACCOUNT_KEY_PATH is not a file. Please provide the path to the service account key file."
    exit 1
else
    log "Service account key path: $SERVICE_ACCOUNT_KEY_PATH"
    cp $SERVICE_ACCOUNT_KEY_PATH $SERVICE_ACCOUNT_KEY_PATH_FOR_CONTAINER
    log "$(ls -lh $SERVICE_ACCOUNT_KEY_PATH_FOR_CONTAINER)"
fi

log "Starting script..."
log "Airflow dags directory: $AIRFLOW_DAGS_DIR"
log "Service account key path: $SERVICE_ACCOUNT_KEY_PATH"
log "Log file: $LOG_FILE"

log "Setting environment variables..."
# ensure AIRFLOW_HOME is set to the default value
export AIRFLOW_HOME=$HOME/airflow
log "AIRFLOW_HOME: $AIRFLOW_HOME"
log "Copying dags to $AIRFLOW_HOME/dags..."
cp -r "$AIRFLOW_DAGS_DIR" "$AIRFLOW_HOME/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=16
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
log "AIRFLOW_HOME: $AIRFLOW_HOME"
log "AIRFLOW__CORE__LOAD_EXAMPLES: $AIRFLOW__CORE__LOAD_EXAMPLES"
log "AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG: $AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG"
log "AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: $AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG"
log "Migrating database..."
airflow db migrate
log "Starting Airflow in standalone mode..."
airflow standalone
