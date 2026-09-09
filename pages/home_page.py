"""Page Object for the Home / product listing page (/#/dashboard/dash)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    PRODUCT_CARDS = (By.CSS_SELECTOR, "div.card")
    CART_ICON = (By.CSS_SELECTOR, "button[routerlink='/dashboard/cart']")
    CART_COUNT_BADGE = (By.CSS_SELECTOR, "button[routerlink='/dashboard/cart'] label")
    LOADING_SPINNER = (By.CSS_SELECTOR, ".ngx-spinner-overlay")

    @staticmethod
    def _product_card_locator(product_name: str):
        return (
            By.XPATH,
            f"//div[@class='card'][.//h5/b[normalize-space()="
            f"'{product_name}']]",
        )

    @staticmethod
    def _add_to_cart_button_locator():
        return (By.XPATH, ".//button[contains(., 'Add To Cart')]")

    def is_home_page_displayed(self) -> bool:
        return self.is_visible(self.PRODUCT_CARDS, timeout=10)

    def add_product_to_cart(self, product_name: str) -> None:
        self.logger.info("Adding product '%s' to cart", product_name)
        self.wait_for_invisible(self.LOADING_SPINNER)
        card = self.wait_for_visible(self._product_card_locator(product_name))
        add_to_cart_button = card.find_element(*self._add_to_cart_button_locator())
        add_to_cart_button.click()

    def get_cart_count(self) -> str:
        return self.get_text(self.CART_COUNT_BADGE)

    def go_to_cart(self) -> None:
        self.logger.info("Navigating to the cart page")
        self.wait_for_invisible(self.LOADING_SPINNER)
        self.click(self.CART_ICON)
