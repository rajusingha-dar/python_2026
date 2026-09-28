"""
account.py
==========
BankAccount - a single account's data and behavior, fully encapsulated.

See design_decisions.md for the full reasoning behind each choice below;
inline comments give the short version.
"""

from exceptions import InvalidAmountError, InsufficientFundsError, InvalidAccountTypeError


class BankAccount:
    """
    Represents one bank account belonging to one customer.

    All balance mutation happens ONLY through deposit(), withdraw(), or a
    Bank-coordinated transfer - there is deliberately no public setter for
    balance. The object protects its own invariants:
      - a SAVINGS account's balance may never go below MIN_SAVINGS_BALANCE
      - a CURRENT account may go negative, but never past -overdraft_limit

    Attributes
    ----------
    account_number : str (read-only property)
        Immutable identity of this account.
    owner_name : str (public, mutable)
        The account holder's name - no validation rules attached, so it
        stays a plain public attribute (see design_decisions.md, section 4).
    account_type : str (read-only property)
        "SAVINGS" or "CURRENT", fixed at creation.
    balance : float (read-only property)
        Current balance - can only change via deposit()/withdraw().
    transactions : list (read-only property, returns a COPY)
        Chronological log of every deposit/withdrawal on this account.
    """

    ACCOUNT_TYPES = ("SAVINGS", "CURRENT")   # class attribute: shared "allowed values"
    MIN_SAVINGS_BALANCE = 0.0                # class attribute: shared business rule
    total_accounts_created = 0               # class attribute: shared counter, ALL instances

    def __init__(self, account_number, owner_name, account_type="SAVINGS",
                 opening_balance=0.0, overdraft_limit=0.0):
        """
        Create a new, fully-validated bank account.

        Parameters
        ----------
        account_number : str
            Unique identifier. Stored privately, exposed only via a
            read-only property (identity must never change post-creation).
        owner_name : str
            Account holder's name. Must be non-empty.
        account_type : str, optional
            "SAVINGS" (default) or "CURRENT" (case-insensitive).
        opening_balance : float, optional
            Starting balance, must be >= 0. Defaults to 0.0.
        overdraft_limit : float, optional
            CURRENT accounts only: how far below zero the balance may go.
            Silently forced to 0 for SAVINGS accounts (they cannot overdraft).

        Raises
        ------
        ValueError
            If account_number or owner_name is empty / not a string.
        InvalidAccountTypeError
            If account_type is not one of ACCOUNT_TYPES.
        InvalidAmountError
            If opening_balance or overdraft_limit is negative or not a number.
        """
        if not account_number or not isinstance(account_number, str):
            raise ValueError("account_number must be a non-empty string.")
        if not owner_name or not isinstance(owner_name, str):
            raise ValueError("owner_name must be a non-empty string.")

        account_type = account_type.strip().upper()
        if account_type not in BankAccount.ACCOUNT_TYPES:
            raise InvalidAccountTypeError(
                f"'{account_type}' is not supported. Choose from {BankAccount.ACCOUNT_TYPES}."
            )

        self._validate_amount(opening_balance, allow_zero=True, label="opening_balance")
        self._validate_amount(overdraft_limit, allow_zero=True, label="overdraft_limit")

        self._account_number = account_number
        self.owner_name = owner_name
        self._account_type = account_type
        self._balance = float(opening_balance)
        self._overdraft_limit = float(overdraft_limit) if account_type == "CURRENT" else 0.0
        self._transactions = []   # private, per-instance list -> each account gets its OWN history

        if opening_balance > 0:
            self._record_transaction("OPENING_BALANCE", opening_balance)

        BankAccount.total_accounts_created += 1

    # ------------------------------------------------------------------
    # Read-only identity and state properties
    # ------------------------------------------------------------------

    @property
    def account_number(self):
        """Read-only: an account's identity must never change after creation."""
        return self._account_number

    @property
    def account_type(self):
        """Read-only: changing type post-creation would silently bypass overdraft rules."""
        return self._account_type

    @property
    def balance(self):
        """Read-only: the ONLY sanctioned mutators are deposit() and withdraw()."""
        return self._balance

    @property
    def transactions(self):
        """
        Read-only view of this account's transaction history.

        Returns a COPY of the internal list, never the list itself. If we
        returned self._transactions directly, external code could do
        `account.transactions.append(...)` or `.clear()` and corrupt the
        account's real history without going through _record_transaction.
        This is the mutable-attribute-leak lesson from Level 1, applied
        defensively at the API boundary.
        """
        return list(self._transactions)

    # ------------------------------------------------------------------
    # Public behavior - the ONLY sanctioned ways to change balance
    # ------------------------------------------------------------------

    def deposit(self, amount):
        """
        Add funds to the account.

        Parameters
        ----------
        amount : int or float
            Must be strictly positive.

        Raises
        ------
        InvalidAmountError
            If amount is not a positive number.
        """
        self._validate_amount(amount, allow_zero=False, label="deposit amount")
        self._balance += amount
        self._record_transaction("DEPOSIT", amount)

    def withdraw(self, amount):
        """
        Remove funds from the account, respecting this account's balance floor.

        SAVINGS accounts cannot go below MIN_SAVINGS_BALANCE (0).
        CURRENT accounts may go negative, but not past -overdraft_limit.

        Parameters
        ----------
        amount : int or float
            Must be strictly positive.

        Raises
        ------
        InvalidAmountError
            If amount is not a positive number.
        InsufficientFundsError
            If the withdrawal would breach the account's balance floor.
        """
        self._validate_amount(amount, allow_zero=False, label="withdrawal amount")

        floor = -self._overdraft_limit if self._account_type == "CURRENT" else BankAccount.MIN_SAVINGS_BALANCE
        if self._balance - amount < floor:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f} from {self._account_number}: "
                f"balance {self._balance:.2f} would fall below the allowed floor "
                f"of {floor:.2f} for a {self._account_type} account."
            )

        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)

    # ------------------------------------------------------------------
    # Static method - pure validation, needs neither self nor cls
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_amount(amount, allow_zero, label):
        """
        Validate that `amount` is a real number satisfying the sign rule.

        Static because this check depends on none of THIS account's state -
        it's pure input validation, reusable from anywhere in the class
        without needing self (an instance) or cls (the class itself).

        Parameters
        ----------
        amount : any
            The value to validate.
        allow_zero : bool
            If True, amount must be >= 0. If False, amount must be > 0.
        label : str
            Human-readable name of the value, used in the error message.

        Raises
        ------
        InvalidAmountError
            If amount is not a number, or violates the sign rule.
        """
        # bool is technically a subclass of int in Python (True == 1), so we
        # explicitly reject booleans to stop `deposit(True)` silently meaning "deposit 1".
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidAmountError(f"{label} must be a number, got {type(amount).__name__}.")
        if allow_zero and amount < 0:
            raise InvalidAmountError(f"{label} cannot be negative, got {amount}.")
        if not allow_zero and amount <= 0:
            raise InvalidAmountError(f"{label} must be greater than zero, got {amount}.")

    # ------------------------------------------------------------------
    # Private helper
    # ------------------------------------------------------------------

    def _record_transaction(self, kind, amount):
        """
        Append one entry to this account's transaction history.

        Private (leading underscore): only this class's own methods should
        ever write to _transactions. External code only ever reads history
        via the `transactions` property above.
        """
        self._transactions.append({
            "type": kind,
            "amount": round(amount, 2),
            "balance_after": round(self._balance, 2),
        })

    # ------------------------------------------------------------------
    # Class method - alternate constructor
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data):
        """
        Build a BankAccount from a plain dict (e.g. a JSON payload or DB row).

        Parameters
        ----------
        data : dict
            Required key: "account_number", "owner_name".
            Optional keys: "account_type", "opening_balance", "overdraft_limit".

        Returns
        -------
        BankAccount

        Raises
        ------
        KeyError
            If a required key is missing.
        """
        return cls(
            account_number=data["account_number"],
            owner_name=data["owner_name"],
            account_type=data.get("account_type", "SAVINGS"),
            opening_balance=data.get("opening_balance", 0.0),
            overdraft_limit=data.get("overdraft_limit", 0.0),
        )

    # ------------------------------------------------------------------
    # Dunder methods for sane printing/debugging
    # ------------------------------------------------------------------

    def __repr__(self):
        return (f"BankAccount(number={self._account_number!r}, owner={self.owner_name!r}, "
                f"type={self._account_type}, balance={self._balance:.2f})")

    def __str__(self):
        return f"[{self._account_type}] {self.owner_name} ({self._account_number}): {self._balance:.2f}"
