@cart
Feature: Add product to cart
  As a registered user of the e-commerce practice site
  I want to add a product to my shopping cart
  So that I can proceed towards checkout with the items I want to buy

  Background: The user logs into the application
    Given the user is on the login page
    When the user logs in with valid credentials
    Then the user should be navigated to the home page

  @smoke @regression
  Scenario: Add ZARA COAT 3 to the cart and verify it is present
    When the user adds product "ZARA COAT 3" to the cart
    And the user navigates to the cart page
    Then the cart should contain product "ZARA COAT 3"
