# Purchases — behaviour specification. Sources: Purchases spec v3 (gate/specs/purchases-v3.md); Figma frames 210:14, 210:31, 210:44.
Feature: Purchases
  A person records purchases and refunds and sees the balance.

  Rule: The balance is the sum of purchases minus refunds

    @TS_LED_001 @happy_path @covered-by:TransactionStoreTests.testAddIncreasesBalance
    Scenario: The balance adds up the purchases
      Given two purchases of 5.00 and 7.50
      When the person opens the balance
      Then the total shows 12.50

    @TS_LED_002 @happy_path @automation-pending
    Scenario: A refund is returned to the balance
      Given a purchase of 10.00 and a refund of 4.00
      When the person opens the balance
      Then the total shows 6.00

  Rule: The daily limit stops new purchases until it resets

    @TS_LED_003 @validation @automation-pending
    Scenario: The limit banner offers "Contact support"
      Given the daily limit is reached
      When the person opens Add purchase
      Then the banner "You've reached today's limit." shows with "Contact support"

    @TS_LED_004 @validation @automation-pending
    Scenario: The sixth purchase of the day is refused
      Given five purchases were recorded today
      When the person records another purchase
      Then the app refuses it without asking the server
      And the limit banner shows

  Rule: Other

    @TS_LED_005 @happy_path @automation-pending
    Scenario: The month's purchases export as a CSV file
      Given purchases exist this month
      When the person taps "Export"
      Then a CSV file is shared

    @TS_LED_006 @validation @automation-pending
    Scenario: A purchase note longer than 140 characters is refused
      Given the person types a note of 141 characters
      When the person saves the purchase
      Then the note is refused
