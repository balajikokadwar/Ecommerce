from behave import then


@then('the cart should contain product "{product_name}"')
def step_verify_product_in_cart(context, product_name):
    assert context.cart_page.is_cart_page_displayed(), "Cart page did not load."
    assert context.cart_page.is_product_in_cart(product_name), (
        f"Expected '{product_name}' in cart, but found: "
        f"{context.cart_page.get_cart_product_names()}"
    )
