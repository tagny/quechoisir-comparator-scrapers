# !/bin/bash
# Script to run Airflow DAGs for the project
# Usage: bash -x ./scripts/start_airflow.sh
# Example: bash ./scripts/start_airflow.sh
docker system prune -f
cd ~/workspace/airflow_env
uv sync
source .venv/bin/activate

# Set a temporary date variable (Airflow execution date format is typically YYYY-MM-DD)
LOG_DIR="./.logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/airflow_standalone_sh.log"

# Function to log messages with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting script..."
log "Log file: $LOG_FILE"

log "Setting environment variables..."
# ensure AIRFLOW_HOME is set to the default value
export AIRFLOW_HOME=$HOME/airflow
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=5
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=5
log "AIRFLOW__CORE__LOAD_EXAMPLES: $AIRFLOW__CORE__LOAD_EXAMPLES"
log "AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG: $AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG"
log "AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: $AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG"

# Migrate database
log "Migrating database..."
airflow db migrate

# Start Airflow in standalone mode
log "Starting Airflow in standalone mode..."
airflow standalone
