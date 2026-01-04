"""ORM model for internet box plans"""

import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from google.cloud import bigquery

Base = declarative_base()


class InternetBoxPlanDatabaseTable(Base):
    __tablename__ = "tbl_internet_box_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scraping_date = Column(DateTime, nullable=False)
    inserted_at = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    operator_name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    call_to_fixed_line_included = Column(String, nullable=True)
    call_to_mobile_included = Column(String, nullable=True)
    tv_included = Column(String, nullable=True)
    plan_type = Column(String, nullable=True)
    discount_plans = Column(String, nullable=True)
    engagement_period = Column(String, nullable=True)
    tv_channels = Column(String, nullable=True)
    recorder_storage = Column(String, nullable=True)
    installation_cost = Column(String, nullable=True)
    cancellation_cost = Column(String, nullable=True)
    cloud_storage = Column(String, nullable=True)

    __table_args__ = (
        {
            "bigquery_time_partitioning": bigquery.TimePartitioning(
                type_="MONTH",           # Choices: "DAY", "MONTH", "YEAR", "HOUR"
                field="scraping_date",    # The specific column to use
                expiration_ms=None,    # Optional: data retention in milliseconds
            ),
            "bigquery_require_partition_filter": True, # Optional: forces users to filter by date
        }
    )
