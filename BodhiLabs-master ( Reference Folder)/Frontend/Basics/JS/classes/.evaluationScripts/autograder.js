const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({
        args: ['--disable-gpu', '--disable-setuid-sandbox', '--no-sandbox', '--disable-dev-shm-usage'],
        ignoreHTTPSErrors: true,
        dumpio: false
    });
    const page = await browser.newPage();
    
    await page.goto('file:///home/labDirectory/index.html');

    // Test cases for BankAccount lab
    const testCases = [
        {
            testid: 1,
            description: "Constructor: Account holder name initialization",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.accountHolder === "John Doe";
                });
                return output;
            }
        },
        {
            testid: 2,
            description: "Constructor: Initial balance initialization",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 3,
            description: "Deposit: Valid positive amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.deposit(500) === true && account.balance === 1500;
                });
                return output;
            }
        },
        {
            testid: 4,
            description: "Deposit: Invalid zero amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.deposit(0) === false && account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 5,
            description: "Deposit: Invalid negative amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.deposit(-100) === false && account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 6,
            description: "Withdraw: Valid amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.withdraw(500) === true && account.balance === 500;
                });
                return output;
            }
        },
        {
            testid: 7,
            description: "Withdraw: Invalid zero amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.withdraw(0) === false && account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 8,
            description: "Withdraw: Invalid negative amount",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.withdraw(-100) === false && account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 9,
            description: "Withdraw: Amount exceeding balance",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    return account.withdraw(1500) === false && account.balance === 1000;
                });
                return output;
            }
        },
        {
            testid: 10,
            description: "Check Balance: Returns correct balance",
            check: async () => {
                const output = await page.evaluate(() => {
                    const account = new BankAccount("John Doe", 1000);
                    account.deposit(500);
                    account.withdraw(200);
                    return account.checkBalance() === 1300;
                });
                return output;
            }
        }
    ];

    // Initialize response object
    const response = { "data": [] };

    // Run through test cases
    for (const testCase of testCases) {
        try {
            const passed = await testCase.check();

            response.data.push({
                "testid": testCase.testid,
                "status": passed ? "success" : "failure",
                "score": passed ? 1 : 0,
                "maximum marks": 1,
                "message": passed 
                    ? `Passed: ${testCase.description}` 
                    : `Failed: ${testCase.description}`
            });

        } catch (error) {
            response.data.push({
                "testid": testCase.testid,
                "status": "failure",
                "score": 0,
                "maximum marks": 1,
                "message": `Test failed: ${error.message}`
            });
        }
    }

    // Write results to file
    const dictstring = JSON.stringify(response, null, 2);
    await fs.promises.writeFile("evaluate.json", dictstring);

    await browser.close();
})();
