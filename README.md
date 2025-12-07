# quechoisir-comparator-scrapers
Implementing ETL pipelines to daily scrap the free comparators of the website www.quechoisir.org.

The data is stored to a cloud storage service (e.g. Google cloud BigQuery) and the logs are streamed to a cloud logging service (e.g. Google cloud Logging).

## Scraped comparator data

### Mobile phone plans in France

The URL https://www.quechoisir.org/comparateur-forfait-mobile-n43896/ is a free public comparator for a mobile phone plan in France.

We will start by scraping this URL and storing the data in a cloud storage service (e.g. Google cloud BigQuery).

The web page is updated daily, so the ETL pipeline will be scheduled to run daily.

The Airflow ETL pipeline will be run daily by the start script that will:

1. start a virtual machine on cloud compute service (e.g. Google cloud Compute Engine)
2. start airflow standalone server
3. run the ETL pipeline to download the web page to:
    - cloud storage
    - transform to json files on cloud storage
    - load the data to BigQuery
4. stop the airflow standalone server
5. stop the virtual machine

## Project structure

```shell
quechoisir-comparator-scrapers/
├── .data/                                                # Data directory
├── .logs/                                                # Logs directory
├── src/                                                  # Source code directory
├── tests/                                                # Tests directory
├── .gitignore                                            # Git ignore file
├── .actrc                                                # Act configuration file
├── .pre-commit-config.yaml                               # Pre-commit configuration file
├── .bumpversion.toml                                     # Bumpversion configuration file
├── README.md                                             # README file
├── LICENSE                                               # License file
├── CHANGELOG.md                                          # Changelog file
├── CONTRIBUTING.md                                       # Contributing file
├── VERSION                                               # Version file
├── .github/                                              # GitHub directory
    ├── ISSUE_TEMPLATE/                                  # Issue templates directory
        ├── bug_report.md                                 # Bug report issue template
        ├── feature_request.md                            # Feature request issue template
        ├── custom.md                                     # Custom issue template
    ├── workflows/                                        # Workflows directory
        ├── ci.yml                                        # CI workflow
        ├── cd.yml                                        # CD workflow
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Changelog

Please read [CHANGELOG.md](CHANGELOG.md) for details on the changes made to this project.

## License

This project is licensed under the Unlicense - see the [LICENSE](LICENSE) file for details.
