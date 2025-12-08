# Mobile phone plans ETL package

This package is used to extract mobile phone plans data from the website https://quechoisir.com/ and store it in a database (e.g. BigQuery).

## Package structure

```
mobile_phone_plans/
├── .env.example                         # example of environment variables file
├── pyproject.toml                       # project configuration file
├── README.md                            # this README file
├── uv.lock                              # uv lock file
├── .logs/                               # logs directory
├── config                               # config package
│   └── extract_action_sequence.yml      # action sequence config file
└── etl                                  # etl package
    ├── __init__.py                      # etl package initialization script
    ├── __main__.py                      # etl package main script
    ├── __version__.py                   # etl package version script
    ├── logging_setup.py                 # etl package logging setup script
    ├── data                             # etl package data directory
    │   └── raw_data_loading.py          # etl package data raw data loading script
    └── extract                          # etl package extract module
        ├── __init__.py                  # etl package extract module initialization script
        ├── downloading.py               # etl package extract module downloading script
        └── selenium_setup.py            # etl package extract module selenium setup script
```

## Installation

```bash
uv sync
```

## Usage

```bash
uv run -m etl <etl_step> -c <config_file> -s <service_account_key_json_path>
```

where:
  - <etl_step> is the ETL step to run (e.g. "extract", "transform", "load")
  - <config_file> is the path to the config file (e.g. "config/extract_action_sequence.yml")
  - <service_account_key_json_path> is the path to the service account key JSON file (e.g. "./.data/credentials/service_account_key.json")

Example:
```bash
# Run the ETL pipeline without cloud logging
uv run -m etl extract -c config/extract_action_sequence.yml

# Run the ETL pipeline with cloud logging
uv run -m etl extract -c config/extract_action_sequence.yml -k .data/credentials/service_account_key.json
```

## Docker

```bash
export IMAGE_VERSION=$(python -c "from etl.__version__ import __version__; print(__version__)")

# Build the Docker image
docker build \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t tagny/quechoisir-mobile-phone-plans-etl:$IMAGE_VERSION .

docker tag tagny/quechoisir-mobile-phone-plans-etl:$IMAGE_VERSION tagny/quechoisir-mobile-phone-plans-etl:latest

# Run the Docker container and open a shell
docker run -ti tagny/quechoisir-mobile-phone-plans-etl:$IMAGE_VERSION sh
docker run -ti --env-file .env --mount type=bind,src=/tmp/service_account_key.json,dst=/tmp/service_account_key.json,readonly tagny/quechoisir-mobile-phone-plans-etl:$IMAGE_VERSION sh

# Run the ETL pipeline without cloud logging
docker run --env-file .env tagny/quechoisir-mobile-phone-plans-etl:$IMAGE_VERSION --mount type=bind,src=/tmp/service_account_key.json,dst=/tmp/service_account_key.json,readonly sh -c "uv run -m etl extract -c config/extract_action_sequence.yml -k /tmp/service_account_key.json"
```
