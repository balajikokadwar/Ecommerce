from behave import when


@when('the user adds product "{product_name}" to the cart')
def step_add_product_to_cart(context, product_name):
    context.home_page.add_product_to_cart(product_name)


@when("the user navigates to the cart page")
def step_navigate_to_cart(context):
    context.home_page.go_to_cart()
