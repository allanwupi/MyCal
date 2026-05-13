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


if __name__ == "__main__":
    unittest.main()