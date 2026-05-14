import unittest
import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from app import app, db


class SeleniumBasicTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        cls.app_context = app.app_context()
        cls.app_context.push()
        db.create_all()

        cls.server_thread = threading.Thread(
            target=lambda: app.run(port=5001, use_reloader=False)
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()

        time.sleep(1)

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        cls.driver = webdriver.Chrome(
        executable_path=r"D:\UWA\trimister 3\CITS 3403\git\chromedriver-win64\chromedriver.exe",
        options=chrome_options
        )
        cls.base_url = "http://127.0.0.1:5001"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    ##add the sign up infomation to avoid the problem of the user already exists when running the test multiple times
    def sign_up_user(self, username, email, password):
        self.driver.get(self.base_url + "/")

        signup_tab = self.driver.find_element(By.ID, "signup-tab")
        signup_tab.click()

        time.sleep(0.5)

        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "confirm_password").send_keys(password)
        self.driver.find_element(By.ID, "signup-submit").click()

        time.sleep(0.5)

    def test_landing_page_loads(self):
        self.driver.get(self.base_url + "/")

        self.assertIn("MyCal", self.driver.title)

    
    def test_login_page_has_form(self):

        self.driver.get(self.base_url + "/")

        identifier_input = self.driver.find_element(
            By.ID,
            "identifier"
        )

        password_input = self.driver.find_element(
            By.ID,
            "password"
        )

        login_button = self.driver.find_element(
            By.ID,
            "login-submit"
        )

        self.assertTrue(identifier_input.is_displayed())
        self.assertTrue(password_input.is_displayed())
        self.assertTrue(login_button.is_displayed())
    
    ### This test assumes that the signup process works correctly and that the user can log in after signing up.
    def test_user_can_sign_up_and_reach_calendar(self):
        self.sign_up_user(
            "seleniumuser1",
            "selenium1@test.com",
            "password123"
        )

        self.assertIn("/calendar", self.driver.current_url)
        self.assertIn("Calendar", self.driver.page_source)
    #test todo list fuinction
    def test_user_can_add_task(self):
        self.sign_up_user(
            "seleniumuser2",
            "selenium2@test.com",
            "password123"
        )

        self.driver.get(self.base_url + "/todo")

        self.driver.find_element(By.ID, "todoInput").send_keys("Finish Selenium Test")
        self.driver.find_element(By.ID, "todoDate").send_keys("2026-05-20T10:30")
        self.driver.find_element(By.ID, "addTodoBtn").click()
        time.sleep(0.5)
        self.assertIn("Finish Selenium Test", self.driver.page_source)

    #add a logout test to ensure that the user can log out successfully and is redirected to the login page.
    def test_user_can_logout(self):
        self.sign_up_user(
            "seleniumuser3",
            "selenium3@test.com",
            "password123"
        )

        self.driver.find_element(By.ID, "logout-submit").click()

        time.sleep(0.5)

        self.assertIn("Login", self.driver.page_source)

if __name__ == "__main__":
    unittest.main()