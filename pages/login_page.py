"""Page Object for the Login page (/#/auth/login)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class LoginPage(BasePage):
    EMAIL_INPUT = (By.ID, "userEmail")
    PASSWORD_INPUT = (By.ID, "userPassword")
    LOGIN_BUTTON = (By.ID, "login")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger, .toast-error")

    def load(self) -> None:
        self.open(ConfigReader.base_url())
        self.wait_for_visible(self.EMAIL_INPUT)

    def enter_email(self, email: str) -> None:
        self.type_text(self.EMAIL_INPUT, email)

    def enter_password(self, password: str) -> None:
        self.type_text(self.PASSWORD_INPUT, password)

    def click_login(self) -> None:
        self.click(self.LOGIN_BUTTON)

    def login(self, email: str, password: str) -> None:
        self.logger.info("Logging in as '%s'", email)
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)
