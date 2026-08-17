"""Integration tests for attendance tracking and the below-75% flagging logic."""


def login_admin(client):
    client.post("/admin/login", data={"username": "admin", "password": "admin123"})


def test_attendance_percentage_shown_on_profile(client, test_student):
    resp = client.post("/student/login", data={
        "usn": test_student["usn"],
        "dob": test_student["dob"].isoformat(),
    })
    assert b"62.5" in resp.data


def test_below_75_percent_is_flagged(client, test_student):
    resp = client.post("/student/login", data={
        "usn": test_student["usn"],
        "dob": test_student["dob"].isoformat(),
    })
    assert b"below minimum" in resp.data


def test_admin_can_update_attendance(client, test_student, test_subject):
    login_admin(client)
    resp = client.post(
        f"/admin/student/{test_student['usn']}/update-attendance",
        data={
            "subject_code": test_subject["subject_code"],
            "classes_held": "50",
            "classes_attended": "45",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b'value="50"' in resp.data
    assert b'value="45"' in resp.data


def test_update_attendance_requires_admin_login(client, test_student, test_subject):
    resp = client.post(
        f"/admin/student/{test_student['usn']}/update-attendance",
        data={
            "subject_code": test_subject["subject_code"],
            "classes_held": "50",
            "classes_attended": "45",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]