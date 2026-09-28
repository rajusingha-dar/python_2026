"""
main.py
=======
Entry point. The while-loop menu structure is unchanged from your
original script — what changed is that every menu option now just
calls a METHOD on `system` (a ReportCardSystem object) instead of
calling a free function and passing the raw `students` dict around.

Run with:
    python main.py
"""

from report_card_system import ReportCardSystem


def print_menu():
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
    system = ReportCardSystem()   # one object now owns everything students-related
    running = True

    while running:
        print_menu()
        try:
            choice = int(input("Enter your choice (1-8): "))
        except ValueError:
            print("Please enter a number between 1 and 8.\n")
            continue

        if choice == 1:
            try:
                sid = int(input("Enter new student ID (positive number): "))
                if sid <= 0:
                    print("Student ID must be a positive number.\n")
                    continue
                name = input("Enter student name: ").strip()
                if not name:
                    print("Name cannot be empty.\n")
                    continue
                if system.add_student(sid, name):
                    print(f"Student '{name}' added with ID {sid}.\n")
                else:
                    print(f"Student ID {sid} already exists.\n")
            except ValueError:
                print("Invalid input. Student ID must be a whole number.\n")

        elif choice == 2:
            try:
                sid = int(input("Enter student ID: "))
                subject = input("Enter subject name: ").strip().title()
                marks = float(input(f"Enter marks for {subject} (0-100): "))
                if not (0 <= marks <= 100):
                    print("Marks must be between 0 and 100.\n")
                    continue
                if system.add_marks(sid, subject, marks):
                    print(f"Recorded {subject} = {marks} for student {sid}.\n")
                else:
                    print(f"No student found with ID {sid}.\n")
            except ValueError:
                print("Invalid input. Student ID and marks must be numbers.\n")

        elif choice == 3:
            try:
                sid = int(input("Enter student ID: "))
                card = system.report_card(sid)
                print(card if card else f"No student found with ID {sid}.\n")
            except ValueError:
                print("Student ID must be a number.\n")

        elif choice == 4:
            cards = system.all_report_cards()
            print("No students have been added yet.\n" if not cards else "\n".join(cards))

        elif choice == 5:
            passed, failed = system.pass_fail_summary()
            print("PASS / FAIL SUMMARY")
            print(f"Passed ({len(passed)}): {', '.join(passed) if passed else 'None'}")
            print(f"Failed ({len(failed)}): {', '.join(failed) if failed else 'None'}\n")

        elif choice == 6:
            top = system.top_scorers()
            print("TOP 3 STUDENTS")
            for rank, student in enumerate(top, start=1):
                print(f"{rank}. {student.name} - {student.average():.2f}%")
            print()

        elif choice == 7:
            subject = input("Enter subject name: ")
            avg = system.subject_average(subject)
            if avg is None:
                print(f"No marks recorded for subject '{subject.strip().title()}' yet.\n")
            else:
                print(f"Class average in {subject.strip().title()}: {avg:.2f}\n")

        elif choice == 8:
            running = False
            print("Exiting. Goodbye!")

        else:
            print("Invalid choice. Please select a number from 1 to 8.\n")


if __name__ == "__main__":
    main()
