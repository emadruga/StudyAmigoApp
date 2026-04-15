"""
test_api.py — Unit tests for SAv1.5 auth endpoints.

Run from /server:
    python -m unittest test_api.py -v
"""
import json
import os
import sqlite3
import tempfile
import unittest

import bcrypt

# Point app at a temp DB before importing
_tmp_dir = tempfile.mkdtemp()
os.environ['SECRET_KEY'] = 'test-secret-key-for-unit-tests'

import app as server_app  # noqa: E402


def _make_test_db(path: str):
    """Create a minimal admin.db with the SAv1.5 schema and one test user."""
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            name          TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email         TEXT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
            ON users(email) WHERE email IS NOT NULL;
    """)
    pw_hash = bcrypt.hashpw(b'senha12345', bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, name, password_hash, email) VALUES (?,?,?,?)",
        ('testuser', 'Test User', pw_hash, 'test@example.com'),
    )
    conn.commit()
    conn.close()


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.db_path = os.path.join(_tmp_dir, 'admin_test.db')
        _make_test_db(self.db_path)
        server_app.ADMIN_DB_PATH = self.db_path
        server_app.app.config['TESTING'] = True
        server_app.app.config['SESSION_TYPE'] = 'filesystem'
        server_app.app.config['SESSION_FILE_DIR'] = _tmp_dir
        self.client = server_app.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # ------------------------------------------------------------------
    # POST /register — must be disabled (503)
    # ------------------------------------------------------------------
    def test_register_disabled(self):
        r = self.client.post('/register', json={
            'username': 'newuser', 'name': 'New', 'password': 'senha12345'
        })
        self.assertEqual(r.status_code, 503)
        data = json.loads(r.data)
        self.assertIn('error', data)

    # ------------------------------------------------------------------
    # POST /login
    # ------------------------------------------------------------------
    def test_login_success(self):
        r = self.client.post('/login', json={
            'email': 'test@example.com', 'password': 'senha12345'
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['user']['name'], 'Test User')

    def test_login_email_case_insensitive(self):
        r = self.client.post('/login', json={
            'email': 'TEST@EXAMPLE.COM', 'password': 'senha12345'
        })
        self.assertEqual(r.status_code, 200)

    def test_login_wrong_password(self):
        r = self.client.post('/login', json={
            'email': 'test@example.com', 'password': 'wrongpassword'
        })
        self.assertEqual(r.status_code, 401)

    def test_login_unknown_email(self):
        r = self.client.post('/login', json={
            'email': 'nobody@example.com', 'password': 'senha12345'
        })
        self.assertEqual(r.status_code, 401)

    def test_login_missing_fields(self):
        r = self.client.post('/login', json={'email': 'test@example.com'})
        self.assertEqual(r.status_code, 400)

    def test_login_username_field_rejected(self):
        """Old username-based payload must not succeed."""
        r = self.client.post('/login', json={
            'username': 'testuser', 'password': 'senha12345'
        })
        self.assertEqual(r.status_code, 400)

    # ------------------------------------------------------------------
    # POST /change-password
    # ------------------------------------------------------------------
    def _login(self):
        self.client.post('/login', json={
            'email': 'test@example.com', 'password': 'senha12345'
        })

    def test_change_password_success(self):
        self._login()
        r = self.client.post('/change-password', json={
            'current_password': 'senha12345',
            'new_password': 'novaSenha99'
        })
        self.assertEqual(r.status_code, 200)
        # Confirm new password works
        r2 = self.client.post('/login', json={
            'email': 'test@example.com', 'password': 'novaSenha99'
        })
        self.assertEqual(r2.status_code, 200)

    def test_change_password_wrong_current(self):
        self._login()
        r = self.client.post('/change-password', json={
            'current_password': 'wrongpassword',
            'new_password': 'novaSenha99'
        })
        self.assertEqual(r.status_code, 401)

    def test_change_password_too_short(self):
        self._login()
        r = self.client.post('/change-password', json={
            'current_password': 'senha12345',
            'new_password': 'curta'
        })
        self.assertEqual(r.status_code, 400)

    def test_change_password_too_long(self):
        self._login()
        r = self.client.post('/change-password', json={
            'current_password': 'senha12345',
            'new_password': 'a' * 21
        })
        self.assertEqual(r.status_code, 400)

    def test_change_password_requires_login(self):
        """Must return 401 if not authenticated."""
        r = self.client.post('/change-password', json={
            'current_password': 'senha12345',
            'new_password': 'novaSenha99'
        })
        self.assertEqual(r.status_code, 401)

    def test_change_password_missing_fields(self):
        self._login()
        r = self.client.post('/change-password', json={
            'current_password': 'senha12345'
        })
        self.assertEqual(r.status_code, 400)


if __name__ == '__main__':
    unittest.main()
