"""
Shared pytest fixtures: Flask test client + a real MySQL test database
that gets wiped and reseeded with known data before every test.

Locally: point these env vars at a throwaway local/test MySQL database
(never your real Aiven one). In CI: GitHub Actions sets them to talk to
the mysql service container defined in .github/workflows/tests.yml.
"""

import os
import sys
import pytest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_USER", "root")
os.environ.setdefault("DB_PASSWORD", "test_root_password")
os.environ.setdefault("DB_NAME", "uniboard_test")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")

from app import app as flask_app
from db import get_db_connection


TEST_STUDENT = {
    "usn": "1XX21CS999",
    "name": "Test Student",
    "dob": date(2003, 5, 15),
    "semester": 5,
    "branch": "CSE",
}

TEST_SUBJECT = {
    "subject_code": "CS501",
    "subject_name": "Test Subject",
    "semester": 5,
    "branch": "CSE",
}


@pytest.fixture(scope="session")
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db():
    """Wipe and reseed a minimal, known dataset before every single test,
    so tests never depend on each other's leftover state."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM results")
    cur.execute("DELETE FROM attendance")
    cur.execute("DELETE FROM subjects")
    cur.execute("DELETE FROM students")
    conn.commit()

    cur.execute(
        "INSERT INTO students (usn, name, dob, semester, branch) VALUES (%s, %s, %s, %s, %s)",
        (TEST_STUDENT["usn"], TEST_STUDENT["name"], TEST_STUDENT["dob"],
         TEST_STUDENT["semester"], TEST_STUDENT["branch"]),
    )
    cur.execute(
        "INSERT INTO subjects (subject_code, subject_name, semester, branch) VALUES (%s, %s, %s, %s)",
        (TEST_SUBJECT["subject_code"], TEST_SUBJECT["subject_name"],
         TEST_SUBJECT["semester"], TEST_SUBJECT["branch"]),
    )
    # 25/40 = 62.5% — deliberately below the 75% threshold, to exercise the flagging logic
    cur.execute(
        "INSERT INTO attendance (usn, subject_code, classes_held, classes_attended) VALUES (%s, %s, %s, %s)",
        (TEST_STUDENT["usn"], TEST_SUBJECT["subject_code"], 40, 25),
    )
    conn.commit()
    cur.close()
    conn.close()

    yield

@pytest.fixture(scope="session")
def test_student():
    return TEST_STUDENT


@pytest.fixture(scope="session")
def test_subject():
    return TEST_SUBJECT