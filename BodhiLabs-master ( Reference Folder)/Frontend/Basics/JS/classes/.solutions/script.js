class BankAccount {
    constructor(accountHolder, initialBalance) {
        this.accountHolder = accountHolder;
        this.balance = initialBalance;
    }

    deposit(amount) {
        if (amount > 0) {
            this.balance += amount;
            return true;
        } else {
            return false;
        }
    }

    withdraw(amount) {
        if (amount > this.balance) {
            return false;
        } else if (amount <= 0) {
            return false;
        } else {
            this.balance -= amount;
            return true;
        }
    }

    checkBalance() {
        return this.balance;
    }
}

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