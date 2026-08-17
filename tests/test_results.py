"""Integration tests for the result upsert logic and subject validation."""


def login_admin(client):
    client.post("/admin/login", data={"username": "admin", "password": "admin123"})


def test_add_new_result(client, test_student, test_subject):
    login_admin(client)
    resp = client.post(
        f"/admin/student/{test_student['usn']}/add-result",
        data={"semester": "5", "subject_code": test_subject["subject_code"], "marks": "85"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"85" in resp.data


def test_upsert_updates_existing_result_not_duplicate(client, test_student, test_subject):
    login_admin(client)
    client.post(
        f"/admin/student/{test_student['usn']}/add-result",
        data={"semester": "5", "subject_code": test_subject["subject_code"], "marks": "60"},
    )
    resp = client.post(
        f"/admin/student/{test_student['usn']}/add-result",
        data={"semester": "5", "subject_code": test_subject["subject_code"], "marks": "95"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"95" in resp.data
    assert b"60" not in resp.data


def test_add_result_unknown_subject_rejected(client, test_student):
    login_admin(client)
    resp = client.post(
        f"/admin/student/{test_student['usn']}/add-result",
        data={"semester": "5", "subject_code": "NOTREAL999", "marks": "70"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"doesn" in resp.data


def test_add_result_requires_admin_login(client, test_student, test_subject):
    resp = client.post(
        f"/admin/student/{test_student['usn']}/add-result",
        data={"semester": "5", "subject_code": test_subject["subject_code"], "marks": "70"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]