from unittest import TestCase
from flask import app, url_for
from sqlalchemy import TIME
from app import create_app, db
from app.config import TestConfig
from app.models import User, Friendship, Event, create_test_data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import sys

localHost = "http://127.0.0.1:5000/"

# Choose a reasonable timeout for waiting for elements to appear on the page during Selenium tests
TIMEOUT_SECONDS = 10

def run_server(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_test_data()
    app.run(port=5000, use_reloader=False, threaded=True)

class SeleniumTests(TestCase):

    def setUp(self):
        self.testApp = create_app(TestConfig)

        self.server_thread = threading.Thread(
            target=run_server,
            args=(self.testApp,),
            daemon=True
        )
        self.server_thread.start()

        import time, requests
        for _ in range(50):
            try:
                requests.get(localHost)
                break
            except:
                time.sleep(0.1)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)
    
    def tearDown(self):
        self.driver.quit()

    
    def test_valid_login(self):
        self.driver.get(localHost)
        identifier_input = self.driver.find_element(By.ID, "identifier")
        password_input = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "submit")
        identifier_input.send_keys("testuser@example.com")
        password_input.send_keys("testpassword")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
        # successful login should redirect to calendar page, so we wait for an element on the calendar page to be present
        WebDriverWait(self.driver, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "calendar"))
        )
        self.assertIsNotNone(self.driver.find_element(By.ID, "calendar"), "Calendar element not found after successful login, expected to be on calendar page")
    
    def test_invalid_login(self):
        self.driver.get(localHost)
        identifier_input = self.driver.find_element(By.ID, "identifier")
        password_input = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "submit")
        identifier_input.send_keys("invalid@example.com")
        password_input.send_keys("invalidpassword")

        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
        # invalid login should flash an error message
        alert_element = WebDriverWait(self.driver, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert"))
        )
        self.assertIsNotNone(alert_element, "Alert message not found after invalid login")
        self.assertEqual(alert_element.text, "Invalid login details. Please try again.", "Alert message text does not match expected invalid login message")