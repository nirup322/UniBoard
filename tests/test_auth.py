"""Integration tests for student and admin login."""


def test_student_login_page_loads(client):
    resp = client.get("/student/login")
    assert resp.status_code == 200


def test_student_login_success(client, test_student):
    resp = client.post("/student/login", data={
        "usn": test_student["usn"],
        "dob": test_student["dob"].isoformat(),
    })
    assert resp.status_code == 200
    assert test_student["name"].encode() in resp.data


def test_student_login_wrong_usn(client):
    resp = client.post("/student/login", data={
        "usn": "1XX21CS000",
        "dob": "2003-05-15",
    })
    assert b"USN not found" in resp.data


def test_student_login_wrong_dob(client, test_student):
    resp = client.post("/student/login", data={
        "usn": test_student["usn"],
        "dob": "2000-01-01",
    })
    assert b"Incorrect date of birth" in resp.data


def test_student_login_usn_case_insensitive(client, test_student):
    resp = client.post("/student/login", data={
        "usn": test_student["usn"].lower(),
        "dob": test_student["dob"].isoformat(),
    })
    assert test_student["name"].encode() in resp.data


def test_admin_login_success(client):
    resp = client.post("/admin/login", data={
        "username": "admin", "password": "admin123",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/admin/dashboard")


def test_admin_login_failure(client):
    resp = client.post("/admin/login", data={
        "username": "admin", "password": "wrongpassword",
    })
    assert b"Invalid username or password" in resp.data


def test_admin_dashboard_requires_login(client):
    resp = client.get("/admin/dashboard", follow_redirects=False)
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_admin_dashboard_after_login(client, test_student):
    client.post("/admin/login", data={"username": "admin", "password": "admin123"})
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert test_student["usn"].encode() in resp.data