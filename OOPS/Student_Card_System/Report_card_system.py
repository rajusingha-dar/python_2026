"""
Student Report Card & Grade Analyzer
=====================================

A menu-driven, console-based mini project that manages student records,
calculates grades, and generates simple class analytics.

Concepts demonstrated in this project:
    - print statements (formatted output, report cards)
    - if / else and nested if / else (grade calculation)
    - for loops (iterating over students and subjects)
    - while loops (the main menu loop)
    - lists (storing marks, storing sorted results)
    - list comprehension (pass/fail lists, subject-wise marks)
    - slicing (top-N students, list[:n])
    - dictionaries (student records, subject -> marks mapping)
    - docstrings (every function is documented)
    - exception handling (try / except for bad input, missing data)

Data model
----------
All student data lives in one dictionary called `students`:

    students = {
        1: {
            "name": "Raju",
            "scores": {"Math": 90, "Science": 85, "English": 78}
        },
        2: {
            "name": "Meera",
            "scores": {"Math": 60, "Science": 55, "English": 70}
        },
        ...
    }

- The outer dict key is the student ID (int).
- The outer dict value is a dict with the student's "name" and "scores".
- "scores" is itself a dict mapping subject name -> marks (0-100).
"""


def add_student(students):
    """
    Add a new student to the students dictionary.

    Prompts the user for a student ID and name, validates that the ID
    is a positive integer and is not already used, then creates an
    empty "scores" dictionary for that student.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.

    Raises
    ------
    Handles ValueError internally (invalid ID input) instead of
    propagating it, so the menu loop never crashes on bad input.
    """
    try:
        student_id = int(input("Enter new student ID (positive number): "))
        if student_id <= 0:
            print("Student ID must be a positive number.\n")
            return

        if student_id in students:
            print(f"Student ID {student_id} already exists.\n")
            return

        name = input("Enter student name: ").strip()
        if not name:
            print("Name cannot be empty.\n")
            return

        students[student_id] = {"name": name, "scores": {}}
        print(f"Student '{name}' added with ID {student_id}.\n")

    except ValueError:
        print("Invalid input. Student ID must be a whole number.\n")


def add_marks(students):
    """
    Add subject marks for an existing student.

    Prompts for a student ID, subject name, and marks (0-100), then
    stores the marks inside that student's "scores" dictionary.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.

    Raises
    ------
    Handles ValueError (non-numeric marks) and KeyError (unknown
    student ID) internally and reports a friendly message instead of
    crashing the program.
    """
    try:
        student_id = int(input("Enter student ID: "))

        if student_id not in students:
            raise KeyError(student_id)

        subject = input("Enter subject name: ").strip().title()
        marks = float(input(f"Enter marks for {subject} (0-100): "))

        if not (0 <= marks <= 100):
            print("Marks must be between 0 and 100.\n")
            return

        students[student_id]["scores"][subject] = marks
        print(f"Recorded {subject} = {marks} for {students[student_id]['name']}.\n")

    except ValueError:
        print("Invalid input. Student ID and marks must be numbers.\n")
    except KeyError:
        print(f"No student found with ID {student_id}.\n")


def calculate_grade(percentage):
    """
    Convert a percentage score into a letter grade.

    Uses nested if / else logic to demonstrate multi-level branching:
    first checks the failing boundary, then narrows down the passing
    grade band.

    Parameters
    ----------
    percentage : float
        The student's average percentage (0-100).

    Returns
    -------
    str
        One of "A+", "A", "B", "C", "D", or "F".
    """
    if percentage >= 40:
        # Passing branch: nested if-else narrows down the grade band
        if percentage >= 90:
            grade = "A+"
        else:
            if percentage >= 75:
                grade = "A"
            else:
                if percentage >= 60:
                    grade = "B"
                else:
                    if percentage >= 50:
                        grade = "C"
                    else:
                        grade = "D"
    else:
        # Failing branch
        grade = "F"

    return grade


def compute_average(scores):
    """
    Compute the average marks for a single student.

    Parameters
    ----------
    scores : dict
        Mapping of subject name -> marks for one student.

    Returns
    -------
    float
        The average of all recorded marks, or 0.0 if no marks exist.
    """
    if not scores:
        return 0.0

    marks_list = list(scores.values())  # dict values -> list
    total = sum(marks_list)
    average = total / len(marks_list)
    return average


def generate_report_card(students, student_id):
    """
    Print a formatted report card for a single student.

    Iterates over the student's subjects with a for loop, prints each
    subject's marks, then prints the overall average and grade.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.
    student_id : int
        The ID of the student whose report card should be printed.

    Raises
    ------
    Handles KeyError internally if the student ID does not exist.
    """
    try:
        student = students[student_id]
    except KeyError:
        print(f"No student found with ID {student_id}.\n")
        return

    print("-" * 35)
    print(f"REPORT CARD - {student['name']} (ID: {student_id})")
    print("-" * 35)

    if not student["scores"]:
        print("No marks recorded yet.\n")
        return

    for subject, marks in student["scores"].items():
        print(f"{subject:<15}: {marks:>6.2f}")

    average = compute_average(student["scores"])
    grade = calculate_grade(average)

    print("-" * 35)
    print(f"{'Average':<15}: {average:>6.2f}")
    print(f"{'Grade':<15}: {grade:>6}")
    print("-" * 35 + "\n")


def display_all_reports(students):
    """
    Print report cards for every student currently stored.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.
    """
    if not students:
        print("No students have been added yet.\n")
        return

    for student_id in students:          # for loop over dictionary keys
        generate_report_card(students, student_id)


def pass_fail_summary(students):
    """
    Build and print lists of passing and failing students.

    Uses list comprehension to filter student names based on their
    average percentage (pass threshold is 40%).

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.
    """
    if not students:
        print("No students have been added yet.\n")
        return

    # List comprehension: build (name, average) pairs
    averages = [(s["name"], compute_average(s["scores"])) for s in students.values()]

    passed = [name for name, avg in averages if avg >= 40]
    failed = [name for name, avg in averages if avg < 40]

    print("PASS / FAIL SUMMARY")
    print(f"Passed ({len(passed)}): {', '.join(passed) if passed else 'None'}")
    print(f"Failed ({len(failed)}): {', '.join(failed) if failed else 'None'}\n")


def top_scorers(students, n=3):
    """
    Display the top N students ranked by average marks.

    Builds a sorted list of (name, average) tuples, then uses list
    slicing to take only the top N entries.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.
    n : int, optional
        How many top students to display (default is 3).
    """
    if not students:
        print("No students have been added yet.\n")
        return

    averages = [(s["name"], compute_average(s["scores"])) for s in students.values()]

    # Sort by average, highest first
    ranked = sorted(averages, key=lambda pair: pair[1], reverse=True)

    top_n = ranked[:n]  # slicing: take the first n items

    print(f"TOP {n} STUDENTS")
    for rank, (name, avg) in enumerate(top_n, start=1):
        print(f"{rank}. {name} - {avg:.2f}%")
    print()


def subject_average(students, subject):
    """
    Calculate the class average for a single subject.

    Uses list comprehension to gather every recorded mark for the
    given subject across all students, then averages them.

    Parameters
    ----------
    students : dict
        The master dictionary holding all student records.
    subject : str
        The subject name to look up (case-insensitive, matched with
        .title() to line up with how add_marks() stores subjects).

    Raises
    ------
    Handles the case where no student has marks for the given
    subject by printing a message instead of raising ZeroDivisionError.
    """
    subject = subject.strip().title()

    # List comprehension with a condition: only marks for this subject
    marks_for_subject = [
        s["scores"][subject]
        for s in students.values()
        if subject in s["scores"]
    ]

    try:
        class_average = sum(marks_for_subject) / len(marks_for_subject)
        print(f"Class average in {subject}: {class_average:.2f}\n")
    except ZeroDivisionError:
        print(f"No marks recorded for subject '{subject}' yet.\n")


def print_menu():
    """
    Print the main menu options.

    Pure display function - contains only print statements.
    """
    print("=" * 40)
    print("--------->STUDENT REPORT CARD & GRADE ANALYZER")
    print("=" * 40)
    print("1. Add Student")
    print("2. Add Marks")
    print("3. View One Report Card")
    print("4. View All Report Cards")
    print("5. Pass / Fail Summary")
    print("6. Top Scorers")
    print("7. Subject-wise Class Average")
    print("8. Exit")
    print("=" * 40)


def main():
    """
    Run the interactive menu loop for the report card system.

    Uses a while loop to repeatedly show the menu and dispatch to the
    right function based on user input, until the user chooses to
    exit. All menu-choice parsing is wrapped in try/except so a
    non-numeric choice never crashes the program.
    """
    students = {}          # master dictionary of all students
    running = True         # controls the while loop

    while running:
        print_menu()  # function call to display the menu
        try:
            choice = int(input("Enter your choice (1-8): "))
        except ValueError:
            print("Please enter a number between 1 and 8.\n")
            continue

        if choice == 1:
            add_student(students)
        elif choice == 2:
            add_marks(students)
        elif choice == 3:
            try:
                sid = int(input("Enter student ID: "))
                generate_report_card(students, sid)
            except ValueError:
                print("Student ID must be a number.\n")
        elif choice == 4:
            display_all_reports(students)
        elif choice == 5:
            pass_fail_summary(students)
        elif choice == 6:
            top_scorers(students)
        elif choice == 7:
            subject = input("Enter subject name: ")
            subject_average(students, subject)
        elif choice == 8:
            running = False
            print("Exiting. Goodbye!")
        else:
            print("Invalid choice. Please select a number from 1 to 8.\n")

if __name__ == "__main__":
    main()