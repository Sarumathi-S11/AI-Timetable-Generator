import pandas as pd
from timetable_generator import TimetableGenerator, detect_conflicts

def sample():
    courses = pd.DataFrame([
        {"course_id":"C1","course":"Python","teacher_id":"T1","room_id":"R1","students":20,"sessions_per_week":2},
        {"course_id":"C2","course":"SQL","teacher_id":"T1","room_id":"R2","students":20,"sessions_per_week":2},
    ])
    teachers = pd.DataFrame([{"teacher_id":"T1","teacher":"Teacher One","unavailable":""}])
    rooms = pd.DataFrame([
        {"room_id":"R1","room":"Room 1","capacity":30},
        {"room_id":"R2","room":"Room 2","capacity":30},
    ])
    return courses, teachers, rooms

def test_generator_avoids_conflicts():
    c, t, r = sample()
    result = TimetableGenerator(c, t, r, ["Mon"], ["09", "10", "11", "12"]).generate()
    assert len(result) == 4
    assert detect_conflicts(result).empty

def test_capacity_validation():
    c, t, r = sample()
    c.loc[0, "students"] = 100
    try:
        TimetableGenerator(c, t, r, ["Mon"], ["09", "10"]).generate()
    except ValueError as e:
        assert "capacity" in str(e).lower()
    else:
        raise AssertionError("Expected capacity validation error")
