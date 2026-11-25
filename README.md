# AI Timetable Generator

**Assignment:** AI-EI-005  
**Student Code:** DAS012952  
**Portal Task ID:** 315

A Python-based academic timetable generator that uses Constraint Satisfaction Problem (CSP) concepts and recursive backtracking to create a weekly timetable without teacher, room, or course clashes.

## Features

- Course, teacher and room data management using CSV files
- Weekly timetable generation using recursive backtracking
- Teacher availability restrictions
- Room-capacity validation
- Teacher, room and course conflict detection
- Streamlit interface with editable data tables
- CSV and Excel timetable export
- Basic schedule metrics and automated tests

## Technology

- Python
- Pandas
- Streamlit
- Recursive backtracking / constraint satisfaction
- CSV and Excel

## Project structure

```text
AI-Timetable-Generator/
├── app.py
├── timetable_generator.py
├── requirements.txt
├── README.md
├── data/
│   ├── courses.csv
│   ├── teachers.csv
│   └── rooms.csv
├── output/
└── tests/
    └── test_generator.py
```

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\\Scripts\\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL shown in the terminal (normally http://localhost:8501).

## Input data format

- `courses.csv`: course ID, course name, teacher ID, room ID, student count and required sessions per week.
- `teachers.csv`: teacher ID, teacher name and optional unavailable periods. Use `Day|Slot` entries separated by semicolons, for example `Monday|09:00-10:00;Friday|14:00-15:00`.
- `rooms.csv`: room ID, room name and seating capacity.

## Scheduling logic

The program expands each course into the number of weekly sessions requested. It then uses recursive backtracking to assign each session to a day and time slot. A candidate is accepted only when:
- the teacher is not already teaching in that period;
- the room is not already occupied in that period;
- the same course is not scheduled twice in that period;
- the teacher is not marked unavailable; and
- the selected room has sufficient capacity.

If a later session cannot be placed, the algorithm removes the previous assignment and tries another slot. If no valid solution exists, the app reports that the constraints need to be reviewed.

## Tests

Run:

```bash
pytest -q
```

## Assignment submission links

Add your public repository URL and YouTube demonstration URL here before submitting.

- GitHub: `PASTE_YOUR_GITHUB_REPOSITORY_URL`
- YouTube demo: `PASTE_YOUR_YOUTUBE_VIDEO_URL`

## Screenshots

Add screenshots of:
1. Application home page
2. Course/teacher/room data tables
3. Generated timetable
4. Conflict checker showing no conflicts
5. CSV/Excel export or metrics

## Limitations and future improvements

This is a prototype using a basic backtracking search. Larger institutions may need stronger optimization such as MRV/degree heuristics, OR-Tools CP-SAT, teacher preference scoring, multi-section support and persistence through a database.
