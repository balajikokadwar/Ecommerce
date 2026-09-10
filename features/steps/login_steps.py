from behave import given, when, then

from utils.config_reader import ConfigReader

# steps folder
@given("the user is on the login page")
def step_open_login_page(context):
    context.login_page.load()


@when("the user logs in with valid credentials")
def step_login_with_valid_credentials(context):
    context.login_page.login(
        ConfigReader.login_email(), ConfigReader.login_password()
    )


@then("the user should be navigated to the home page")
def step_verify_home_page(context):
    assert context.home_page.is_home_page_displayed(), (
        "Home page was not displayed after login — product cards not found."
    )
