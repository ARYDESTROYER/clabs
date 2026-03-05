const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch(
        {
            args: ['--disable-gpu', '--disable-setuid-sandbox', '--no-sandbox', '--disable-dev-shm-usage'],
            ignoreHTTPSErrors: true,
            dumpio: false
        }
    );
    const page = await browser.newPage();

    // Load the student's HTML file
    await page.goto('file://' + __dirname + '/index.html'); // Adjust path if necessary
    await page.addScriptTag({ path: 'script.js' });

    const response = { "data": [] };

    // Helper function to get displayed dimensions
    const getDisplayedDimensions = async () => {
        return await page.evaluate(() => {
            const width = document.getElementById('width').textContent;
            const height = document.getElementById('height').textContent;
            return { width: width, height: height };
        });
    };

    // Test Case 1: Check if initial window dimensions are displayed correctly
    await page.setViewport({ width: 400, height: 500 });
    await new Promise(resolve => setTimeout(resolve, 500));  // Give time for resize event to fire

    displayedDimensions = await getDisplayedDimensions();

    if (displayedDimensions.width === '400px'  && displayedDimensions.height === '500px') {
        response.data.push({
            "testid": 1,
            "status": "success",
            "score": 1,
            "maximum marks": 1,
            "message": "Window dimensions displayed correctly."
        });
    } else {
        response.data.push({
            "testid": 1,
            "status": "failed",
            "score": 0,
            "maximum marks": 1,
            "message": `Window dimensions not displayed correctly. Expected width: 400px, height: 500px.`
        });
    }

    // Test Case 2: Check if window dimensions update correctly on resize
    await page.setViewport({ width: 800, height: 600 });
    await new Promise(resolve => setTimeout(resolve, 500));  // Give time for resize event to fire

    displayedDimensions = await getDisplayedDimensions();

    if (displayedDimensions.width === '800px' && displayedDimensions.height === '600px') {
        response.data.push({
            "testid": 2,
            "status": "success",
            "score": 1,
            "maximum marks": 1,
            "message": "Window dimensions updated correctly on resize."
        });
    } else {
        response.data.push({
            "testid": 2,
            "status": "failed",
            "score": 0,
            "maximum marks": 1,
            "message": `Window dimensions not updated correctly on resize. Expected width: 800px, height: 600px.`
        });
    }

    // Test Case 3: Check dimensions again after resizing to a different value
    await page.setViewport({ width: 1024, height: 768 });
    await new Promise(resolve => setTimeout(resolve, 500));  // Give time for resize event to fire

    displayedDimensions = await getDisplayedDimensions();

    if (displayedDimensions.width === '1024px' && displayedDimensions.height === '768px') {
        response.data.push({
            "testid": 3,
            "status": "success",
            "score": 1,
            "maximum marks": 1,
            "message": "Window dimensions correctly updated to new size."
        });
    } else {
        response.data.push({
            "testid": 3,
            "status": "failed",
            "score": 0,
            "maximum marks": 1,
            "message": `Window dimensions not updated correctly to new size. Expected width: 1024px, height: 768px.`
        });
    }

    // Create the output JSON
    const output = {
        "data": response.data
    };

    const fs = require('fs');
    fs.writeFileSync("evaluate.json", JSON.stringify(output, null, 2), (err) => {
        if (err) throw err;
    });

    await browser.close();
})();
