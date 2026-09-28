# Instance Methods vs Class Methods vs Static Methods

> Companion to `oop_core_concepts.py` — same `Book` class, same examples.
> Written to answer one question clearly: **when do I use which one?**

---

## The one-sentence version of each

- **Instance method** — works with *one specific object's* own data. Needs `self`.
- **Class method** — works with data shared by the *whole class*, not any one object. Needs `cls`.
- **Static method** — doesn't need any object's data or the class's data. It's just a related helper function that happens to live inside the class.

---

## Why do we even need three kinds? (The core problem each one solves)

Every method in a class needs to answer one question first: **"What am I actually operating on?"**

- If the answer is *"this one particular object"* → instance method.
- If the answer is *"the class as a whole, shared by every object"* → class method.
- If the answer is *"nothing object-specific at all — I just need the inputs I'm given"* → static method.

Once you can answer that question for any method you're about to write, picking the right kind becomes automatic instead of guesswork.

---

## 1. Instance Methods — "Do something with THIS object"

**Simple explanation:** the default, most common kind of method. It reads or changes the data that belongs to *one specific object* — the object you called it on.

**Signal it needs `self`:** does the method use `self.something` anywhere inside it? If yes, it's an instance method.

```python
class Book:
    def __init__(self, title, copies):
        self.title = title
        self.copies = copies
        self.copies_checked_out = 0

    def check_out(self):                    # uses self.copies, self.copies_checked_out
        self.copies_checked_out += 1
```

```python
book1 = Book("Clean Code", 3)
book2 = Book("Fluent Python", 2)

book1.check_out()   # only affects book1's own data
```

**When to use it:** almost always — this is your default choice. Any time a method's job is "read or change something about this one object," it's an instance method. `check_out()`, `return_book()`, `describe()` in your `Book` class are all instance methods because each one only makes sense in the context of *one* particular book.

---

## 2. Class Methods — "Do something with the CLASS itself"

**Simple explanation:** a method that works with data shared across *every* object of the class — not any one object's private data. It receives `cls` (the class itself) instead of `self` (one object).

**Signal it needs `@classmethod` + `cls`:** does the method need to read or update a *class attribute* (something shared by all objects), or does it need to build and return a *new object* of the class?

```python
class Book:
    total_books = 0                    # shared by every Book

    def __init__(self, title, copies):
        self.title = title
        self.copies = copies
        Book.total_books += 1

    @classmethod
    def get_total_books(cls):
        return f"Total books: {cls.total_books}"

    @classmethod
    def from_string(cls, text):        # alternate constructor
        title, copies = text.split(",")
        return cls(title.strip(), int(copies))
```

```python
print(Book.get_total_books())          # doesn't belong to any ONE book
book3 = Book.from_string("Deep Work, 4")   # a second way to build a Book
```

**When to use it:**
1. **Reading or updating something shared across the whole class** (a running count, a shared setting, a registry of all created objects).
2. **Alternate constructors** — a second, differently-named way to build an object, when `__init__` alone can't cleanly cover every use case (building from a string, a dictionary, a file line, etc). This is the single most common real-world use of `@classmethod` you'll see in production Python code.

**Why `cls` instead of hardcoding `Book`?** If a subclass ever inherits this method, `cls` automatically refers to the *subclass*, not `Book`. Hardcoding the class name would silently break that.

---

## 3. Static Methods — "A helper that just belongs here"

**Simple explanation:** a method that doesn't touch `self` OR `cls` at all. It's a plain function that takes some inputs and returns a result — the only reason it lives inside the class is that it's conceptually *related* to what the class does.

**Signal it needs `@staticmethod`:** does the method use `self.anything` or `cls.anything`? If neither appears anywhere in the method body, it's static.

```python
class Book:
    @staticmethod
    def is_valid_isbn(isbn):
        digits_only = isbn.replace("-", "")
        return digits_only.isdigit() and len(digits_only) in (10, 13)
```

```python
print(Book.is_valid_isbn("978-0132350884"))   # True — no Book object needed anywhere
```

**When to use it:** a validation check, a calculation, or a small utility that's *about* books conceptually (so it makes sense to find it inside `Book`), but genuinely doesn't need any particular book's data or the class's shared data to do its job.

**A useful gut-check:** if you could just as easily pull the method out of the class entirely and make it a plain standalone function, and nothing about it would feel "lost" — that's a strong sign it should be `@staticmethod`, not an instance method.

---

## Side-by-side comparison

| | Instance Method | Class Method | Static Method |
|---|---|---|---|
| Decorator | *(none)* | `@classmethod` | `@staticmethod` |
| First parameter | `self` (one object) | `cls` (the class) | *(none)* |
| Can access object's own data? | Yes | No | No |
| Can access shared class data? | Yes (via `self.ClassName` or `self.__class__`) | Yes | No |
| Typical use | Everyday behavior on one object | Shared counters, alternate constructors | Standalone helper/validation logic |
| Called as | `book1.check_out()` | `Book.get_total_books()` | `Book.is_valid_isbn(x)` |
| Can also be called via an instance? | Yes (normal) | Yes, but rarely done this way | Yes, but rarely done this way |

---

## How to decide — a simple 3-question checklist

Ask these in order, for any method you're about to write:

1. **Does it need to read or change one specific object's own data (`self.something`)?**
   → Yes: it's an **instance method**. Stop here — this covers most methods you'll ever write.

2. **If not, does it need to read or change something shared by the whole class, or build a new object in an alternate way?**
   → Yes: it's a **class method**.

3. **If neither of the above is true — it just needs its own input arguments to do its job?**
   → It's a **static method**.

```text
Does the method use self.xxx?
        │
       Yes ──────────────► INSTANCE METHOD
        │
        No
        │
Does it use cls.xxx, or build/return a new object?
        │
       Yes ──────────────► CLASS METHOD
        │
        No
        │
        ▼
   STATIC METHOD
```

---

## Common mistakes to avoid

- **Making everything an instance method "just because."** If a method never actually uses `self`, that's a sign it should be static or a class method — not a rule you're breaking, just a method that's misplaced.
- **Overusing `@staticmethod`.** If a "static" method really is closely tied to a class's purpose but keeps needing more and more inputs passed in manually, it might actually want to be an instance or class method instead — ask whether it's *fighting* to avoid using `self`/`cls`.
- **Forgetting `cls` in a class method meant to be an alternate constructor**, and hardcoding the class name instead. This quietly breaks the method for any future subclass.
- **Assuming static methods "belong to no one."** They *do* conceptually belong to the class — that's the entire reason to nest them inside it instead of leaving them as loose functions elsewhere in the file.

---

## Quick recap, in plain words

- **Instance method** = "do this to *me* (this one object)."
- **Class method** = "do this for *all of us* (the whole class)," or "here's a different way to *make* one of us."
- **Static method** = "this fact or calculation is *related* to us, but doesn't need any of us specifically."
