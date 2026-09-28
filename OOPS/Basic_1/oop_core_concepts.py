"""
oop_core_concepts.py
=====================
One file covering: classes, objects, constructors, self, and the three
kinds of methods - instance, class, and static.

Domain: a simple Library with Book objects.

Run:  python oop_core_concepts.py
"""


class Book:
    """A single book that can be checked out of the library."""

    # ---- CLASS ATTRIBUTE: shared by every Book object, not per-instance ----
    total_books = 0

    # ---- CONSTRUCTOR: runs automatically when a new Book() is created ----
    def __init__(self, title, author, copies):
        # 'self' means "the specific Book object being built right now"
        self.title = title
        self.author = author
        self.copies = copies          # how many copies the library owns
        self.copies_checked_out = 0   # starts at zero for every new book

        Book.total_books += 1         # every new Book increases the shared count

    # ---- INSTANCE METHOD: works on THIS book's own data (uses self) ----
    def check_out(self):
        """Check out one copy of this specific book, if any are available."""
        available = self.copies - self.copies_checked_out
        if available <= 0:
            print(f"'{self.title}' has no copies left to check out.")
            return
        self.copies_checked_out += 1
        print(f"You checked out '{self.title}'. Copies left: {self.available_copies()}")

    def return_book(self):
        """Return one checked-out copy of this specific book."""
        if self.copies_checked_out == 0:
            print(f"No copies of '{self.title}' are currently checked out.")
            return
        self.copies_checked_out -= 1
        print(f"You returned '{self.title}'. Copies left: {self.available_copies()}")

    def available_copies(self):
        """Another instance method: derived from THIS book's own state."""
        return self.copies - self.copies_checked_out

    def describe(self):
        return f"'{self.title}' by {self.author} - {self.available_copies()}/{self.copies} available"

    # ---- CLASS METHOD: works on the CLASS itself (uses cls, not self) ----
    @classmethod
    def get_total_books(cls):
        """Doesn't belong to any one book - it reports on the whole class."""
        return f"Total distinct book titles in the library: {cls.total_books}"

    @classmethod
    def from_string(cls, book_string):
        """
        Alternate constructor: build a Book from "Title, Author, Copies".
        Using cls(...) instead of Book(...) means this still works correctly
        even if a subclass of Book calls it.
        """
        title, author, copies = [part.strip() for part in book_string.split(",")]
        return cls(title, author, int(copies))

    # ---- STATIC METHOD: doesn't need self OR cls, just a related utility ----
    @staticmethod
    def is_valid_isbn(isbn):
        """
        Pure logic that only relates to books conceptually - no instance
        data, no class data, just a plain function grouped inside the class.
        """
        digits_only = isbn.replace("-", "")
        return digits_only.isdigit() and len(digits_only) in (10, 13)


# ------------------------------------------------------------------------
# DEMO
# ------------------------------------------------------------------------

def section(title_text):
    print("\n" + "=" * 55)
    print(title_text)
    print("=" * 55)


section("1. CREATING OBJECTS (the constructor runs automatically)")
book1 = Book("Clean Code", "Robert C. Martin", copies=3)
book2 = Book("Fluent Python", "Luciano Ramalho", copies=2)
print(book1.describe())
print(book2.describe())


section("2. INSTANCE METHODS - each object manages its OWN data")
book1.check_out()
book1.check_out()
book2.check_out()
book2.check_out()          # takes the last copy
book2.check_out()          # none left -> prints a message, no crash
print(book1.describe())
print(book2.describe())


section("3. self IN ACTION - same method, different object, different result")
print("book1.available_copies():", book1.available_copies())
print("book2.available_copies():", book2.available_copies())
print("^ one method definition, but 'self' makes each call operate on its own object")


section("4. CLASS METHOD - operates on the CLASS, shared across ALL books")
print(Book.get_total_books())
book3 = Book("The Pragmatic Programmer", "Andy Hunt", copies=1)
print("After adding a third book:")
print(Book.get_total_books())


section("5. CLASS METHOD AS ALTERNATE CONSTRUCTOR")
book4 = Book.from_string("Deep Work, Cal Newport, 4")
print("Built from a string ->", book4.describe())
print(Book.get_total_books())


section("6. STATIC METHOD - a utility that belongs with the class, needs no object")
print("Is '978-0132350884' a valid ISBN?", Book.is_valid_isbn("978-0132350884"))
print("Is 'abc123' a valid ISBN?", Book.is_valid_isbn("abc123"))
print("Called directly on the class - no Book object needed at all.")


section("7. RETURNING A BOOK")
book1.return_book()
print(book1.describe())


section("SUMMARY")
for book in (book1, book2, book3, book4):
    print(" -", book.describe())
print(Book.get_total_books())
