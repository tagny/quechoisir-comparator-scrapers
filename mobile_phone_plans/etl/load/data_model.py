"""ORM model for mobile phone plans"""

import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

# --- Step 1: Define ORM Model ---
Base = declarative_base()


class MobilePhonePlanDatabaseTable(Base):
    __tablename__ = "tbl_mobile_phone_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scraping_date = Column(DateTime, nullable=False)
    inserted_at = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    operator_name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    internet_level = Column(String, nullable=True)
    call_included = Column(String, nullable=False)
    sms_included = Column(String, nullable=False)
    mms_included = Column(String, nullable=True)
    internet_data_included = Column(String, nullable=True)
