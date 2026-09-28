"""
student.py
==========
The `Student` class. Each Student OBJECT owns its own name, ID, and
scores dict — this replaces the old per-student sub-dictionary that
used to live inside the master `students` dict.
"""


class Student:
    """Represents a single student and their subject-wise marks."""

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.scores = {}   # subject (str) -> marks (float), owned by THIS student

    # ---- instance methods: things a Student can do to its own data ----

    def add_marks(self, subject, marks):
        """Record marks for one subject on this student."""
        self.scores[subject] = marks

    def average(self):
        """Return this student's average across all recorded subjects."""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def grade(self):
        """Return this student's letter grade, based on their average."""
        return Student.calculate_grade(self.average())

    def has_passed(self):
        """True if this student's average meets the passing threshold."""
        return self.average() >= 40

    def report_card(self):
        """Return a formatted report card string for this student."""
        lines = ["-" * 35, f"REPORT CARD - {self.name} (ID: {self.student_id})", "-" * 35]

        if not self.scores:
            lines.append("No marks recorded yet.\n")
            return "\n".join(lines)

        for subject, marks in self.scores.items():
            lines.append(f"{subject:<15}: {marks:>6.2f}")

        lines.append("-" * 35)
        lines.append(f"{'Average':<15}: {self.average():>6.2f}")
        lines.append(f"{'Grade':<15}: {self.grade():>6}")
        lines.append("-" * 35 + "\n")
        return "\n".join(lines)

    # ---- static method: grade logic doesn't need self OR cls at all ----

    @staticmethod
    def calculate_grade(percentage):
        """
        Convert a percentage into a letter grade.
        Static because this is pure logic on a number — it doesn't
        need any particular student's data, just the number passed in.
        """
        if percentage >= 90:
            return "A+"
        elif percentage >= 75:
            return "A"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"

    # ---- dunder method: nicer default printing (a small preview of Level 5) ----

    def __repr__(self):
        return f"Student(id={self.student_id}, name={self.name!r}, avg={self.average():.2f})"
