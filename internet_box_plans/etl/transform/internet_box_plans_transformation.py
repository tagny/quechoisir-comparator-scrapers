"""
Internet Box plans transformation.
"""

from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup
from etl.data.raw_data_loading import BaseHtmlLoader, LocalHtmlLoader
from etl.data.transformed_data_loading import BaseJsonLoader, LocalJsonLoader
from etl.logging_setup import logger
from etl.transform.data_model import InternetBoxPlan


@dataclass
class InternetBoxPlansTransformer:
    """This class is responsible for transforming the raw data into a list
    of InternetBoxPlan objects and saving them to a JSON file."""

    scraping_date: datetime
    """When the offer was scraped"""
    raw_data_loader: BaseHtmlLoader
    """Loader for the raw data"""
    transformed_data_loader: BaseJsonLoader
    """Loader for the transformed data"""

    def transform(self) -> None:
        """Transform the raw data into a list of InternetBoxPlan objects."""
        soup = BeautifulSoup(self.raw_data_loader.load_results(), "html.parser")
        plans = []
        plan_articles = soup.find(
            "div", class_="qc-comparateur_products qc-gap-9"
        ).find_all("article", class_="qc-offer-card qc-shadow-2 qc-round-2 qc-grid")
        updated_date = str(
            soup.find("div", class_="qc-gap-4 qc-comparateur_subinfo")
            .find("time")
            .attrs["datetime"]
        )
        for plan_article in plan_articles:
            plan_div_element = plan_article.find_parent("div")
            data_modal_id = plan_article.find("button").attrs["data-modal-content"]
            data_modal_element = soup.find("div", id=data_modal_id)
            try:
                plan = InternetBoxPlan.from_plan_element(plan_div_element, data_modal_element)
                plan.scraping_date = self.scraping_date
                plan.updated_date = updated_date
                plans.append(plan)
            except Exception as ex:
                logger.exception(
                    "Failed to transform plan element %s: %s", plan_div_element, ex
                )
        self.transformed_data_loader.save_plans(plans)


if __name__ == "__main__":
    scraping_date = datetime.strptime("2026/01/04", "%Y/%m/%d")
    transformer = InternetBoxPlansTransformer(
        scraping_date=scraping_date,
        raw_data_loader=LocalHtmlLoader(
            raw_base_dir=".data/internet-box-plans/raw/", scraping_date=scraping_date
        ),
        transformed_data_loader=LocalJsonLoader(
            transformed_base_dir=".data/internet-box-plans/transformed/",
            scraping_date=scraping_date,
        ),
    )
    transformer.transform()
