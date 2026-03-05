const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

async function runTests() {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        headless: true
    });
    const page = await browser.newPage();

    // Load the HTML file
    await page.goto("file:///home/labDirectory/index.html");

    const results = { data: [] };

    // Add a task
    await page.type("#task-input", "Test Task");
    await page.click("#add-task");

    // Wait until the task and buttons are rendered
    await page.waitForSelector(".complete-btn");
    await page.waitForSelector(".delete-btn");

    // Test 1: Complete Task Functionality
    await page.click(".complete-btn");
    const taskCompleted = await page.evaluate(() => {
        return document
            .querySelector("#task-list li")
            .classList.contains("completed");
    });
    results.data.push({
        testid: "CompleteTaskFunctionality",
        score: taskCompleted ? 1 : 0,
        status: taskCompleted ? "success" : "failure",
        "maximum marks": 1,
        message: taskCompleted
            ? "Task completed successfully"
            : "Failed to complete task",
    });

    // Test 2: Delete Task Functionality
    await page.click(".delete-btn");
    const taskDeleted = await page.evaluate(() => {
        return document.querySelector("#task-list li") === null;
    });
    results.data.push({
        testid: "DeleteTaskFunctionality",
        score: taskDeleted ? 1 : 0,
        status: taskDeleted ? "success" : "failure",
        "maximum marks": 1,
        message: taskDeleted
            ? "Task deleted successfully"
            : "Failed to delete task",
    });

    await browser.close();

    // Write results to evaluate.json
    fs.writeFileSync(
        path.resolve("evaluate.json"),
        JSON.stringify(results, null, 2)
    );
}

runTests().catch((error) => {
    console.error("Autograder failed:", error);
    const results = {
        data: [
            {
                testid: "AutograderError",
                score: 0,
                "maximum marks": 1,
                message: `Autograder failed: ${error.message}`,
            },
        ],
    };
    fs.writeFileSync(
        path.resolve("evaluate.json"),
        JSON.stringify(results, null, 2)
    );
});
