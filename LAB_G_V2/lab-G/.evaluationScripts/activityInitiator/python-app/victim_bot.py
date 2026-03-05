#!/usr/bin/env python3
"""
Simulates admin user browsing product reviews
"""
import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'http://localhost:30000')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'SecureAdminPass2025!')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 30))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/victim.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_driver():
    """Create Chrome WebDriver with headless configuration"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Use system chromedriver (installed via apt)
    service = Service('/usr/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    return driver

def admin_login(driver):
    """Login as admin user"""
    try:
        logger.info(f"Navigating to login page: {WEBAPP_URL}/login")
        driver.get(f"{WEBAPP_URL}/login")

        # Wait for login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Fill credentials
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(ADMIN_USERNAME)
        password_field.send_keys(ADMIN_PASSWORD)

        # Submit login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # Wait for redirect
        time.sleep(2)

        logger.info("✓ Admin login successful")
        return True

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False

def visit_reviews(driver):
    """Visit all reviews page - where XSS triggers"""
    try:
        logger.info("Visiting /reviews page (XSS trigger point)")
        driver.get(f"{WEBAPP_URL}/reviews")

        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Allow JavaScript execution time (XSS payload runs here)
        time.sleep(5)

        logger.info("✓ Reviews page loaded and JavaScript executed")
        return True

    except Exception as e:
        logger.error(f"Failed to visit reviews: {e}")
        return False

def visit_admin_dashboard(driver):
    """Visit admin dashboard - another XSS trigger point"""
    try:
        logger.info("Visiting /admin dashboard")
        driver.get(f"{WEBAPP_URL}/admin")

        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Allow JavaScript execution time
        time.sleep(5)

        logger.info("✓ Admin dashboard loaded")
        return True

    except Exception as e:
        logger.error(f"Failed to visit admin dashboard: {e}")
        return False

def run_victim_routine():
    """Main victim routine - called periodically"""
    logger.info("=" * 60)
    logger.info("VICTIM BOT ROUTINE STARTED")
    logger.info("=" * 60)

    driver = None

    try:
        # Create browser
        driver = create_driver()
        logger.info("✓ Chrome driver initialized")

        # Login as admin
        if not admin_login(driver):
            logger.error("Failed to login, aborting routine")
            return

        # Visit reviews page (primary XSS trigger)
        visit_reviews(driver)

        # Visit admin dashboard (secondary XSS trigger)
        visit_admin_dashboard(driver)

        logger.info("✓ Victim routine completed successfully")

    except Exception as e:
        logger.error(f"Victim routine failed: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("✓ Browser closed")

def main():
    """Main loop - run victim routine periodically"""
    logger.info("Victim bot started")
    logger.info(f"Target URL: {WEBAPP_URL}")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    logger.info(f"Admin user: {ADMIN_USERNAME}")

    # Wait for webapp to be ready
    logger.info("Waiting for webapp to be ready...")
    time.sleep(10)

    # Run continuously
    while True:
        try:
            run_victim_routine()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")

        # Wait before next routine
        logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
