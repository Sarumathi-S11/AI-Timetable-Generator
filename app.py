import io
from pathlib import Path
import pandas as pd
import streamlit as st
from timetable_generator import TimetableGenerator, detect_conflicts, timetable_metrics

ROOT = Path(__file__).parent
DATA = ROOT / "data"
st.set_page_config(page_title="AI Timetable Generator", page_icon="🗓️", layout="wide")
st.title("🗓️ AI Timetable Generator")
st.caption("Automatic weekly timetable creation using Constraint Satisfaction and Backtracking")

@st.cache_data
def load_csv(name):
    return pd.read_csv(DATA / name)

courses_default = load_csv("courses.csv")
teachers_default = load_csv("teachers.csv")
rooms_default = load_csv("rooms.csv")

with st.sidebar:
    st.header("Timetable settings")
    days = st.multiselect("Working days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    slots = st.multiselect("Time slots", ["09:00-10:00", "10:00-11:00", "11:15-12:15", "12:15-13:15", "14:00-15:00", "15:00-16:00"], default=["09:00-10:00", "10:00-11:00", "11:15-12:15", "12:15-13:15", "14:00-15:00", "15:00-16:00"])
    st.info("Lunch break is represented by the gap between 12:15 and 14:00.")

tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Manage data", "Conflict checker", "About"])

with tab2:
    st.subheader("Course, teacher and room data")
    st.write("Edit the sample data below or upload replacement CSV files.")
    c1, c2, c3 = st.columns(3)
    with c1:
        courses = st.data_editor(courses_default, num_rows="dynamic", use_container_width=True, key="courses")
    with c2:
        teachers = st.data_editor(teachers_default, num_rows="dynamic", use_container_width=True, key="teachers")
    with c3:
        rooms = st.data_editor(rooms_default, num_rows="dynamic", use_container_width=True, key="rooms")
    st.download_button("Download courses CSV", courses.to_csv(index=False), "courses.csv", "text/csv")
    st.download_button("Download teachers CSV", teachers.to_csv(index=False), "teachers.csv", "text/csv")
    st.download_button("Download rooms CSV", rooms.to_csv(index=False), "rooms.csv", "text/csv")

with tab1:
    st.subheader("Create a weekly timetable")
    st.markdown("The generator schedules every required course session while avoiding teacher, room and course overlaps.")
    if st.button("✨ Generate timetable", type="primary", disabled=not days or not slots):
        try:
            generator = TimetableGenerator(courses, teachers, rooms, days, slots)
            timetable = generator.generate()
            st.session_state["timetable"] = timetable
            st.session_state["nodes"] = generator.nodes_visited
            st.success(f"Timetable generated successfully. Search nodes visited: {generator.nodes_visited}")
        except Exception as exc:
            st.error(str(exc))
    timetable = st.session_state.get("timetable")
    if timetable is not None:
        st.dataframe(timetable, use_container_width=True, hide_index=True)
        metrics = timetable_metrics(timetable, len(slots))
        cols = st.columns(5)
        for col, (label, value) in zip(cols, [
            ("Sessions", metrics["scheduled_sessions"]), ("Periods used", metrics["unique_periods_used"]),
            ("Teachers", metrics["teacher_count"]), ("Rooms", metrics["room_count"]),
            ("Conflicts", metrics["conflicts"])
        ]):
            col.metric(label, value)
        st.metric("Period utilization", f'{metrics["utilization_percent"]}%')
        csv_bytes = timetable.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv_bytes, "generated_timetable.csv", "text/csv")
        excel = io.BytesIO()
        with pd.ExcelWriter(excel, engine="openpyxl") as writer:
            timetable.to_excel(writer, index=False, sheet_name="Timetable")
        st.download_button("⬇️ Download Excel", excel.getvalue(), "generated_timetable.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption(f"Backtracking search nodes: {st.session_state.get('nodes', 0)}")

with tab3:
    st.subheader("Conflict detection")
    existing = st.session_state.get("timetable")
    if existing is None:
        st.info("Generate a timetable first to run the conflict checker.")
    else:
        conflicts = detect_conflicts(existing)
        if conflicts.empty:
            st.success("No teacher, room or course conflicts detected.")
        else:
            st.error(f"{len(conflicts)} conflict row(s) found.")
            st.dataframe(conflicts, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("How it works")
    st.markdown("""
    1. **Input data:** courses, teachers, rooms, student count and weekly sessions.
    2. **Constraints:** a teacher, room and course cannot be assigned to two classes in the same period.
    3. **Capacity:** a room must have enough seats for the course.
    4. **Teacher availability:** unavailable periods are read from the teacher CSV.
    5. **Search:** recursive backtracking tries a valid day/period and backtracks when a later assignment cannot fit.

    This is an educational scheduling prototype. Review generated schedules before real institutional use.
    """)
