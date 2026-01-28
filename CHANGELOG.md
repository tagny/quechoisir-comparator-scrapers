
## 0.7.0

- Add Terraform infrastructure and GitHub Actions workflows to provision a GCP instance and build images with Terraform.
- Update CI workflows and gitignore to support Terraform files and syntax analysis.

## 0.6.0

- Add Airflow DAG for the internet box plans ETL pipeline with configuration files for orchestration.
- Improve internet box plans ETL code readability and enable logging in data utilities.
- Update CD workflows to build and push Docker images to docker.io.

## 0.5.0

- Add internet box plans ETL pipeline with Dockerfile.

## 0.4.0

- Add loading step of mobile phone plans ETL pipeline with BigQuery and Airflow orchestration.

## 0.3.0

- Add transformation step of mobile phone plans ETL pipeline with new data model and Airflow orchestration.

## 0.2.0

- Add extract step of mobile phone plans ETL pipeline with Dockerfile.
- Add Airflow-orchestrated ETL pipeline for mobile phone plans, including execution scripts and environment setup.
- Add start script to run the ETL pipeline in a tmux session.

## 0.1.0

 Added:

- README.md
- LICENSE
- CHANGELOG.md
- CONTRIBUTING.md
- VERSION
- .gitignore
- .actrc
- .pre-commit-config.yaml
- .bumpversion.toml
- .github/workflows/ci.yml
- .github/workflows/cd.yml
- .github/ISSUE_TEMPLATES/bug_report.md
- .github/ISSUE_TEMPLATES/feature_request.md
- .github/ISSUE_TEMPLATES/custom.md
- .github/pull_request_template.md
