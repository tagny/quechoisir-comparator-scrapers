"""This module scrap offers from the comparator energie-info.fr by running different
scenarios i.e. prospect profiles"""

import time
from dataclasses import dataclass
from typing import List, Literal
from urllib.parse import urlparse

from etl.data.raw_data_loading import BaseHtmlLoader
from etl.extract.selenium_setup import init_chrome_driver
from etl.logging_setup import logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class Action:
    """Represents how to fill a field of the dynamic search form"""

    label: str
    delay: float
    """Time to wait before acting"""
    tag: str
    type: str
    value: str
    value_text: str
    locator_name: Literal[
        "id",
        "xpath",
        "link text",
        "partial link text",
        "name",
        "tag name",
        "class name",
        "css selector",
    ]
    locator_value: str


class DynamicSearchBrowser:
    """Apply values of a scenario to fill the dynamic search form"""

    def __init__(
        self,
        form_actions: List[Action],
        data_loader: BaseHtmlLoader,
        base_url: str,
    ) -> None:
        self.base_url = base_url
        self.base_domain = urlparse(self.base_url).netloc
        self.driver = init_chrome_driver()
        self.actions = form_actions
        self.data_loader = data_loader

    def execute_action(self, action: Action):
        """execute a given action

        Args:
            action (Action): the action to execute
        """
        time.sleep(action.delay)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((action.locator_name, action.locator_value))
        )
        web_elt = self.driver.find_element(action.locator_name, action.locator_value)
        if action.type == "text":
            logger.debug("Fill text field...")
            web_elt.send_keys(action.value)
        elif action.tag == "select":
            logger.debug("Select an option...")
            select = Select(web_elt)
            logger.debug("Select options: %s", select.all_selected_options)
            select.select_by_value(action.value)
        elif action.tag == "input" and action.type == "range":
            logger.debug("Set range input...")
            # Set HTML5 range input via JS and fire input/change events so UI reacts
            try:
                logger.debug("Setting range input via JS to %s", action.value)
                logger.debug(
                    "Range input value before: %s", web_elt.get_attribute("value")
                )
                self.driver.execute_script(
                    f"arguments[0].value = {action.value};", web_elt
                )
                # Optionally, trigger input event to notify any listeners
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input'));", web_elt
                )
                logger.debug(
                    "Range input value after: %s", web_elt.get_attribute("value")
                )
            except Exception:
                logger.exception("JS range set failed, falling back to send_keys")
                logger.debug(
                    "Range input value before: %s", web_elt.get_attribute("value")
                )
                web_elt.send_keys(action.value)
                logger.debug(
                    "Range input value after: %s", web_elt.get_attribute("value")
                )
        else:
            # self.driver.execute_script("arguments[0].scrollIntoView();", web_elt)
            logger.debug("Click %s...", web_elt.tag_name)
            web_elt.click()

    def run(self):
        """runs the browser from filling the dynamic search form to getting the HTML
        of results"""
        self.driver.get(self.base_url)
        action_count = 0
        for action in self.actions:
            logger.info("Executes %s", action)
            try:
                self.execute_action(action)
            except Exception:
                logger.exception("Error")
                # break
            finally:
                # Save after each action for debugging
                html_content = self.driver.page_source
                self.data_loader.save_results(html_content)
                action_count += 1
        self.driver.close()  # terminates the loaded browser window
        self.driver.quit()  # ends the WebDriver application
