"""
Creates WebDriver instances for the browser under test.

Relies on Selenium 4's built-in Selenium Manager to resolve/download the
correct driver binary for the installed browser, so no separate driver
binaries or driver-manager dependency need to be maintained — this keeps the
framework portable across local machines and CI runners.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from utils.logger import get_logger

logger = get_logger(__name__)


class DriverFactory:
    """Builds a configured WebDriver for the requested browser."""

    @staticmethod
    def get_driver(browser: str, headless: bool):
        browser = (browser or "chrome").lower()
        logger.info("Creating '%s' driver (headless=%s)", browser, headless)

        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)

        elif browser == "edge":
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Edge(options=options)

        else:
            raise ValueError(f"Unsupported browser: '{browser}'")

        if not headless:
            driver.maximize_window()

        return driver
