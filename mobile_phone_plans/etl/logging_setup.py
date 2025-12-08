"""This sets up the logging for the whole package"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import google.cloud.logging
import pytz
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from google.oauth2 import service_account

PROJECT_NAME = "quechoisir-mobile-phone-plans-etl"
logger = logging.getLogger(PROJECT_NAME)
logger.setLevel(logging.DEBUG)

# Define the custom format string
BASE_MSG_FORMAT = (
    "[%(name)s|%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s] %(message)s"
)
ETL_STEP_MSG_FORMAT = (
    "[%(name)s|{etl_step}|%(asctime)s|%(levelname)s"
    "|%(filename)s:%(lineno)s] %(message)s"
)
DATE_FORMAT = "%H:%M:%S"
LOG_DIR = "./.logs"
os.makedirs(LOG_DIR, exist_ok=True)

cloud_logging_client = None


def setup_logger(
    level=logging.DEBUG, etl_step=None, service_account_key_json_path=None
):
    global cloud_logging_client
    """Set up the logger with file and console handlers."""
    logger.setLevel(level)
    # --- clear handlers ---
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    # --- Avoid adding multiple handlers if the logger is reused (e.g., in modules) ---
    if not logger.handlers:
        formatter = logging.Formatter(
            (
                BASE_MSG_FORMAT
                if not etl_step
                else ETL_STEP_MSG_FORMAT.format(etl_step=etl_step)
            ),
            datefmt=DATE_FORMAT,
        )

        # --- add file handler ---
        file_handler = RotatingFileHandler(
            f"{LOG_DIR}/{PROJECT_NAME}.log",
            maxBytes=10000,
            backupCount=1,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # --- set up logging to console ---
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # set a format which is simpler for console use
        console_handler.setFormatter(formatter)
        # add the handler to the root logger
        logger.addHandler(console_handler)

        # --- add cloud logging handler ---
        try:
            if service_account_key_json_path is None:
                logger.warning(
                    "No service account key path provided,"
                    " skipping cloud logging handler"
                )
                pass
            else:
                # 1. Load credentials from the service account key file
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_key_json_path
                )
                # 2. Create the Cloud Logging client using the loaded credentials
                cloud_logging_client = google.cloud.logging.Client(
                    credentials=credentials
                )
                logger.info("Cloud Logging client created successfully!")

                # 3. Set up a handler to send logs to Cloud Logging
                cloud_handler = CloudLoggingHandler(
                    cloud_logging_client, logger_name=PROJECT_NAME
                )
                cloud_handler.setLevel(logging.INFO)
                cloud_handler.setFormatter(formatter)
                logger.addHandler(cloud_handler)
        except Exception as ex:
            logger.exception(
                "Error when adding cloud logging handler with %s: %s",
                service_account_key_json_path,
                ex,
            )


setup_logger()
TODAY_DATE = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d-%m-%Y %H:%M:%S")
logger.info("Logger set up successfully on %s!", TODAY_DATE)
