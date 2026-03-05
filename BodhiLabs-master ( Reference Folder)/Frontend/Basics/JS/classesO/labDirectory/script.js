// TODO: Complete the BankAccount class implementation
class BankAccount {
    constructor(accountHolder, initialBalance) {
        // TODO: Initialize the account with accountHolder and initialBalance
        // Remember to create this.accountHolder and this.balance properties
    }

    deposit(amount) {
        // TODO: Implement deposit method
        // Return true if successful (amount > 0)
        // Return false if unsuccessful (amount <= 0)
        // Remember to update this.balance if successful
    }

    withdraw(amount) {
        // TODO: Implement withdraw method
        // Return true if successful (0 < amount <= balance)
        // Return false if unsuccessful (amount <= 0 or amount > balance)
        // Remember to update this.balance if successful
    }

    checkBalance() {
        // TODO: Implement checkBalance method
        // Return the current balance
    }
}

// !!!! DO NOT MODIFY THE CODE BELOW THIS LINE !!!!
let currentAccount = null;

document.getElementById('createAccount').addEventListener('click', () => {
    const holder = document.getElementById('accountHolder').value;
    const balance = parseFloat(document.getElementById('initialBalance').value);
    
    if (holder && !isNaN(balance) && balance >= 0) {
        currentAccount = new BankAccount(holder, balance);
        document.getElementById('accountOperations').classList.remove('hidden');
        updateAccountInfo();
        document.getElementById('message').textContent = 'Account created successfully!';
    } else {
        document.getElementById('message').textContent = 
            'Please provide valid account holder name and initial balance.';
    }
});

document.getElementById('deposit').addEventListener('click', () => {
    const amount = parseFloat(document.getElementById('amount').value);
    if (currentAccount) {
        if (currentAccount.deposit(amount)) {
            document.getElementById('message').textContent = 
                `Successfully deposited $${amount}`;
            updateAccountInfo();
        } else {
            document.getElementById('message').textContent = 
                'Invalid deposit amount';
        }
    }
});

document.getElementById('withdraw').addEventListener('click', () => {
    const amount = parseFloat(document.getElementById('amount').value);
    if (currentAccount) {
        if (currentAccount.withdraw(amount)) {
            document.getElementById('message').textContent = 
                `Successfully withdrew $${amount}`;
            updateAccountInfo();
        } else {
            document.getElementById('message').textContent = 
                'Invalid withdrawal amount or insufficient funds';
        }
    }
});

document.getElementById('checkBalance').addEventListener('click', () => {
    if (currentAccount) {
        const balance = currentAccount.checkBalance();
        document.getElementById('message').textContent = 
            `Current balance: $${balance}`;
    }
});

function updateAccountInfo() {
    if (currentAccount) {
        document.getElementById('accountInfo').textContent = 
            `Account Holder: ${currentAccount.accountHolder} | Balance: $${currentAccount.balance}`;
    }
}