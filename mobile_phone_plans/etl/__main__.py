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
from etl.extract.downloading import Action, DynamicSearchBrowser
from etl.logging_setup import logger, setup_logger

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
RAW_BASE_DIR = os.getenv("RAW_BASE_DIR")
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


if __name__ == "__main__":
    try:
        app()
    except Exception as ex:
        logger.exception("Error while running the ETL pipeline step!")
        raise ex
    finally:
        # Close the client to close all associated handlers and flush logs
        from etl.logging_setup import cloud_logging_client

        if cloud_logging_client:
            logger.info("Closing Cloud Logging client...")
            cloud_logging_client.close()
