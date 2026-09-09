"""
Behave lifecycle hooks: driver setup/teardown, page object wiring, and
failure diagnostics (screenshots) shared by every feature/scenario.
"""
import os
from datetime import datetime
from pathlib import Path

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader
from utils.driver_factory import DriverFactory
from utils.logger import get_logger

logger = get_logger("environment")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SCREENSHOT_DIR = _PROJECT_ROOT / "reports" / "screenshots"


def before_all(context):
    logger.info("===== Test run starting =====")
    context.config_data = ConfigReader


def before_scenario(context, scenario):
    logger.info("Starting scenario: %s", scenario.name)
    context.driver = DriverFactory.get_driver(
        browser=ConfigReader.browser(), headless=ConfigReader.headless()
    )
    context.driver.set_page_load_timeout(ConfigReader.page_load_timeout())

    context.login_page = LoginPage(context.driver)
    context.home_page = HomePage(context.driver)
    context.cart_page = CartPage(context.driver)


def after_step(context, step):
    if step.status == "failed" and ConfigReader.screenshot_on_failure():
        _capture_screenshot(context, step)


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver is not None:
        driver.quit()
    logger.info("Finished scenario: %s [%s]", scenario.name, scenario.status.name)


def after_all(context):
    logger.info("===== Test run finished =====")


def _capture_screenshot(context, step) -> None:
    driver = getattr(context, "driver", None)
    if driver is None:
        return

    _SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_step_name = "".join(
        c if c.isalnum() else "_" for c in step.name
    )[:80]
    file_path = _SCREENSHOT_DIR / f"{timestamp}_{safe_step_name}.png"

    try:
        driver.save_screenshot(str(file_path))
        logger.error("Step failed: '%s'. Screenshot saved to %s", step.name, file_path)
    except Exception as exc:
        logger.warning("Could not capture failure screenshot: %s", exc)
