"""
UniBoard - Synthetic Data Generator (MySQL version)
Generates realistic fake CSE students (currently in semester 5),
with results for semesters 1-4 and attendance for semester 5 subjects.

Run this AFTER creating the schema (schema_mysql.sql) in your MySQL server.
Default XAMPP MySQL credentials: user='root', password='' (empty)
"""

import random
from faker import Faker
from db import get_db_connection

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

BRANCH = "CSE"
CURRENT_SEM = 5
PAST_SEMS = [1, 2, 3, 4]
NUM_STUDENTS = 120

SUBJECTS_BY_SEM = {
    1: [("CS101", "Programming in C"), ("MA101", "Engineering Mathematics I"), ("PH101", "Engineering Physics")],
    2: [("CS102", "Data Structures"), ("MA102", "Engineering Mathematics II"), ("EC102", "Basic Electronics")],
    3: [("CS201", "Object Oriented Programming"), ("CS202", "Discrete Mathematics"), ("CS203", "Digital Logic Design")],
    4: [("CS204", "Database Management Systems"), ("CS205", "Operating Systems"), ("CS206", "Computer Networks")],
    5: [("CS301", "Software Engineering"), ("CS302", "Design and Analysis of Algorithms"), ("CS303", "Web Technologies"), ("CS304", "Theory of Computation")],
}

GRADE_BANDS = [
    (90, 100, "A+"), (80, 89, "A"), (70, 79, "B+"),
    (60, 69, "B"), (50, 59, "C"), (40, 49, "D"), (0, 39, "F"),
]


def marks_to_grade(marks):
    for lo, hi, grade in GRADE_BANDS:
        if lo <= marks <= hi:
            return grade
    return "F"


def generate_usn(index):
    return f"1AB21CS{index:03d}"


def build_database():
    conn = get_db_connection()
    cur = conn.cursor()

    # Reset tables (respecting FK order)
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    cur.execute("DELETE FROM attendance")
    cur.execute("DELETE FROM results")
    cur.execute("DELETE FROM subjects")
    cur.execute("DELETE FROM students")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")

    # ---- Insert subjects ----
    for sem, subs in SUBJECTS_BY_SEM.items():
        for code, name in subs:
            cur.execute(
                "INSERT INTO subjects (subject_code, subject_name, semester, branch) VALUES (%s, %s, %s, %s)",
                (code, name, sem, BRANCH),
            )

    # ---- Insert students ----
    students = []
    for i in range(1, NUM_STUDENTS + 1):
        usn = generate_usn(i)
        name = fake.name()
        dob = fake.date_of_birth(minimum_age=19, maximum_age=22).isoformat()
        students.append((usn, name, dob))
        cur.execute(
            "INSERT INTO students (usn, name, dob, semester, branch) VALUES (%s, %s, %s, %s, %s)",
            (usn, name, dob, CURRENT_SEM, BRANCH),
        )

    # ---- Insert attendance (current semester subjects) ----
    current_subjects = SUBJECTS_BY_SEM[CURRENT_SEM]
    for usn, _, _ in students:
        for code, _ in current_subjects:
            classes_held = random.randint(35, 45)
            attendance_pct = random.choices(
                [random.uniform(0.85, 1.0), random.uniform(0.60, 0.84), random.uniform(0.40, 0.59)],
                weights=[0.65, 0.25, 0.10],
            )[0]
            classes_attended = int(classes_held * attendance_pct)
            cur.execute(
                """INSERT INTO attendance (usn, subject_code, classes_held, classes_attended)
                   VALUES (%s, %s, %s, %s)""",
                (usn, code, classes_held, classes_attended),
            )

    # ---- Insert results (past semesters) ----
    for usn, _, _ in students:
        for sem in PAST_SEMS:
            for code, _ in SUBJECTS_BY_SEM[sem]:
                marks = random.choices(
                    [random.randint(75, 100), random.randint(50, 74), random.randint(20, 39)],
                    weights=[0.55, 0.35, 0.10],
                )[0]
                grade = marks_to_grade(marks)
                cur.execute(
                    """INSERT INTO results (usn, semester, subject_code, marks, grade)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (usn, sem, code, marks, grade),
                )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Database populated successfully.")
    print(f"  Students: {NUM_STUDENTS}")
    print(f"  Subjects: {sum(len(v) for v in SUBJECTS_BY_SEM.values())}")
    print(f"  Attendance rows: {NUM_STUDENTS * len(current_subjects)}")
    print(f"  Results rows: {NUM_STUDENTS * sum(len(SUBJECTS_BY_SEM[s]) for s in PAST_SEMS)}")


if __name__ == "__main__":
    build_database()