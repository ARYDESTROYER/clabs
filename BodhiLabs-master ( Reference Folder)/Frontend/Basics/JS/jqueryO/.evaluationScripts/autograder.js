const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

const TEST_TIMEOUT = 15000; // Increased to 15 seconds for safety
let browser;
let page;
let results = {
  data: [],
};

async function initBrowser() {
  browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    ignoreHTTPSErrors: true,
    dumpio: false
  });
  page = await browser.newPage();
  await page.setViewport({ width: 1024, height: 768 });
}

async function closeBrowser() {
  if (browser) {
    await browser.close();
  }
}

function addTestResult(testid, score, maxMarks, message) {
  results.data.push({
    testid,
    status: score > 0 ? "success" : "failure",
    score,
    "maximum marks": maxMarks,
    message,
  });
}

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runTests() {
  try {
    await initBrowser();

    // Load the page
    await page.goto('file://' + path.join(__dirname, 'index.html'));

    // Test 1: Check if lightbox opens when clicking gallery item
    const testOpenLightbox = async () => {
      try {
        // Click the first gallery item
        await page.click(".gallery-item:first-child");
        // Wait for lightbox to be visible
        await page.waitForFunction(
          () =>
            window.getComputedStyle(document.querySelector(".lightbox"))
              .display !== "none",
          { timeout: 5000 },
        );
        // Check if the image source is correct
        const imgSrc = await page.$eval(".lightbox-image", (el) =>
          el.getAttribute("src"),
        );
        const expectedSrc = "images/img_5terre.jpg";

        if (imgSrc === expectedSrc) {
          addTestResult(
            "OpenLightbox",
            1,
            1,
            "Lightbox opens correctly with proper image",
          );
        } else {
          addTestResult(
            "OpenLightbox",
            0,
            1,
            "Lightbox image source not set correctly",
          );
        }
      } catch (error) {
        addTestResult(
          "OpenLightbox",
          0,
          1,
          "Failed to open lightbox: " + error.message,
        );
      }
    };

    // Test 2: Check if close button works
    const testCloseButton = async () => {
      try {
        // Open lightbox first
        await page.click(".gallery-item:first-child");
        await page.waitForFunction(
          () =>
            window.getComputedStyle(document.querySelector(".lightbox"))
              .display !== "none",
          { timeout: 5000 },
        );

        // Click close button
        await page.click(".close");
        // Wait for lightbox to be hidden
        await page.waitForFunction(
          () =>
            window.getComputedStyle(document.querySelector(".lightbox"))
              .display === "none",
          { timeout: 5000 },
        );

        addTestResult("CloseButton", 1, 1, "Close button works correctly");
      } catch (error) {
        addTestResult(
          "CloseButton",
          0,
          1,
          "Close button not working: " + error.message,
        );
      }
    };

    // Test 3: Check if clicking outside closes lightbox
    const testOutsideClick = async () => {
      try {
        // Check for jQuery
        const hasJQuery = await page.evaluate(() => typeof $ !== "undefined");
        if (!hasJQuery) {
          addTestResult(
            "OutsideClick",
            0,
            1,
            "jQuery not found. Ensure jQuery is included in index.html",
          );
          return;
        }

        // Add test click handler
        await page.evaluate(() => {
          window.outsideClickHandled = false;
          const originalFadeOut = $.fn.fadeOut;
          $.fn.fadeOut = function () {
            if (this.hasClass("lightbox")) {
              window.outsideClickHandled = true;
            }
            return originalFadeOut.apply(this, arguments);
          };
        });

        // Open lightbox
        await page.click(".gallery-item:first-child");
        await page.waitForFunction(
          () =>
            window.getComputedStyle(document.querySelector(".lightbox"))
              .display !== "none",
          { timeout: 5000 },
        );

        // Verify lightbox element exists and is clickable
        const lightboxExists = await page.evaluate(() => !!document.querySelector(".lightbox"));
        if (!lightboxExists) {
          addTestResult(
            "OutsideClick",
            0,
            1,
            "Lightbox element not found in the DOM",
          );
          return;
        }

        // Wait for event handlers to be ready
        await delay(1000); // Increased for reliability

        // Trigger click directly on .lightbox element
        await page.evaluate(() => {
          const lightbox = document.querySelector(".lightbox");
          const event = new MouseEvent("click", {
            bubbles: true,
            cancelable: true,
            view: window,
          });
          lightbox.dispatchEvent(event);
        });

        // Wait for lightbox to close
        try {
          await page.waitForFunction(
            () =>
              window.getComputedStyle(document.querySelector(".lightbox"))
                .display === "none",
            { timeout: TEST_TIMEOUT },
          );
        } catch (timeoutError) {
          const lightboxDisplay = await page.evaluate(
            () => window.getComputedStyle(document.querySelector(".lightbox")).display || "unknown"
          );
          addTestResult(
            "OutsideClick",
            0,
            1,
            `Outside click timed out after ${TEST_TIMEOUT}ms: Lightbox did not close. Current display: ${lightboxDisplay}. Ensure the lightbox closes when clicking outside.`,
          );
          return; // Exit the test to prevent further checks
        }

        // Check if the event was handled correctly
        const wasHandled = await page.evaluate(
          () => window.outsideClickHandled,
        );
        const isHidden = await page.evaluate(
          () =>
            window.getComputedStyle(document.querySelector(".lightbox"))
              .display === "none",
        );

        if (wasHandled && isHidden) {
          addTestResult(
            "OutsideClick",
            1,
            1,
            "Outside click handled correctly",
          );
        } else {
          addTestResult(
            "OutsideClick",
            0,
            1,
            'Outside click handler not implemented correctly. Ensure $(e.target).is(".lightbox, .close") is checked before calling fadeOut()',
          );
        }
      } catch (error) {
        const lightboxDisplay = await page.evaluate(
          () => window.getComputedStyle(document.querySelector(".lightbox")).display || "unknown"
        );
        addTestResult(
          "OutsideClick",
          0,
          1,
          `Outside click test failed: ${error.message}. Lightbox display: ${lightboxDisplay}`,
        );
      }
    };

    // Run all tests
    await testOpenLightbox();
    await testCloseButton();
    await testOutsideClick();
  } catch (error) {
    addTestResult(
      "TestSuiteError",
      0,
      3,
      "Test suite failed to run: " + error.message,
    );
  } finally {
    // Write results to file
    fs.writeFileSync(
      path.join(__dirname, "evaluate.json"),
      JSON.stringify(results, null, 2),
    );

    await closeBrowser();
  }
}

// Run the test suite
runTests().catch(() => {});
