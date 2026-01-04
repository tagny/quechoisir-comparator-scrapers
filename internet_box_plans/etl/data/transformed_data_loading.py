"""This modules defines abstract classes and concrete implementations for loading
transformed JSON data files to and from Local and cloud storage folders."""

import abc
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv
from etl.data.utils import (
    custom_json_encoder,
)
from etl.logging_setup import logger
from google.api_core.exceptions import NotFound
from google.cloud import storage

load_dotenv()


@dataclass
class BaseJsonLoader(abc.ABC):
    """Abstract base class for transformed JSON data"""

    transformed_base_dir: str
    """Base directory where to save/load the JSON files"""
    scraping_date: datetime
    """Date of the scraping session """

    def get_scraping_date_dir(self) -> str:
        """Returns the sub-directory path for the scraping date"""
        return os.path.join(
            self.transformed_base_dir,
            self.scraping_date.strftime("%Y/%m/%d"),
        )

    def get_plans_jsonline_file_path(self) -> str:
        """Returns the file path where the plans JSON-line file is stored

        Returns:
            str: the file path where the plans JSON-line file is stored
        """
        date_sub_dir = self.get_scraping_date_dir()
        return os.path.join(date_sub_dir, "plans.jsonl")

    @abc.abstractmethod
    def save_plans(self, data: List[Dict[str, Any]]) -> None:
        pass

    @abc.abstractmethod
    def load_plans(self) -> List[Dict[str, Any]]:
        pass


@dataclass
class LocalJsonLoader(BaseJsonLoader):
    """Transformed JSON files loader saving/loading files to/from local filesystem"""

    def save_plans(self, data: List[Dict[str, Any]]) -> None:
        plan_counter = 0
        output_jsonl_path = self.get_plans_jsonline_file_path()
        os.makedirs(os.path.dirname(output_jsonl_path), exist_ok=True)
        with open(output_jsonl_path, "w", encoding="utf-8") as writer:
            for plan in data:
                json.dump(custom_json_encoder(plan), writer, ensure_ascii=False)
                writer.write("\n")
                plan_counter += 1
        logger.info(
            "%d Plans data extracted and saved to %s", plan_counter, output_jsonl_path
        )

    def load_plans(self) -> List[Dict[str, Any]]:
        jsonl_path = self.get_plans_jsonline_file_path()
        plans = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                plans.append(json.loads(line))
        return plans


@dataclass
class GoogleCloudStorageJsonLoader(BaseJsonLoader):
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

    def _get_bucket(self):
        return self.storage_client.bucket(self.bucket_name)

    def save_plans(self, data: List[Dict[str, Any]]) -> None:
        plan_counter = 0
        # Build jsonl content in memory and upload to GCS
        lines = []
        for plan in data:
            lines.append(json.dumps(custom_json_encoder(plan), ensure_ascii=False))
            plan_counter += 1
        content = "\n".join(lines) + ("\n" if lines else "")
        blob_name = self.get_plans_jsonline_file_path()
        blob = self._get_bucket().blob(blob_name)
        blob.upload_from_string(content, content_type="application/json; charset=utf-8")
        logger.info(
            "%d Plans data extracted and saved to gs://%s/%s",
            plan_counter,
            self.bucket_name,
            blob_name,
        )

    def load_plans(self) -> List[Dict[str, Any]]:
        jsonl_path = self.get_plans_jsonline_file_path()
        blob_name = jsonl_path
        blob = self._get_bucket().blob(blob_name)
        if not blob.exists():
            raise FileNotFoundError(f"gs://{self.bucket_name}/{blob_name} not found")
        content = blob.download_as_text(encoding="utf-8")
        plans = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            plans.append(json.loads(line))
        return plans
