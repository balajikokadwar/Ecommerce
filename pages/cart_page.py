"""Page Object for the Cart page (/#/dashboard/cart)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    CART_CONTAINER = (By.CSS_SELECTOR, "div.cart")
    CART_ITEM_NAMES = (By.CSS_SELECTOR, "li.items h3")

    def is_cart_page_displayed(self) -> bool:
        return self.is_visible(self.CART_CONTAINER, timeout=10)

    def get_cart_product_names(self) -> list:
        if not self.is_visible(self.CART_ITEM_NAMES, timeout=5):
            return []
        return [element.text.strip() for element in self.find_all(self.CART_ITEM_NAMES)]

    def is_product_in_cart(self, product_name: str) -> bool:
        return product_name.strip().upper() in [
            name.upper() for name in self.get_cart_product_names()
        ]
