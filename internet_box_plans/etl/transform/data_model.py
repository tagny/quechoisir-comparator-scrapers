"""
Data model for internet box plans.
"""

import re
from dataclasses import dataclass

import bs4.element
from bs4 import BeautifulSoup
from etl.data.utils import serialize_to_json_file


@dataclass
class InternetBoxPlan:
    scraping_date: str
    updated_date: str
    name: str
    description: str
    operator_name: str
    price: str
    call_to_fixed_line_included: str
    call_to_mobile_included: str
    tv_included: str
    plan_type: str  # "FIBRE" or "ADSL" or "4G"
    discount_plans: str
    engagement_period: str
    tv_channels: int
    recorder_storage: int
    installation_cost: str
    cancellation_cost: str
    cloud_storage: int

    @classmethod
    def from_plan_element(
        cls, plan_element: bs4.element.Tag, data_modal_element: bs4.element.Tag
    ):
        """Create a InternetBoxPlan from a plan element."""
        benefit_elements = plan_element.find(
            "div",
            class_="qc-offer-card_content qc-fs-s qc-color-neutral-700 qc-list-styled",
        ).find_all("li")
        call_to_mobile_included = None
        call_to_fixed_line_included = None
        tv_included = None
        plan_type = None
        description = ""
        for benefit_element in benefit_elements:
            benefit_text = benefit_element.text.strip()
            description += benefit_text + "\n"
            if "Appels mobiles" in benefit_text:
                call_to_mobile_included = benefit_text
            elif "Appels fixes" in benefit_text:
                call_to_fixed_line_included = benefit_text
            elif "Télévision" in benefit_text:
                tv_included = benefit_text
            elif "Offre" in benefit_text:
                plan_type = benefit_text
        more_info_elements = data_modal_element.find_all("li")
        engagement_period = None
        tv_channels = None
        recorder_storage = None
        installation_cost = None
        cancellation_cost = None
        cloud_storage = None
        discount_plans = None
        for more_info_element in more_info_elements:
            more_info_text = more_info_element.text.strip()
            description += more_info_text + "\n"
            if "Engagement" in more_info_text:
                engagement_period = more_info_text.split("Engagement : ")[-1].strip()
            elif "Chaînes" in more_info_text:
                tv_channels = more_info_text.split("Chaînes : ")[-1].strip()
            elif "Enregistreur" in more_info_text:
                recorder_storage = more_info_text.split("Enregistreur : ")[-1].strip()
            elif "Raccordement" in more_info_text:
                installation_cost = more_info_text.split("Raccordement : ")[-1].strip()
            elif "Résiliation" in more_info_text:
                cancellation_cost = more_info_text.split("Résiliation : ")[-1].strip()
            elif "Cloud" in more_info_text:
                cloud_storage = more_info_text.split("Cloud : ")[-1].strip()
            elif "Promo" in more_info_text:
                discount_plans = more_info_text.split("Promo : ")[-1].strip()

        return cls(
            scraping_date=None,
            updated_date=None,
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
            plan_type=plan_type,
            call_to_fixed_line_included=call_to_fixed_line_included,
            call_to_mobile_included=call_to_mobile_included,
            tv_included=tv_included,
            discount_plans=discount_plans,
            engagement_period=engagement_period,
            tv_channels=tv_channels,
            recorder_storage=recorder_storage,
            installation_cost=installation_cost,
            cancellation_cost=cancellation_cost,
            cloud_storage=cloud_storage,
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
    mobile_phone_plan = InternetBoxPlan.from_plan_element(plan_element)
    serialize_to_json_file(mobile_phone_plan, ".data/test.json")
