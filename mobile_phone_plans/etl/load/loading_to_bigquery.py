"""This module contains functions to load data into BigQuery for storing transformed
daily mobile phone plans data."""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv
from etl.data.transformed_data_loading import BaseJsonLoader
from etl.load.data_model import Base, MobilePhonePlanDatabaseTable
from etl.logging_setup import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = os.getenv("DATASET")


@dataclass
class BigQueryDataLoader:
    """Class to load data into BigQuery. It uses SQLAlchemy to interact with
    BigQuery."""

    transformed_data_loader: BaseJsonLoader
    project_id: str
    dataset: str
    service_account_key_json_path: str

    def flatten_plans_to_table_rows(
        self,
        plans: List[Dict[str, Any]],
    ) -> List[MobilePhonePlanDatabaseTable]:
        """Flatten and format plans data to match the table structure"""
        table_rows = []
        inserted_at = datetime.now()
        for plan in tqdm(plans, desc="Flattening plans for BigQuery insertion..."):
            # instantiate model and assign flattened attributes explicitly
            plan_table_row = MobilePhonePlanDatabaseTable()
            plan_table_row.scraping_date = plan.get("scraping_date")
            plan_table_row.inserted_at = inserted_at
            plan_table_row.name = plan.get("name")
            plan_table_row.description = plan.get("description")
            plan_table_row.operator_name = plan.get("operator_name")
            plan_table_row.price = plan.get("price")
            plan_table_row.internet_level = plan.get("internet_level")
            plan_table_row.call_included = plan.get("call_included")
            plan_table_row.sms_included = plan.get("sms_included")
            plan_table_row.mms_included = plan.get("mms_included")
            plan_table_row.internet_data_included = plan.get("internet_data_included")

            table_rows.append(plan_table_row)
        return table_rows

    def insert_plans(self) -> None:
        """Format and load plans scraped on the same date (scraping_date)
        to BigQuery"""
        transformed_plans = self.transformed_data_loader.load_plans()
        plans_table_rows = self.flatten_plans_to_table_rows(transformed_plans)
        if plans_table_rows:
            logger.info(
                "Create BigQuery engine with project ID %s and dataset %s",
                self.project_id,
                self.dataset,
            )
            if not self.project_id or not self.dataset:
                raise ValueError("Project ID or dataset not found")
            if not self.service_account_key_json_path:
                logger.warning(
                    "No service account key path provided." " Using default credentials"
                )
                engine = create_engine(f"bigquery://{self.project_id}/{self.dataset}")
            else:
                logger.info(
                    "Using service account credentials at %s",
                    self.service_account_key_json_path,
                )
                engine = create_engine(
                    f"bigquery://{self.project_id}/{self.dataset}",
                    credentials_path=self.service_account_key_json_path,
                )
            logger.info("Create table(s) (if not exists)")
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            session = Session()
            try:
                # Get the scraping_date from the first row to use for deletion
                # All rows processed in one run are expected to have the same
                # scraping_date
                scraping_date_to_delete = plans_table_rows[0].scraping_date
                if scraping_date_to_delete:
                    logger.info(
                        "Deleting existing rows with scraping_date = %s before"
                        " insertion...",
                        scraping_date_to_delete,
                    )
                    deleted_count = (
                        session.query(MobilePhonePlanDatabaseTable)
                        .filter_by(scraping_date=scraping_date_to_delete)
                        .delete()
                    )
                    logger.info("Deleted %d existing rows.", deleted_count)

                logger.info("Inserting %d rows into BigQuery...", len(plans_table_rows))
                session.add_all(plans_table_rows)
                session.commit()
                logger.info(
                    "Inserted %d rows into BigQuery table %s",
                    len(plans_table_rows),
                    MobilePhonePlanDatabaseTable.__tablename__,
                )
            except Exception as ex:
                logger.exception("Error when loading to BigQuery: %s", ex)
                session.rollback()
                raise ex
            finally:
                session.close()
        else:
            logger.warning("No plans to insert.")
