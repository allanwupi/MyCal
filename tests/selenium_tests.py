from unittest import TestCase
from flask import url_for
from sqlalchemy import TIME
from app import create_app, db
from app.config import TestConfig
from app.models import User, Friendship, Event, create_test_data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing
#import time
import sys

localHost = "http://127.0.0.1:5000/"

# Choose a reasonable timeout for waiting for elements to appear on the page during Selenium tests
TIMEOUT_SECONDS = 10

class SeleniumTests(TestCase):
    def setUp(self):
        self.testApp =  create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        create_test_data()

        # On Mac a pickle error occurs when using multiprocessing.Process, so we use fork_context instead
        if sys.platform == "darwin":
            fork_context = multiprocessing.get_context("fork")
            self.server_thread = fork_context.Process(
                target=self.testApp.run,
                kwargs={"use_reloader": False},
            )
        elif sys.platform.startswith("win"):
            #import threading
            #self.server_thread = threading.Thread(target=lambda: self.testApp.run(port=5000, use_reloader=False))
            self.server_thread = multiprocessing.Process(target=self.testApp.run)
        else:
            self.server_thread = multiprocessing.Process(target=self.testApp.run)
        self.server_thread.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        return super().setUp()
    
    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
        return super().tearDown()
    
    def test_valid_login(self):
        self.driver.get(localHost)
        identifier_input = self.driver.find_element(By.ID, "identifier")
        password_input = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "submit")

        identifier_input.send_keys("testuser@example.com")
        password_input.send_keys("testpassword")
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
        submit_button.click()
        # invalid login should flash an error message
        alert_element = WebDriverWait(self.driver, TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert"))
        )
        self.assertIsNotNone(alert_element, "Alert message not found after invalid login")
        self.assertEqual(alert_element.text, "Invalid login details. Please try again.", "Alert message text does not match expected invalid login message")