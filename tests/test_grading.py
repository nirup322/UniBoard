"""Unit tests for marks_to_grade() — pure function, no DB needed."""

from app import marks_to_grade


def test_a_plus_boundary():
    assert marks_to_grade(90) == "A+"
    assert marks_to_grade(100) == "A+"


def test_a_grade():
    assert marks_to_grade(85) == "A"
    assert marks_to_grade(80) == "A"
    assert marks_to_grade(89) == "A"


def test_fail_boundary():
    assert marks_to_grade(39) == "F"
    assert marks_to_grade(0) == "F"


def test_pass_boundary():
    assert marks_to_grade(40) == "D"


def test_mid_range_grades():
    assert marks_to_grade(75) == "B+"
    assert marks_to_grade(65) == "B"
    assert marks_to_grade(55) == "C"