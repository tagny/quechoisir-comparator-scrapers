#!/bin/bash
# Start the airflow server and the etl in a tmux session
# Usage: bash -x ./scripts/start_script.sh <DAG_ID>
# Example: bash -x ./scripts/start_script.sh quechoisir_mobile_phone_plans_etl

LOG_DIR="./.logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/start_script_sh.log"

# Function to log messages with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting script..."
log "Dag id: $DAG_ID"
log "Log file: $LOG_FILE"

DAG_ID=$1
if [ -z "$DAG_ID" ]; then
    echo "Error: DAG_ID is not set. Please provide the dag id."
    exit 1
fi

if ! uv -V; then
    echo "uv is not installed. Installing uv first."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! docker -v; then
    echo "docker is not installed. Installing docker first."
    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install -y docker.io
fi

if ! jq -V; then
    echo "jq is not installed. Installing jq first."
    sudo apt-get install -y jq
fi

if ! tmux -V; then
    echo "tmux is not installed. Installing tmux first."
    sudo apt-get install -y tmux
fi

# add user to docker group to avoid sudo
# sudo groupadd docker
# sudo usermod -aG docker $USER

# get the docker image
docker image pull tagny/quechoisir-mobile-phone-plans-etl:latest

# copy the dags from the image to the host
mkdir -p ~/airflow/dags
docker run -it --rm -d --name quechoisir-tmp-container tagny/quechoisir-mobile-phone-plans-etl sleep 600
docker cp quechoisir-tmp-container:/app/dags ~/airflow
docker stop quechoisir-tmp-container
ls ~/airflow/dags

# init uv env
cd ~/workspace/airflow_env
uv sync
source .venv/bin/activate


# Function to wait for a tmux session to finish
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


log "Start airflow server in a tmux session"
tmux new -d -s airflow_server "bash airflow_standalone.sh"
log "Wait for airflow server to start"
sleep 20
log "Start dag in a tmux session"
tmux new -d -s dag "bash run_dag.sh $DAG_ID"
log "Wait for dag to finish"
wait_for_tmux_session_completion "dag" 20
log "Stopping airflow server..."
tmux kill-session -t airflow_server
log "Wait for airflow server to stop"
wait_for_tmux_session_completion "airflow_server" 5
log "All done!"
