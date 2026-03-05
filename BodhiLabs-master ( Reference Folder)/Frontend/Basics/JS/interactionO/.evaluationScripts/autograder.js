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

    await page.goto('file://' + __dirname + '/index.html'); // Path to the index.html file

    // Initialize response object
    const response = { "data": [] };

    // Test if Scroll to Top button scrolls to the top
    const scrollTopTest = await page.evaluate(() => {
        window.scrollTo(0, 1000); // Simulate scroll
        document.getElementById('scrollTop').click(); // Trigger scroll to top
        
        return window.scrollY === 0; // Check if we are at the top
    });

    response.data.push({
        "testid": 1,
        "status": scrollTopTest ? "success" : "failure",
        "score": scrollTopTest ? 1 : 0,
        "maximum marks": 1,
        "message": scrollTopTest ? "Scroll to Top works correctly." : "Scroll to Top failed."
    });

    // Test if Scroll to Bottom button scrolls to the bottom
    const scrollBottomTest = await page.evaluate(() => {
        window.scrollTo(0, 0); // Simulate scroll
        document.getElementById('scrollBottom').click(); // Trigger scroll to bottom
        return window.scrollY + window.innerHeight === document.body.scrollHeight; // Check if we are at the bottom
    });

    response.data.push({
        "testid": 2,
        "status": scrollBottomTest ? "success" : "failure",
        "score": scrollBottomTest ? 1 : 0,
        "maximum marks": 1,
        "message": scrollBottomTest ? "Scroll to Bottom works correctly." : "Scroll to Bottom failed."
    });

    // Test if alert is triggered
    let alertTriggered = false;
    page.on('dialog', async dialog => {
        if (dialog.type() === 'alert') {
            alertTriggered = true;
            await dialog.dismiss();
        }
    });

    await page.click('#alertButton'); // Trigger alert button

    response.data.push({
        "testid": 3,
        "status": alertTriggered ? "success" : "failure",
        "score": alertTriggered ? 1 : 0,
        "maximum marks": 1,
        "message": alertTriggered ? "Alert was triggered correctly." : "Alert button did not trigger."
    });

    var dictstring = JSON.stringify(response, null, 2);
    var fs = require('fs');
    await fs.writeFile("evaluate.json", dictstring, (err) => err && console.error(err));

    await browser.close();
})();
