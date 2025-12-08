"""main module for mobile phone plans ETL"""

import logging
import os
from datetime import datetime

import click
import yaml
from dotenv import load_dotenv
from etl.data.raw_data_loading import (
    GoogleCloudStorageHtmlLoader,
    LocalHtmlLoader,
)
from etl.data.transformed_data_loading import (
    GoogleCloudStorageJsonLoader,
    LocalJsonLoader,
)
from etl.extract.downloading import Action, DynamicSearchBrowser
from etl.load.loading_to_bigquery import BigQueryDataLoader
from etl.logging_setup import logger, setup_logger
from etl.transform.daily_plans_transformation import DailyPlansTransformer

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
RAW_BASE_DIR = os.getenv("RAW_BASE_DIR")
TRANSFORMED_BASE_DIR = os.getenv("TRANSFORMED_BASE_DIR")
DATASET = os.getenv("DATASET")
BASE_URL = os.getenv("BASE_URL")
PROJECT_ID = os.getenv("PROJECT_ID")
ETL_STEP_EXTRACT = "1-EXTRACT"
ETL_STEP_TRANSFORM = "2-TRANSFORM"
ETL_STEP_LOAD = "3-LOAD"


def get_suitable_raw_data_loader(
    bucket: str,
    raw_base_dir: str,
    service_account_json_path: str,
    scraping_date: datetime,
) -> LocalHtmlLoader | GoogleCloudStorageHtmlLoader:
    """Instantiates a suitable HTML loader based on the provided"""
    if bucket and service_account_json_path:
        return GoogleCloudStorageHtmlLoader(
            bucket_name=bucket,
            raw_base_dir=raw_base_dir,
            service_account_key_json_path=service_account_json_path,
            scraping_date=scraping_date,
        )
    return LocalHtmlLoader(
        raw_base_dir=raw_base_dir,
        scraping_date=scraping_date,
    )


def get_suitable_transformed_data_loader(
    bucket: str,
    transformed_base_dir: str,
    service_account_json_path: str,
    scraping_date: datetime,
) -> LocalJsonLoader | GoogleCloudStorageJsonLoader:
    """Initializes a suitable JSON loader based on the"""
    logger.info(
        "Initializing JSON loader with bucket=%s, service_account_json_path=%s",
        bucket,
        service_account_json_path,
    )
    if bucket and service_account_json_path:
        return GoogleCloudStorageJsonLoader(
            bucket_name=bucket,
            transformed_base_dir=transformed_base_dir,
            service_account_key_json_path=service_account_json_path,
            scraping_date=scraping_date,
        )
    return LocalJsonLoader(
        transformed_base_dir=transformed_base_dir,
        scraping_date=scraping_date,
    )


@click.group()
def app():
    pass


@app.command()
@click.option(
    "-c",
    "--config-path",
    help="Path to the YAML configuration file defining action sequences per prospect"
    " profile",
    required=True,
)
@click.option(
    "-k",
    "--service-account-key-path",
    help="Path to the service account key JSON file",
    required=False,
)
def extract(
    config_path: str,
    service_account_key_path: str,
):
    """ETL extract command to scrape mobile phone plans for a given prospect
      profile scenario.
    Args:
        config_path (str): path to the YAML configuration file defining action
          sequences per prospect profile
        service_account_key_path (str): Path to the service account key JSON file
    """
    setup_logger(
        level=logging.INFO,
        etl_step=ETL_STEP_EXTRACT,
        service_account_key_json_path=service_account_key_path,
    )
    logger.info("ETL pipeline - step extract")
    if not os.path.exists(config_path):
        logger.error("Config file not found at %s", config_path)
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, mode="r", encoding="utf-8") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    dict_actions = config["action_sequence"]
    obj_actions = [Action(**action_config) for action_config in dict_actions]
    logger.debug("Action sequence to execute: %s", obj_actions)
    scraping_date = datetime.now()
    data_loader = get_suitable_raw_data_loader(
        BUCKET_NAME,
        RAW_BASE_DIR,
        service_account_key_path,
        scraping_date,
    )
    browser = DynamicSearchBrowser(
        obj_actions,
        base_url=BASE_URL,
        data_loader=data_loader,
    )
    browser.run()
    logger.info("End of ETL pipeline step - extract")


@app.command()
@click.option(
    "-d",
    "--scraping-date",
    help="The date in YYYY/MM/DD format when the raw HTML files where scraped"
    " to identify their folder.",
)
@click.option(
    "-k",
    "--service-account-key-path",
    help="Path to the service account key JSON file",
)
def transform(
    scraping_date: str,
    service_account_key_path: str,
):
    """Transform step of the ETL pipeline scraping mobile phone plans

    Args:
        scraping_date (str): The date in YYYY/MM/DD format when the raw HTML
         files where scraped to identify their folder.
        service_account_key_path (str): Path to the service account key JSON file
    """
    setup_logger(
        level=logging.INFO,
        etl_step=ETL_STEP_TRANSFORM,
        service_account_key_json_path=service_account_key_path,
    )
    logger.info(
        "ETL pipeline - step transform - on scraping_date = %s",
        scraping_date,
    )

    scraping_date = datetime.strptime(scraping_date, "%Y/%m/%d")

    raw_data_loader = get_suitable_raw_data_loader(
        BUCKET_NAME,
        RAW_BASE_DIR,
        service_account_key_path,
        scraping_date,
    )

    transformed_data_loader = get_suitable_transformed_data_loader(
        BUCKET_NAME,
        TRANSFORMED_BASE_DIR,
        service_account_key_path,
        scraping_date,
    )

    transformer = DailyPlansTransformer(
        scraping_date=scraping_date,
        raw_data_loader=raw_data_loader,
        transformed_data_loader=transformed_data_loader,
    )
    transformer.transform()
    logger.info("End of ETL pipeline step - transform")


@app.command()
@click.option(
    "-d",
    "--scraping-date",
    help="The date when the raw HTML files where scraped to identify their folder.",
)
@click.option(
    "-k",
    "--service-account-key-path",
    help="Path to the service account key JSON file",
)
def load(
    scraping_date: str,
    service_account_key_path: str,
):
    """Load step of the ETL pipeline scraping mobile phone plans

    Args:
        predefined_profile_id (str): the id of the predefined prospect profile
         to use (defined in fr_energy_offers_scraper.data.prospect_predefined_profiles).
        scraping_date (str): The date when the raw HTML files where scraped
         to identify their folder.
        service_account_key_path (str): Path to the service account key JSON file
    """
    setup_logger(
        level=logging.INFO,
        etl_step=ETL_STEP_LOAD,
        service_account_key_json_path=service_account_key_path,
    )
    logger.info(
        "ETL pipeline - step load - on scraping_date = %s",
        scraping_date,
    )

    scraping_date = datetime.strptime(scraping_date, "%Y/%m/%d")
    transformed_data_loader = get_suitable_transformed_data_loader(
        BUCKET_NAME,
        TRANSFORMED_BASE_DIR,
        service_account_key_path,
        scraping_date,
    )

    bq_loader = BigQueryDataLoader(
        transformed_data_loader=transformed_data_loader,
        project_id=PROJECT_ID,
        dataset=DATASET,
        service_account_key_json_path=service_account_key_path,
    )

    bq_loader.insert_plans()
    logger.info("End of ETL pipeline step - load")


if __name__ == "__main__":
    try:
        app()
    except Exception as ex:
        logger.exception("Error while running the ETL pipeline step: %s", ex)
        raise ex
    finally:
        # Close the client to close all associated handlers and flush logs
        from etl.logging_setup import cloud_logging_client

        if cloud_logging_client:
            logger.info("Closing Cloud Logging client...")
            cloud_logging_client.close()
