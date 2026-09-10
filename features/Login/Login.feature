@login
Feature: Login
  As a registered user of the e-commerce practice site

  @smoke
  Scenario: Add ZARA COAT 3 to the cart and verify it is present
    Given the user is on the login page
    When the user logs in with valid credentials
    Then the user should be navigated to the home page
