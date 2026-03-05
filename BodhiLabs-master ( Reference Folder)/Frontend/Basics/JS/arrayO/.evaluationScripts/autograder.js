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

    // Test cases for output verification
    const testCases = [
        {
            testid: 1,
            description: "Original Array output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Original Array: 1,2,3,4,5');
                });
                return outputText;
            }
        },
        {
            testid: 2,
            description: "Array After Adding Element 1 output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Adding Element 1: 1,2,3,4,5,1');
                });
                return outputText;
            }
        },
        {
            testid: 3,
            description: "Array After Removing Last Element output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Removing Last Element: 1,2,3,4,5');
                });
                return outputText;
            }
        },
        {
            testid: 4,
            description: "Array After Adding Element 0 output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Adding Element 0: 0,1,2,3,4,5');
                });
                return outputText;
            }
        },
        {
            testid: 5,
            description: "Array After Removing First Element output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Removing First Element: 1,2,3,4,5');
                });
                return outputText;
            }
        },
        {
            testid: 6,
            description: "Index of Element 3 output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Index of Element 3: 2');
                });
                return outputText;
            }
        },
        {
            testid: 7,
            description: "Array After Removing Element 3 output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Removing Element 3: 1,2,4,5');
                });
                return outputText;
            }
        },
        {
            testid: 8,
            description: "Array After Adding Element 6 at Index 2 output should be correct",
            check: async () => {
                const outputText = await page.evaluate(() => {
                    const outputElement = document.getElementById('output');
                    return outputElement.innerHTML.includes('Array After Adding Element 6 at Index 2: 1,2,6,4,5');
                });
                return outputText;
            }
        }
    ];

    // Initialize response object
    const response = { "data": [] };

    // Track if any test case fails
    let allPassed = true;

    // Run through test cases
    for (let testCase of testCases) {
        try {
            const passed = await testCase.check();
            if (!passed) {
                allPassed = false;
                response.data.push({
                    "testid": testCase.testid,
                    "status": "failure",
                    "score": 0,
                    "maximum marks": 1,
                    "message": `Failed: ${testCase.description}`
                });
            } else {
                response.data.push({
                    "testid": testCase.testid,
                    "status": "success",
                    "score": 1,
                    "maximum marks": 1,
                    "message": "Passed"
                });
            }
        } catch (error) {
            allPassed = false;
            response.data.push({
                "testid": testCase.testid,
                "status": "failure",
                "score": 0,
                "maximum marks": 1,
                "message": `Error in test: ${error.message}`
            });
        }
    }

    // Write results to file
    const dictstring = JSON.stringify(response, null, 2);
    await fs.promises.writeFile("evaluate.json", dictstring);

    await browser.close();
})();
