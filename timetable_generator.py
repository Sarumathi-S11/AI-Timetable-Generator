"""Constraint-based AI timetable generator using recursive backtracking."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd

@dataclass(frozen=True)
class Session:
    course_id: str
    course: str
    teacher_id: str
    teacher: str
    room_id: str
    room: str
    duration: int = 1

class TimetableGenerator:
    def __init__(self, courses: pd.DataFrame, teachers: pd.DataFrame,
                 rooms: pd.DataFrame, days: List[str], slots: List[str]):
        self.courses = courses.fillna("").copy()
        self.teachers = teachers.fillna("").copy()
        self.rooms = rooms.fillna("").copy()
        self.days = days
        self.slots = slots
        self.schedule: List[dict] = []
        self.teacher_busy = set()
        self.room_busy = set()
        self.course_busy = set()
        self.sessions = self._build_sessions()
        self.nodes_visited = 0

    def _build_sessions(self) -> List[Session]:
        teacher_map = self.teachers.set_index("teacher_id").to_dict("index")
        room_map = self.rooms.set_index("room_id").to_dict("index")
        sessions = []
        for row in self.courses.to_dict("records"):
            tid = str(row["teacher_id"])
            rid = str(row["room_id"])
            if tid not in teacher_map:
                raise ValueError(f"Teacher ID {tid} for {row['course']} was not found.")
            if rid not in room_map:
                raise ValueError(f"Room ID {rid} for {row['course']} was not found.")
            teacher = teacher_map[tid]
            room = room_map[rid]
            if int(room["capacity"]) < int(row["students"]):
                raise ValueError(f"Room {room['room']} capacity is too small for {row['course']}.")
            for _ in range(int(row["sessions_per_week"])):
                sessions.append(Session(
                    str(row["course_id"]), str(row["course"]), tid,
                    str(teacher["teacher"]), rid, str(room["room"]), 1
                ))
        # Most constrained sessions first: teachers/courses with more sessions first.
        return sorted(sessions, key=lambda s: (-sum(1 for x in sessions if x.teacher_id == s.teacher_id),
                                               s.course, s.teacher_id))

    def _valid(self, session: Session, day: str, slot: str) -> bool:
        key = (day, slot)
        if (session.teacher_id, day, slot) in self.teacher_busy:
            return False
        if (session.room_id, day, slot) in self.room_busy:
            return False
        if (session.course_id, day, slot) in self.course_busy:
            return False
        # Optional teacher unavailable periods: semicolon-separated "Day|Slot"
        teacher_row = self.teachers[self.teachers["teacher_id"].astype(str) == session.teacher_id].iloc[0]
        unavailable = str(teacher_row.get("unavailable", "")).strip()
        if unavailable:
            blocked = {x.strip() for x in unavailable.split(";") if x.strip()}
            if f"{day}|{slot}" in blocked:
                return False
        return True

    def _place(self, session: Session, day: str, slot: str):
        self.schedule.append({
            "day": day, "time": slot, "course_id": session.course_id,
            "course": session.course, "teacher_id": session.teacher_id,
            "teacher": session.teacher, "room_id": session.room_id, "room": session.room
        })
        self.teacher_busy.add((session.teacher_id, day, slot))
        self.room_busy.add((session.room_id, day, slot))
        self.course_busy.add((session.course_id, day, slot))

    def _remove(self, session: Session, day: str, slot: str):
        self.schedule.pop()
        self.teacher_busy.remove((session.teacher_id, day, slot))
        self.room_busy.remove((session.room_id, day, slot))
        self.course_busy.remove((session.course_id, day, slot))

    def _backtrack(self, index: int = 0) -> bool:
        if index == len(self.sessions):
            return True
        session = self.sessions[index]
        for day in self.days:
            for slot in self.slots:
                self.nodes_visited += 1
                if self._valid(session, day, slot):
                    self._place(session, day, slot)
                    if self._backtrack(index + 1):
                        return True
                    self._remove(session, day, slot)
        return False

    def generate(self) -> pd.DataFrame:
        self.schedule = []
        self.teacher_busy.clear()
        self.room_busy.clear()
        self.course_busy.clear()
        self.nodes_visited = 0
        if not self._backtrack():
            raise RuntimeError(
                "No valid timetable found with the current constraints. "
                "Add more time slots/rooms or review teacher availability and course sessions."
            )
        result = pd.DataFrame(self.schedule)
        day_order = {d: i for i, d in enumerate(self.days)}
        slot_order = {s: i for i, s in enumerate(self.slots)}
        result["_day"] = result["day"].map(day_order)
        result["_slot"] = result["time"].map(slot_order)
        return result.sort_values(["_day", "_slot", "course"]).drop(columns=["_day", "_slot"]).reset_index(drop=True)

def detect_conflicts(timetable: pd.DataFrame) -> pd.DataFrame:
    """Return rows involved in teacher, room, or course double-booking."""
    if timetable.empty:
        return pd.DataFrame(columns=list(timetable.columns) + ["conflict"])
    parts = []
    for field, label in [("teacher_id", "Teacher double-booked"),
                         ("room_id", "Room double-booked"),
                         ("course_id", "Course double-booked")]:
        duplicated = timetable.duplicated(subset=["day", "time", field], keep=False)
        if duplicated.any():
            temp = timetable.loc[duplicated].copy()
            temp["conflict"] = label
            parts.append(temp)
    if not parts:
        return pd.DataFrame(columns=list(timetable.columns) + ["conflict"])
    return pd.concat(parts).drop_duplicates().sort_values(["day", "time"]).reset_index(drop=True)

def timetable_metrics(timetable: pd.DataFrame, slots_per_day: int) -> dict:
    total = len(timetable)
    unique_periods = timetable[["day", "time"]].drop_duplicates().shape[0] if total else 0
    return {
        "scheduled_sessions": total,
        "unique_periods_used": unique_periods,
        "teacher_count": timetable["teacher_id"].nunique() if total else 0,
        "room_count": timetable["room_id"].nunique() if total else 0,
        "conflicts": len(detect_conflicts(timetable)),
        "utilization_percent": round((unique_periods / (5 * slots_per_day)) * 100, 1) if slots_per_day else 0
    }
