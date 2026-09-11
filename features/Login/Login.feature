@login
Feature: Login
  As a registered user of the e-commerce practice site

  @smoke
  Scenario: Login to app using valid credentials
    Given the user is on the login page
    When the user logs in with valid credentials
    Then the user should be navigated to the home page
