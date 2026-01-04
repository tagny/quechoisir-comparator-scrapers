# Internet box plans ETL package

This package is used to extract internet box plans data from the website https://quechoisir.com/ and store it in a database (e.g. BigQuery).

## Package structure

```
internet_box_plans/
├── .env.example                         # example of environment variables file
├── pyproject.toml                       # project configuration file
├── README.md                            # this README file
├── uv.lock                              # uv lock file
├── .logs/                               # logs directory
├── config                               # config package
│   └── extract_action_sequence.yml      # action sequence config file
├── etl                                  # etl package
│    ├── __init__.py                     # etl package initialization script
│    ├── __main__.py                     # etl package main script
│    ├── __version__.py                  # etl package version script
│    ├── logging_setup.py                # etl package logging setup script
│    ├── data                            # etl package data directory
│    │   └── raw_data_loading.py         # etl package data raw data loading script
│    ├── extract                         # etl package extract module
│    │   ├── __init__.py                 # etl package extract module initialization script
│    │   ├── downloading.py              # etl package extract module downloading script
│    │   └── selenium_setup.py           # etl package extract module selenium setup script
│    ├── transform                       # etl package transform module
│    │   ├── __init__.py                 # etl package transform module initialization script
│    │   └── transform.py                # etl package transform module transform script
│    └── load                            # etl package load module
│        ├── __init__.py                 # etl package load module initialization script
│        └── load.py                     # etl package load module load script
├── .bumpversion.toml                    # bumpversion configuration file
├── .dockerignore                        # docker ignore file
├── .env.example                         # example of environment variables file
├── Dockerfile-alpine                    # dockerfile for alpine linux - recommended as it is the smallest image
├── Dockerfile-bookworm                  # dockerfile for bookworm
├── pyproject.toml                       # project configuration file
├── README.md                            # this README file
└── uv.lock                              # uv lock file
```

## Installation

```bash
uv sync
```

## Configuration

### Extract action sequence

The extract action sequence is a YAML file that contains the configuration for the ETL pipeline. It is located at `config/extract_action_sequence.yml`.

### Environment variables

The environment variables are stored in a `.env` file. An example is provided in `.env.example`.

### Service account key

The service account key is a JSON file that contains the credentials for the Google Cloud service account. It is used to authenticate the ETL pipeline when it is run in a Docker container.

The service account key is mounted in the Docker container at `/tmp/service_account_key.json`.

## Usage

```bash
uv run -m etl extract -c <config_file> -k <service_account_key_json_path>
uv run -m etl transform -d <scraping_date> -k <service_account_key_json_path>
uv run -m etl load -d <scraping_date> -k <service_account_key_json_path>
```

where:
  - <config_file> is the path to the config file (e.g. "config/extract_action_sequence.yml")
  - <scraping_date> is the date of the scraping (e.g. "2026/01/04")
  - <service_account_key_json_path> is the path to the service account key JSON file (e.g. "./.data/credentials/service_account_key.json")

Example:
```bash
# Run the extract step of the ETL pipeline without cloud logging
uv run -m etl extract -c config/extract_action_sequence.yml

# Run the extract step of the ETL pipeline with cloud logging
uv run -m etl extract -c config/extract_action_sequence.yml -k .data/credentials/service_account_key.json

# Run the transform step of the ETL pipeline without cloud logging
uv run -m etl transform -d 2026/01/04 -k ../.data/credentials/service_account_key.json

# Run the load step of the ETL pipeline without cloud logging
uv run -m etl load -d 2026/01/04 -k ../.data/credentials/service_account_key.json
```

## Docker

```bash
export IMAGE_VERSION=$(python3 -c "from etl.__version__ import __version__; print(__version__)")

# Build the Docker image
docker build -t tagny/quechoisir-internet-box-plans-etl:$IMAGE_VERSION-alpine -t tagny/quechoisir-internet-box-plans-etl:latest -f Dockerfile-alpine .
docker build -t tagny/quechoisir-internet-box-plans-etl:$IMAGE_VERSION-bookworm -f Dockerfile-bookworm .

# Push the Docker image to Docker Hub
docker push tagny/quechoisir-internet-box-plans-etl:$IMAGE_VERSION-alpine
docker push tagny/quechoisir-internet-box-plans-etl:$IMAGE_VERSION-bookworm
docker push tagny/quechoisir-internet-box-plans-etl:latest


# Run the Docker container and open a shell
docker run --rm -ti tagny/quechoisir-internet-box-plans-etl sh

docker run --rm  -ti --env-file .env --mount type=bind,src=/tmp/service_account_key.json,dst=/tmp/service_account_key.json,readonly tagny/quechoisir-internet-box-plans-etl sh

# Run the ETL pipeline without cloud logging
docker run --rm  --env-file .env tagny/quechoisir-internet-box-plans-etl sh -c "uv run -m etl extract -c config/extract_action_sequence.yml -k /tmp/service_account_key.json"
```
