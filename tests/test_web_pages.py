import os
import unittest
from unittest.mock import patch
from pathlib import Path

os.environ.setdefault("PASS", "test-password")

import app as app_package
from app import db
from app.models import Connection, Settings, User


class DummyImap:
    def close(self):
        return None

    def logout(self):
        return None


class DummySmtp:
    def starttls(self, context=None):
        return None

    def login(self, user, password):
        return None

    def sendmail(self, from_addr, to_addr, message):
        return None

    def quit(self):
        return None


class TestWebPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = str(Path(__file__).resolve().parents[1])
        cls.test_db_name = "test_database.db"
        cls.test_db_path = os.path.join(cls.repo_root, "app", cls.test_db_name)

        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

        app_package.DB_NAME = cls.test_db_name
        cls.app = app_package.create_app()
        cls.app.config["TESTING"] = True

        with cls.app.app_context():
            db.create_all()
            user = User(email="user@example.com")
            user.password = "not-a-real-hash"
            db.session.add(user)
            db.session.add(
                Connection(
                    outgoing_hostname="smtp.example.com",
                    incoming_hostname="imap.example.com",
                    smtp_port=587,
                    imap_port=993,
                )
            )
            db.session.add(Settings(del_button_behavior="trash", num_msg_per_page=10))
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        self.client = self.app.test_client()

    def login(self):
        with patch("app.auth.check_password_hash", return_value=True):
            response = self.client.post(
                "/login",
                data={"email": "user@example.com", "password": "password123"},
            )
        self.assertEqual(response.status_code, 302)

    def test_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_setup_page(self):
        response = self.client.get("/setup")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_home_page(self):
        self.login()
        with patch("app.pages.use_imap", return_value=DummyImap()):
            response = self.client.get("/home")
        self.assertEqual(response.status_code, 302)
        self.assertIn("folder=INBOX", response.location)

    def test_send_page(self):
        self.login()
        with patch("app.pages.smtplib.SMTP", return_value=DummySmtp()):
            response = self.client.get("/send")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Send Message", response.data)

    def test_settings_page(self):
        self.login()
        response = self.client.get("/settings?page=general")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"General Settings", response.data)

    def test_reload_page(self):
        self.login()
        response = self.client.get("/reload")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reloading", response.data)


if __name__ == "__main__":
    unittest.main()
