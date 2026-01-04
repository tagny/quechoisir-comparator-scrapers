#!/bin/bash
# Start the airflow server and the etl in a tmux session
# Usage: bash -x ./scripts/start_script.sh <DAG_ID> <AIRFLOW_DAGS_DIR> <SERVICE_ACCOUNT_KEY_PATH>
# Example: bash -x ./scripts/start_script.sh quechoisir_mobile_phone_plans_etl ./airflow_dags/dags ./.data/credentials/service_account_key.json

DAG_ID=$1
if [ -z "$DAG_ID" ]; then
    echo "Error: DAG_ID is not set. Please provide the dag id."
    exit 1
fi
AIRFLOW_DAGS_DIR=$2
if [ ! -d "$AIRFLOW_DAGS_DIR" ]; then
    echo "Error: AIRFLOW_DAGS_DIR is not a directory. Please provide the path to the airflow dags directory."
    exit 1
fi
SERVICE_ACCOUNT_KEY_PATH=$3
if [ ! -f "$SERVICE_ACCOUNT_KEY_PATH" ]; then
    echo "Error: SERVICE_ACCOUNT_KEY_PATH is not a file. Please provide the path to the service account key file."
    exit 1
fi
LOG_DIR="./.logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/start_script_sh.log"

# Function to log messages with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting script..."
log "Dag id: $DAG_ID"
log "Airflow dags directory: $AIRFLOW_DAGS_DIR"
log "Service account key path: $SERVICE_ACCOUNT_KEY_PATH"
log "Log file: $LOG_FILE"

wait_for_tmux_session_completion() {
    TMUX_TARGET_SESSION=$1
    WAITING_TIME=$2  # in seconds

    log "Waiting for completion of tmux session: $TMUX_TARGET_SESSION"

    # 2. Poll for status
    while true; do

        if tmux has-session -t "$TMUX_TARGET_SESSION"; then
            log "Session $TMUX_TARGET_SESSION is still running."
        else
            log "Session $TMUX_TARGET_SESSION is no more running."
            break
        fi
        log "Waiting for $WAITING_TIME seconds before checking again..."
        sleep $WAITING_TIME  # Wait before checking again
    done
}



progress-bar() {
  local duration=${1}


    already_done() { for ((done=0; done<$elapsed; done++)); do printf "▇"; done }
    remaining() { for ((remain=$elapsed; remain<$duration; remain++)); do printf " "; done }
    percentage() { printf "| %s%%" $(( (($elapsed)*100)/($duration)*100/100 )); }
    clean_line() { printf "\r"; }

  for (( elapsed=1; elapsed<=$duration; elapsed++ )); do
      already_done; remaining; percentage
      sleep 1
      clean_line
  done
  clean_line
}


AIRFLOW_SERVER_WAIT_TIME=30
ETL_WAIT_TIME=20
log "Start airflow server in a tmux session"
tmux new -d -s airflow_server "bash scripts/start_airflow.sh $AIRFLOW_DAGS_DIR $SERVICE_ACCOUNT_KEY_PATH"
log "Wait for airflow server to start"
progress-bar $AIRFLOW_SERVER_WAIT_TIME
if ! tmux has-session -t airflow_server; then
    log "Airflow server failed to start. Exiting."
    exit 1
fi
log "Start etl in a tmux session"
tmux new -d -s etl "bash scripts/run_etl_dag.sh $DAG_ID $AIRFLOW_DAGS_DIR"
log "Wait for etl to finish"
wait_for_tmux_session_completion "etl" 20
log "Stopping airflow server..."
tmux kill-session -t airflow_server
log "Wait for airflow server to stop"
wait_for_tmux_session_completion "airflow_server" 5
log "All done!"
