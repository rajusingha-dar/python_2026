# Design Decisions — Bank Account Management System

This doc exists to answer "why did I do it this way" for every choice in
this project that isn't self-evident. Read it alongside `account.py` and
`bank.py` — each heading below maps to a specific piece of that code.

---

## 1. Why is `balance` a read-only property with no public setter?

**The decision:** `self._balance` is private; `balance` is exposed only as
a `@property` with a getter, no setter. The *only* way to change it is
`deposit()` or `withdraw()`.

**Why:** if `balance` were a plain public attribute, any code anywhere
could do `account.balance = -999999` or `account.balance = "lots"` and the
object would have no say in it. By funneling every change through two
methods, those two methods become the **single enforcement point** for
every business rule: "amount must be positive," "savings can't go below
zero," "current can't exceed its overdraft limit." One point of
enforcement means one place to get it right, and one place to test.

This is the actual *purpose* of encapsulation — not hiding data out of
secrecy, but making it structurally impossible for the object to end up
in a state that violates its own rules.

---

## 2. Why are `account_number` and `account_type` also read-only?

**The decision:** both are private, exposed as read-only properties.

**Why:** an account's number is its **identity** — if it could be
reassigned, `bank._accounts[account_number]` (the dict keyed by that
number) would silently point to the wrong entry. And `account_type`
determines which balance-floor rule applies (`0` for SAVINGS vs.
`-overdraft_limit` for CURRENT); allowing it to change post-creation would
let someone open a SAVINGS account, flip it to CURRENT, and suddenly
overdraft a type of account that was never supposed to allow it.

**The underlying principle:** ask "if this attribute changed after
creation, would anything else in the object become inconsistent?" If yes,
it should be read-only.

---

## 3. Why is `owner_name` a plain public attribute, with no property at all?

**The decision:** `self.owner_name = owner_name` — direct, no `@property`.

**Why:** there's no rule protecting it (a name can freely change — legal
name changes happen), and no other state depends on its value being one
thing or another. Wrapping it in a property here would be the exact
over-engineering the Level 2 theory warned against — properties earn
their place through validation or computation, not by default. This is a
deliberate contrast in the same file: notice `owner_name` (plain) sitting
right next to `balance` (property) — same class, different needs.

---

## 4. Why does `transactions` return `list(self._transactions)` instead of `self._transactions`?

**The decision:** the getter returns a **copy** of the internal list.

**Why:** this is the Level 1 "mutable attribute leak" trap, applied
defensively. If the property returned the real list, this would compile
and run without error, and would be *devastating*:

```python
account.transactions.clear()   # wipes real history — looks read-only, isn't
```

Returning a copy means external code can inspect, filter, or iterate the
history freely, but can never mutate the account's actual record of what
happened. `demo.py` section 5 proves this: appending to the returned copy
doesn't change what `account.transactions` returns on the next call.

---

## 5. Why custom exceptions (`InsufficientFundsError`, etc.) instead of raising `ValueError` everywhere?

**The decision:** a small hierarchy — `BankError` as the base, with
`InvalidAmountError`, `InsufficientFundsError`, `AccountNotFoundError`,
`DuplicateAccountError`, and `InvalidAccountTypeError` underneath it.

**Why:** think about what calling code needs to *do* differently for each
failure. "Insufficient funds" might prompt "offer an overdraft upgrade."
"Account not found" might prompt "let the user re-enter the account
number." A generic `ValueError` for both gives the caller nothing to
branch on except parsing the message text — brittle and easy to break
silently if the wording ever changes.

Naming the exception *is* the documentation: `except InsufficientFundsError`
reads exactly as clearly as its own doc-comment would. And because they
all share `BankError` as a base, code that only cares "did *something*
bank-related fail" can catch broadly (see `demo.py` section 8) without
losing the ability to be specific elsewhere.

---

## 6. Why does `withdraw()` compute a `floor` instead of writing two separate methods for SAVINGS and CURRENT?

**The decision:** one `withdraw()` method computes the applicable floor
(`0` or `-overdraft_limit`) based on `self._account_type`, then applies
one shared check.

**Why:** at this stage (before Level 3: Inheritance), the honest
alternative would be duplicating the entire withdraw logic into two
near-identical methods differing only in the floor value — a DRY
violation waiting to cause a bug the moment one copy gets updated and the
other doesn't. Computing the floor as a small piece of data, then reusing
one code path, keeps the actual withdrawal logic — validate, check floor,
subtract, log — written exactly once.

**Where this is heading:** this `if account_type == "CURRENT"` branching
is *exactly* the kind of code Level 3 (Inheritance) and Level 11 (SOLID's
Open/Closed Principle) will teach you to replace with `SavingsAccount` and
`CurrentAccount` subclasses, each overriding a `_balance_floor()` method.
Right now this branch is the correct, honest solution for your current
toolkit — recognizing why it'll eventually become awkward as more account
types appear is exactly the instinct SOLID is trying to build.

---

## 7. Why does `Bank.transfer()` exist on `Bank`, not as a method on `BankAccount`?

**The decision:** `source.transfer_to(destination, amount)` was the
tempting alternative; instead, `Bank.transfer(from_no, to_no, amount)`
coordinates both accounts from the outside.

**Why:** if `transfer_to` lived on `BankAccount`, that method's body would
need to do `other_account._balance += amount` — reaching directly into
*another* object's private internals. That defeats the entire point of
making `_balance` private: an account's balance should only ever be
touched by that account's own methods. `Bank` already legitimately holds
both accounts, so it's the right owner of any operation that spans more
than one — it calls each account's own public `deposit()`/`withdraw()`,
never touching a private attribute across the boundary.

---

## 8. Why does a failed transfer refund the source instead of just raising an error?

**The decision:** in `Bank.transfer()`, `source.withdraw()` happens
first; if `destination.deposit()` then fails, the code calls
`source.deposit(amount)` to reverse the withdrawal before re-raising.

**Why:** think through what happens *without* the refund: money leaves
the source account, the deposit into the destination fails, and the
amount has vanished from the system entirely — a real bug that would be
disastrous in an actual bank. This is what "negative scenario handling"
means in practice: not just catching an exception, but asking "what state
is the *system* left in when this fails partway through?" A two-step
operation that can fail between its steps needs an explicit plan for that
in-between state.

---

## 9. Why is `close_account()` only allowed at a zero balance, instead of just deleting the account?

**The decision:** `close_account()` raises `ValueError` if
`account.balance != 0`.

**Why:** deleting a `BankAccount` object with a non-zero balance would
silently destroy that money — no exception, no error, just gone. Forcing
the balance to zero first (via a withdrawal or transfer the caller
initiates deliberately) makes fund disappearance a conscious, visible
action rather than a side effect of tidying up a dictionary.

---

## 10. Why is `_validate_amount` a `@staticmethod` instead of a regular method or a free function?

**The decision:** `@staticmethod` on `BankAccount._validate_amount`.

**Why not a regular method?** It never reads or writes `self` — it
doesn't need any particular account's data, just the raw `amount` value
passed in. Making it a regular method would be misleading: it implies a
dependency on instance state that doesn't exist.

**Why not a free function outside the class entirely?** Because this
validation is *conceptually* about what a valid bank-account amount is —
it belongs with the class, for discoverability (`BankAccount._validate_amount`
is easy to find; a loose `validate_amount()` function floating in the
module is not) and to signal it's part of this class's contract, even
though it doesn't touch instance state.

---

## 11. Why does `from_dict()` use `@classmethod` and `cls(...)` instead of just being a free function that returns `BankAccount(...)`?

**The decision:** `@classmethod def from_dict(cls, data): return cls(...)`.

**Why:** using `cls(...)` instead of hardcoding `BankAccount(...)` means
this alternate-constructor pattern would still work correctly even from a
subclass, without needing to override `from_dict` itself (relevant once
Level 3 introduces `SavingsAccount(BankAccount)`-style subclasses). It's a
small piece of future-proofing that costs nothing today.

---

## 12. Why are `total_accounts_created` and `total_banks_created` class attributes instead of, say, a global variable?

**The decision:** `BankAccount.total_accounts_created` and
`Bank.total_banks_created`, incremented inside each `__init__`.

**Why:** a global variable would work, but it lives *outside* the class
that's actually responsible for the count, disconnected from the object
whose creation it's tracking. A class attribute keeps the counter
logically attached to the thing being counted — `BankAccount.total_accounts_created`
reads as self-documenting in a way `_account_counter` sitting alone at
module level never would, and it can't accidentally be shadowed by an
unrelated variable of the same name elsewhere in a larger program.

---

## 13. Why split the code into four files instead of one big script?

**The decision:** `exceptions.py`, `account.py`, `bank.py`, `demo.py`.

**Why:** each file has one clear reason to change:
- `exceptions.py` changes only when the system needs a new *kind* of
  failure to represent.
- `account.py` changes only when a single account's own rules change.
- `bank.py` changes only when cross-account coordination logic changes.
- `demo.py` changes only when you want to exercise the system differently.

This is a preview of what Level 11 (SOLID) will name explicitly as the
**Single Responsibility Principle** — you don't need the formal name yet
to feel the benefit: if you need to add a `FixedDepositAccount` type
tomorrow, you know immediately that means editing `account.py`, and nothing
else, because that's the one file responsible for what an account *is*.

---

## Summary — the one habit worth taking away

Every decision above traces back to the same question, asked repeatedly:

> **"If I allow this to be changed/accessed directly from outside, what
> invariant could break, and who would be responsible for it breaking?"**

Any time the answer is "something could break, and no one specific piece
of code would be responsible for catching it" — that's exactly where a
private attribute, a property, a custom exception, or a dedicated method
belongs.
