"""
oop_basics_simple.py
====================
Encapsulation + Inheritance + Access Modifiers + @property, in ONE small file.

Run:  python oop_basics_simple.py
"""

# ----------------------------------------------------------------------
# PART 1: ENCAPSULATION, ACCESS MODIFIERS and @property
# ----------------------------------------------------------------------

class Account:
    """A simple bank account. Data + the rules for that data live together."""

    def __init__(self, owner, balance, pin):
        self.owner = owner            # PUBLIC     -> anyone can read/change
        self._branch = "Kolkata"      # PROTECTED  -> "internal, please don't touch" (convention)
        self.__pin = pin              # PRIVATE    -> name-mangled, hard to reach from outside
        self.balance = balance        # goes through the SETTER below (so it gets validated)

    # ---- @property: the GETTER ----------------------------------------
    @property
    def balance(self):
        """Runs when you READ account.balance (looks like an attribute, is a method)."""
        return self._balance

    # ---- @balance.setter: the SETTER ----------------------------------
    @balance.setter
    def balance(self, value):
        """Runs when you WRITE account.balance = value. Rules are enforced here."""
        if value < 0:
            raise ValueError("Balance cannot be negative!")
        self._balance = value         # real data is stored in the protected _balance

    # ---- a method that safely uses the private data -------------------
    def check_pin(self, pin):
        """Outside code never sees __pin; it can only ask 'is this PIN correct?'"""
        return pin == self.__pin

    def deposit(self, amount):
        self.balance = self.balance + amount   # reuses the setter's validation

    def describe(self):
        return f"{self.owner} has {self.balance} at the {self._branch} branch"


# ----------------------------------------------------------------------
# PART 2: INHERITANCE
# ----------------------------------------------------------------------

class SavingsAccount(Account):        # SavingsAccount IS-A Account
    """Gets everything from Account, and adds interest on top."""

    def __init__(self, owner, balance, pin, interest_rate):
        super().__init__(owner, balance, pin)   # let the parent set up owner/balance/pin
        self.interest_rate = interest_rate      # new attribute, only for savings

    def add_interest(self):
        self.balance = self.balance + self.balance * self.interest_rate

    def describe(self):                          # method OVERRIDING, extended with super()
        return super().describe() + f" (interest rate: {self.interest_rate * 100:.0f}%)"

    def peek_protected(self):
        # A child CAN use the parent's protected attribute (that's what "protected" is for)
        return self._branch

    def peek_private(self):
        # A child can NOT use the parent's private attribute directly
        return self.__pin   # Python looks for _SavingsAccount__pin -> AttributeError


# ----------------------------------------------------------------------
# DEMO
# ----------------------------------------------------------------------

def title(text):
    print("\n" + "=" * 55)
    print(text)
    print("=" * 55)


title("1. PUBLIC - anyone can read and change it")
acc = Account("Raju", 1000, pin=4321)
print("owner:", acc.owner)
acc.owner = "Raju K"
print("owner after change:", acc.owner)

title("2. PROTECTED (_name) - works, but it's a 'please don't'")
print("acc._branch:", acc._branch, "  <- accessible, but you're not supposed to")

title("3. PRIVATE (__name) - Python hides it by renaming")
try:
    print(acc.__pin)
except AttributeError as e:
    print("acc.__pin failed:", e)
print("Real hidden name is _Account__pin:", acc._Account__pin, " (possible, but clearly a hack)")
print("Proper way -> acc.check_pin(4321):", acc.check_pin(4321))
print("Proper way -> acc.check_pin(1111):", acc.check_pin(1111))

title("4. @property GETTER and SETTER")
print("Read  (getter):", acc.balance)          # no parentheses, looks like an attribute
acc.balance = 1500                             # setter runs, value is valid
print("Write (setter): balance is now", acc.balance)
try:
    acc.balance = -50                          # setter rejects it
except ValueError as e:
    print("Invalid write blocked:", e)
print("Balance is still safe:", acc.balance)

title("5. INHERITANCE - child gets everything from parent")
sav = SavingsAccount("Priya", 2000, pin=1111, interest_rate=0.05)
sav.deposit(500)                               # deposit() was never written in SavingsAccount
print("deposit() inherited from Account -> balance:", sav.balance)
sav.add_interest()
print("add_interest() is new in child   -> balance:", sav.balance)
print("isinstance(sav, Account):", isinstance(sav, Account), "  (IS-A relationship)")

title("6. OVERRIDING + super()")
print(acc.describe())
print(sav.describe())                          # child's version, which extends the parent's

title("7. ACCESS LEVELS ACROSS INHERITANCE")
print("Child reading PROTECTED _branch:", sav.peek_protected())
try:
    sav.peek_private()
except AttributeError as e:
    print("Child reading PRIVATE __pin failed:", e)
print("Child still validates via inherited setter:")
try:
    sav.balance = -1
except ValueError as e:
    print("  blocked ->", e)
