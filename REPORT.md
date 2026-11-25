# AI Timetable Generator — Project Report

**Assignment Code:** AI-EI-005  
**Student Code:** DAS012952  
**Portal Task ID:** 315

## 1. Objective
The objective is to develop an automated academic timetable generator that assigns course sessions to weekly days and time slots while satisfying teacher, room, course and room-capacity constraints.

## 2. Tools and technologies
Python is used for the scheduling logic. Pandas manages tabular input and output data. Streamlit provides a simple interactive interface. CSV files store courses, teachers and rooms, while OpenPyXL supports Excel export.

## 3. Methodology
The application reads course, teacher and room information from CSV files. Each course is expanded into its required number of weekly sessions. A recursive backtracking algorithm assigns sessions to available periods. Before placing a session, the algorithm checks whether the teacher, room and course are free and whether the teacher is available. Room capacity is validated before scheduling begins. If a later assignment becomes impossible, the algorithm backtracks and tries a different period.

## 4. Main features
- Course, teacher and room data management
- Automatic weekly timetable generation
- Teacher availability and room capacity checks
- Teacher, room and course conflict detection
- Timetable display with utilization metrics
- CSV and Excel export

## 5. Testing
Automated tests verify that generated schedules do not contain teacher/room/course overlaps and that insufficient room capacity is rejected. The application should also be manually checked with edited input data and different day/time selections.

## 6. Conclusion
The project demonstrates how constraint satisfaction and backtracking can automate a timetable scheduling task. The prototype is suitable for demonstrating the core workflow. Additional optimization and validation would be required before deployment in a real institution.

## 7. Submission evidence to add
Insert screenshots of the running application, editable input data, generated timetable, conflict-free result and export controls. Add the GitHub repository and YouTube demo URLs in the README before final submission.
