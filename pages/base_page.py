"""Base class providing common, wait-safe interactions for every page object."""
import time

from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.config_reader import ConfigReader
from utils.logger import get_logger


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, ConfigReader.explicit_wait())
        self.logger = get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        self.logger.info("Navigating to %s", url)
        self.driver.get(url)

    def find(self, locator) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def wait_for_visible(self, locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator, retries: int = 3) -> None:
        """Click, retrying briefly if a transient overlay (e.g. a loading
        spinner) intercepts the click or the element goes stale mid-click."""
        for attempt in range(1, retries + 1):
            try:
                self.wait_for_clickable(locator).click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if attempt == retries:
                    raise
                time.sleep(0.5)

    def type_text(self, locator, text: str) -> None:
        field = self.wait_for_visible(locator)
        field.clear()
        field.send_keys(text)

    def get_text(self, locator) -> str:
        return self.wait_for_visible(locator).text

    def is_visible(self, locator, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def wait_for_url_contains(self, fragment: str) -> bool:
        return self.wait.until(EC.url_contains(fragment))

    def wait_for_invisible(self, locator) -> None:
        """Wait until locator is either absent or invisible (e.g. loading spinners)."""
        try:
            self.wait.until(EC.invisibility_of_element_located(locator))
        except Exception:
            pass
