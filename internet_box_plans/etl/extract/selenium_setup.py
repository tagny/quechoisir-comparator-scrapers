"""This module centralises the setup of selenium"""

import shutil
import tempfile

from etl.logging_setup import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def init_chrome_driver() -> webdriver.Chrome:
    """Init Chrome web driver

    Returns:
        webdriver.Chrome: the initialized web driver
    """
    logger.debug("Initializing the Chrome Web driver...")
    chrome_options = Options()
    # Essential for headless in restricted environments
    # Use modern headless (Chrome 109+)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--log-path=.logs/chromedriver.log")
    # Avoid /tmp issues by specifying a clean, writable user data dir
    tmp_user_dir = tempfile.mkdtemp(suffix="_fr-energy-offers-scraper")
    logger.debug("Using temporary Chrome user data dir at %s", tmp_user_dir)
    chrome_options.add_argument(f"--user-data-dir={tmp_user_dir}")
    # Optional, but sometimes helps
    chrome_options.add_argument("--remote-debugging-port=9222")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome Web driver initialized")
        return driver
    except Exception as ex:
        logger.exception("Error when init web driver: %s", ex)
        # Clean up the temporary user data dir
        logger.debug("Clean up the temporary user data dir")
        shutil.rmtree(tmp_user_dir, ignore_errors=True)
        # raise the exception
        raise ex
