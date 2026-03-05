# Student Class Implementation

## Problem Statement

You need to implement a JavaScript class called `BankAccount` that manages bank account information and transactions. The class should handle basic account data and provide methods for deposit, withdrawal, and balance display.

## Class Structure

The Student class should contain:

1. A constructor that initializes:
    - accountHolder (string)
    - balance (number)

2. Different methods:
    - deposit()
    - withdraw()
    - checkBalance()

## Detailed Requirements

### Constructor
```javascript
constructor(accountHolder, initialBalance)
```

- Initializes a new BankAccount instance with:
    - accountHolder: account holder's name (string)
    - initialBalance: initial account balance (number)

Methods
1. deposit(amount)
    
    - Purpose: Adds the specified amount to the account balance
    - Parameters: amount (number)
    - Returns:

        - true if the amount is valid (greater than 0)
        - false if the amount is invalid

    - Behavior: Only adds the amount if it's valid

2. withdraw(amount)

    - Purpose: Subtracts the specified amount from the account balance
    - Parameters: amount (number)
    - Returns:

        - true if the amount is valid (greater than 0 and less than the current balance)
        - false if the amount is invalid

    - Behavior: Only subtracts the amount if it's valid

3. checkBalance()

    - Purpose: Returns the current account balance
    - Returns:

        - Current account balance
        - 0 if the balance is negative

Do not remove the existing HTML elements or change their IDs or edit the existing JavaScript code. You can add new JavaScript code as needed.