"""
Data model for mobile phone plans.
"""

import re
from dataclasses import dataclass

import bs4.element
from bs4 import BeautifulSoup
from etl.data.utils import serialize_to_json_file


@dataclass
class MobilePhonePlan:
    scraping_date: str
    name: str
    description: str
    operator_name: str
    price: str
    internet_level: str
    call_included: str
    sms_included: str
    mms_included: str
    internet_data_included: str

    @classmethod
    def from_plan_element(cls, plan_element: bs4.element.Tag):
        """Create a MobilePhonePlan from a plan element."""
        benefit_elements = plan_element.find(
            "div",
            class_="qc-offer-card_content qc-fs-s qc-color-neutral-700 qc-list-styled",
        ).find_all("li")
        sms_mms_included = (
            None if len(benefit_elements) < 2 else benefit_elements[1].text.strip()
        )
        description = "\n".join(
            re.sub(r"\s+", " ", text.strip())
            for text in plan_element.find("div", id=lambda x: x and "details" in x)
            .text.strip()
            .split("\n")
            if text.strip() != ""
        )
        internet_data_from_description = description.split("Volume données")[-1].strip()
        return cls(
            scraping_date=None,
            name=plan_element.find(
                "article", class_="qc-offer-card qc-shadow-2 qc-round-2 qc-grid"
            )
            .find("h2", class_="qc-heading-xs qc-ff-base qc-fw-black qc-gap-1")
            .text.strip(),
            description=description,
            operator_name=plan_element.attrs["data-operateur"].strip(),
            price=re.sub(
                r"\s+",
                " ",
                plan_element.find("b", class_="qc-offer-card_price").text.strip(),
            ),
            internet_level=plan_element.attrs["data-internet"].strip(),
            call_included=re.sub(r"\s+", " ", benefit_elements[0].text.strip()),
            sms_included=(
                None
                if sms_mms_included is None
                else re.sub(r"\s+", " ", sms_mms_included.split("/")[0].strip())
            ),
            mms_included=(
                None
                if sms_mms_included is None
                else re.sub(r"\s+", " ", sms_mms_included.split("/")[1].strip())
            ),
            internet_data_included=(
                internet_data_from_description
                if len(benefit_elements) < 3
                else re.sub(r"\s+", " ", benefit_elements[2].text.strip())
            ),
        )


if __name__ == "__main__":
    plan_element_html_content = """
    <div class="qc-gap-5" data-operateur="cic-mobile" data-internet="4G"
     data-forfaits="['Engagement 12 mois']" data-dureeappelmn="9999999999"
      data-donneemobilemo="" data-price="29.99" data-comparateur-product="">
        <article class="qc-offer-card qc-shadow-2 qc-round-2 qc-grid">
            ...
        </article>
    </div>
    """
    plan_element = BeautifulSoup(plan_element_html_content, "html.parser").find("div")
    mobile_phone_plan = MobilePhonePlan.from_plan_element(plan_element)
    serialize_to_json_file(mobile_phone_plan, ".data/test.json")
