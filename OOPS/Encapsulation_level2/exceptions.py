"""
exceptions.py
=============
Custom exceptions for the bank system.

WHY CUSTOM EXCEPTIONS INSTEAD OF ValueError/KeyError EVERYWHERE?
------------------------------------------------------------------
Using generic exceptions (ValueError, KeyError) for every failure means
callers can't distinguish "insufficient funds" from "bad account number"
without parsing error message strings - fragile and unpythonic. Custom,
named exceptions let calling code do:

    try:
        bank.withdraw(acc_no, amount)
    except InsufficientFundsError:
        offer_overdraft_upgrade()
    except AccountNotFoundError:
        ask_user_to_recheck_account_number()

Each failure mode is precisely catchable, and the exception NAME itself
documents what went wrong - no need to read a message string.

A NOTE ON INHERITANCE (a small, unavoidable preview of Level 3):
------------------------------------------------------------------
Every exception below inherits from `BankError`, which itself inherits
from Python's built-in `Exception`. This is really the only way custom
exceptions work in Python - `raise` and `except` are built around class
hierarchies. You don't need to understand inheritance deeply yet; just
notice the pattern: `class InvalidAmountError(BankError):` means
"InvalidAmountError IS-A BankError IS-A Exception." This lets calling
code choose how specific to be:

    except InvalidAmountError:   # catches only this one
    except BankError:            # catches ANY bank-related error
    except Exception:            # catches literally anything (too broad - avoid)

We'll cover inheritance itself properly in Level 3.
"""


class BankError(Exception):
    """Base class for every error this bank system can raise."""


class InvalidAmountError(BankError):
    """Raised when a monetary amount fails validation (negative, zero where not allowed, wrong type)."""


class InsufficientFundsError(BankError):
    """Raised when a withdrawal/transfer would breach an account's allowed balance floor."""


class AccountNotFoundError(BankError):
    """Raised when an operation references an account number that doesn't exist at this bank."""


class DuplicateAccountError(BankError):
    """Raised when attempting to open an account with a number that's already in use."""


class InvalidAccountTypeError(BankError):
    """Raised when creating an account with a type outside BankAccount.ACCOUNT_TYPES."""
