"""
app.py — UniBoard Flask application.
Step 1: minimal setup, just to confirm Flask runs and can reach MySQL.
"""

from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-later")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


@app.route("/")
def home():
    return "UniBoard is running."


@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    # GET = just show the empty login form
    if request.method == "GET":
        return render_template("student_login.html")

    # POST = form was submitted, check credentials
    usn = request.form["usn"].strip().upper()
    dob = request.form["dob"]  # comes in as 'YYYY-MM-DD', matches MySQL DATE format

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)  # dictionary=True lets us access columns by name
    cur.execute("SELECT * FROM students WHERE usn = %s", (usn,))
    student = cur.fetchone()

    if student is None:
        cur.close()
        conn.close()
        return render_template("student_login.html", error="USN not found.")

    # student["dob"] comes back as a Python date object; convert to string to compare
    if str(student["dob"]) != dob:
        cur.close()
        conn.close()
        return render_template("student_login.html", error="Incorrect date of birth.")

    # Credentials correct — fetch attendance and results, then show the profile page
    # (reusing the same connection/cursor opened above)
    cur.execute("""
        SELECT s.subject_name, a.classes_held, a.classes_attended
        FROM attendance a
        JOIN subjects s ON a.subject_code = s.subject_code
        WHERE a.usn = %s
    """, (usn,))
    attendance_rows = cur.fetchall()

    # Calculate attendance percentage in Python (kept out of SQL for clarity)
    for row in attendance_rows:
        row["percentage"] = round(100 * row["classes_attended"] / row["classes_held"], 1)

    # Past semester results, joined with subjects
    cur.execute("""
        SELECT r.semester, s.subject_name, r.marks, r.grade
        FROM results r
        JOIN subjects s ON r.subject_code = s.subject_code
        WHERE r.usn = %s
        ORDER BY r.semester
    """, (usn,))
    result_rows = cur.fetchall()

    cur.close()
    conn.close()

    # Group results by semester: {1: [...], 2: [...], ...}
    results_by_semester = {}
    for row in result_rows:
        sem = row["semester"]
        results_by_semester.setdefault(sem, []).append(row)

    return render_template(
        "student_profile.html",
        student=student,
        attendance=attendance_rows,
        results=results_by_semester,
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")

    username = request.form["username"]
    password = request.form["password"]

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True  # marks this browser session as logged in
        return redirect("/admin/dashboard")

    return render_template("admin_login.html", error="Invalid username or password.")


@app.route("/admin/dashboard")
def admin_dashboard():
    # Guard: only allow access if session shows admin is logged in
    if not session.get("is_admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT usn, name, semester, branch FROM students ORDER BY usn")
    students = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin_dashboard.html", students=students)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect("/admin/login")


@app.route("/admin/add-student", methods=["GET", "POST"])
def admin_add_student():
    if not session.get("is_admin"):
        return redirect("/admin/login")

    if request.method == "GET":
        return render_template("admin_add_student.html")

    usn = request.form["usn"].strip().upper()
    name = request.form["name"].strip()
    dob = request.form["dob"]
    semester = request.form["semester"]
    branch = request.form["branch"].strip().upper()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO students (usn, name, dob, semester, branch) VALUES (%s, %s, %s, %s, %s)",
            (usn, name, dob, semester, branch),
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        # Happens if this USN already exists (usn is the primary key)
        cur.close()
        conn.close()
        return render_template("admin_add_student.html", error=f"A student with USN {usn} already exists.")

    cur.close()
    conn.close()
    return redirect("/admin/dashboard")


@app.route("/admin/student/<usn>")
def admin_manage_student(usn):
    if not session.get("is_admin"):
        return redirect("/admin/login")

    error = None
    if request.args.get("error") == "unknown_subject":
        error = "That subject code doesn't exist. Pick one from the dropdown."

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM students WHERE usn = %s", (usn,))
    student = cur.fetchone()
    if student is None:
        cur.close()
        conn.close()
        return "Student not found.", 404

    cur.execute("""
        SELECT a.subject_code, s.subject_name, a.classes_held, a.classes_attended
        FROM attendance a
        JOIN subjects s ON a.subject_code = s.subject_code
        WHERE a.usn = %s
    """, (usn,))
    attendance_rows = cur.fetchall()

    cur.execute("""
        SELECT r.semester, s.subject_name, r.marks, r.grade
        FROM results r
        JOIN subjects s ON r.subject_code = s.subject_code
        WHERE r.usn = %s
        ORDER BY r.semester
    """, (usn,))
    result_rows = cur.fetchall()

    # All valid subjects, for the "Add/Update Result" dropdown —
    # prevents the admin from typing a subject_code that doesn't exist
    cur.execute("SELECT subject_code, subject_name, semester FROM subjects ORDER BY semester, subject_code")
    all_subjects = cur.fetchall()

    cur.close()
    conn.close()

    results_by_semester = {}
    for row in result_rows:
        results_by_semester.setdefault(row["semester"], []).append(row)

    return render_template(
        "admin_manage_student.html",
        student=student,
        attendance=attendance_rows,
        results=results_by_semester,
        all_subjects=all_subjects,
        error=error,
    )


@app.route("/admin/student/<usn>/update-attendance", methods=["POST"])
def admin_update_attendance(usn):
    if not session.get("is_admin"):
        return redirect("/admin/login")

    subject_code = request.form["subject_code"]
    classes_held = request.form["classes_held"]
    classes_attended = request.form["classes_attended"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE attendance
           SET classes_held = %s, classes_attended = %s
           WHERE usn = %s AND subject_code = %s""",
        (classes_held, classes_attended, usn, subject_code),
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(f"/admin/student/{usn}")


def marks_to_grade(marks):
    """Same grading logic as the seed script — keeps grades consistent
    whether a result comes from seeding or manual admin entry."""
    bands = [
        (90, 100, "A+"), (80, 89, "A"), (70, 79, "B+"),
        (60, 69, "B"), (50, 59, "C"), (40, 49, "D"), (0, 39, "F"),
    ]
    for lo, hi, grade in bands:
        if lo <= marks <= hi:
            return grade
    return "F"


@app.route("/admin/student/<usn>/add-result", methods=["POST"])
def admin_add_result(usn):
    if not session.get("is_admin"):
        return redirect("/admin/login")

    semester = request.form["semester"]
    subject_code = request.form["subject_code"].strip().upper()
    marks = int(request.form["marks"])
    grade = marks_to_grade(marks)

    conn = get_db_connection()
    cur = conn.cursor()

    # Validate the subject code actually exists before touching results —
    # gives a clean error instead of letting the DB foreign key reject it
    cur.execute("SELECT 1 FROM subjects WHERE subject_code = %s", (subject_code,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        return redirect(f"/admin/student/{usn}?error=unknown_subject")

    # Check if a result for this student/semester/subject already exists — update instead of duplicating
    cur.execute(
        "SELECT id FROM results WHERE usn = %s AND semester = %s AND subject_code = %s",
        (usn, semester, subject_code),
    )
    existing = cur.fetchone()

    if existing:
        cur.execute(
            "UPDATE results SET marks = %s, grade = %s WHERE id = %s",
            (marks, grade, existing[0]),
        )
    else:
        cur.execute(
            "INSERT INTO results (usn, semester, subject_code, marks, grade) VALUES (%s, %s, %s, %s, %s)",
            (usn, semester, subject_code, marks, grade),
        )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(f"/admin/student/{usn}")


@app.route("/debug-student/<usn>")
def debug_student(usn):
    """Temporary diagnostic route — shows the raw DOB value stored for a
    student, to compare against what's being typed into the login form."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT usn, name, dob FROM students WHERE usn = %s", (usn,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    if student is None:
        return {"error": "not found"}
    return {
        "usn": student["usn"],
        "name": student["name"],
        "dob_raw": repr(student["dob"]),
        "dob_as_str": str(student["dob"]),
        "dob_type": str(type(student["dob"])),
    }


@app.route("/debug-env")
def debug_env():
    """Temporary diagnostic route — shows exactly what DB_HOST the running
    app sees, to debug why it might differ from what's set on Render.
    We'll delete this once the issue is resolved."""
    import os
    return {
        "DB_HOST_raw": repr(os.environ.get("DB_HOST")),
        "DB_PORT_raw": repr(os.environ.get("DB_PORT")),
        "DB_USER_raw": repr(os.environ.get("DB_USER")),
        "DB_SSL_CA_raw": repr(os.environ.get("DB_SSL_CA")),
        "all_DB_keys": [k for k in os.environ if k.startswith("DB_")],
    }


@app.route("/test-db")
def test_db():
    """Temporary route just to prove the DB connection works.
    We'll delete this once we build real routes."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"Connected! Found {count} students in the database."


if __name__ == "__main__":
    app.run(debug=True)