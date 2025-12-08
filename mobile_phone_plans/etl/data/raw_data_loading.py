"""This modules defines abstract classes and concrete implementations for loading
scraped HTML files to and from Local and cloud storage folders."""

import abc
import os
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv
from etl.logging_setup import logger
from google.api_core.exceptions import NotFound
from google.cloud import storage

load_dotenv()


@dataclass
class BaseHtmlLoader(abc.ABC):
    """Abstract base class for HTML files loaders"""

    raw_base_dir: str
    """Base directory where to save/load the HTML files"""
    scraping_date: datetime
    """Date of the scraping session """

    def get_offer_id(self, detail_html_path: str) -> str:
        """Get an offer id based on the path of its detail HTML file

        Args:
            detail_html_path (str): _description_

        Returns:
            str: _description_
        """
        return os.path.basename(detail_html_path).split(".")[0]

    def get_scraping_date_dir(self) -> str:
        """Returns the sub-directory path for the scraping date"""
        return os.path.join(
            self.raw_base_dir,
            self.scraping_date.strftime("%Y/%m/%d"),
        )

    def get_scraping_date_detail_dir(self) -> str:
        """Returns the base directory path for detail pages

        Returns:
            str: the base directory path for detail pages
        """
        return os.path.join(
            self.get_scraping_date_dir(),
            "detail",
        )

    def get_results_file_path(self) -> str:
        """Returns the file path where the results HTML file is stored

        Returns:
            str: the file path where the results HTML file is stored
        """
        date_sub_dir = self.get_scraping_date_dir()
        return os.path.join(date_sub_dir, "results.html")

    @abc.abstractmethod
    def save_results(self, results_html_content: str) -> None:
        """Saves the HTML content of the results page

        Args:
            results_html_content (str): HTML content of the results page
        """

    @abc.abstractmethod
    def load_results(self) -> str:
        """Loads and returns the HTML content of the results page

        Returns:
            str: HTML content of the results page
        """


@dataclass
class LocalHtmlLoader(BaseHtmlLoader):
    """HTML files loader saving/loading files to/from local filesystem"""

    def save_results(self, results_html_content: str) -> None:
        date_dir = self.get_scraping_date_dir()
        os.makedirs(date_dir, exist_ok=True)
        file_path = self.get_results_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(results_html_content)
        logger.info("Saved data at %s", file_path)

    def load_results(self) -> str:
        file_path = self.get_results_file_path()
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


@dataclass
class GoogleCloudStorageHtmlLoader(BaseHtmlLoader):
    """HTML files loader saving/loading files to/from Google Cloud Storage"""

    bucket_name: str
    """Name of the GCS bucket where to save/load the HTML files"""
    storage_client: storage.Client = None
    """GCS storage client"""
    service_account_key_json_path: str = None
    """local path to the key of the service account"""

    def __post_init__(self):
        if self.service_account_key_json_path:
            self.storage_client = storage.Client.from_service_account_json(
                self.service_account_key_json_path
            )
        else:
            # fallback to application default credentials
            self.storage_client = storage.Client()
        logger.debug("Initialized GCS storage client for bucket: %s", self.bucket_name)
        self.__check_bucket_exists()

    def __check_bucket_exists(self) -> None:
        """Checks that the GCS bucket exists to avoid creating it with a non-compliant
        name"""
        try:
            self.storage_client.get_bucket(self.bucket_name)
        except NotFound:
            raise ValueError(f"GCS bucket {self.bucket_name} does not exist") from None

    def save_results(self, results_html_content: str) -> None:
        # Ensure the bucket exists
        self.__check_bucket_exists()

        bucket = self.storage_client.bucket(self.bucket_name)

        blob_path = self.get_results_file_path()

        blob = bucket.blob(blob_path)
        blob.upload_from_string(results_html_content, content_type="text/html")
        logger.info("uploaded data at gs://%s/%s", self.bucket_name, blob_path)

    def load_results(self) -> str:
        """Loads and returns the HTML content of the results page

        Args:
            results_html_content (str): HTML content of the results page

        Returns:
            str: HTML content of the results page
        """
        # Ensure the bucket exists
        self.__check_bucket_exists()

        bucket = self.storage_client.bucket(self.bucket_name)

        blob_path = self.get_results_file_path()

        blob = bucket.blob(blob_path)
        try:
            logger.info("loading data from gs://%s/%s", self.bucket_name, blob_path)
            return blob.download_as_text(encoding="utf-8")
        except NotFound as exc:
            logger.exception(
                "GCS object gs://%s/%s not found", self.bucket_name, blob_path
            )
            raise exc
