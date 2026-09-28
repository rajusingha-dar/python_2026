"""
bank.py
=======
Bank - owns a collection of BankAccount objects and coordinates operations
that involve more than one account (like transfers).
"""

from account import BankAccount
from exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InvalidAmountError,
)


class Bank:
    """
    Represents one bank branch, holding many BankAccount objects.

    DESIGN NOTE - why transfer() lives HERE and not on BankAccount:
    A transfer is inherently a two-account operation. Putting it on
    BankAccount would force one account's method to reach into a
    DIFFERENT account's private internals (`other._balance += amount`),
    which breaks encapsulation - an object should manage only its OWN
    state. Bank already legitimately holds references to both accounts,
    so it's the correct place to coordinate the two-step operation.
    """

    total_banks_created = 0   # class attribute: shared across every Bank instance

    def __init__(self, name):
        """
        Parameters
        ----------
        name : str
            The bank's display name. Must be non-empty.

        Raises
        ------
        ValueError
            If name is empty or not a string.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Bank name must be a non-empty string.")
        self.name = name
        self._accounts = {}   # account_number -> BankAccount; private collection
        Bank.total_banks_created += 1

    def open_account(self, account_number, owner_name, account_type="SAVINGS",
                      opening_balance=0.0, overdraft_limit=0.0):
        """
        Create and register a new account at this bank.

        Raises
        ------
        DuplicateAccountError
            If account_number is already registered here.
        ValueError, InvalidAccountTypeError, InvalidAmountError
            Propagated from BankAccount's own validation.
        """
        if account_number in self._accounts:
            raise DuplicateAccountError(f"Account '{account_number}' already exists at {self.name}.")

        account = BankAccount(account_number, owner_name, account_type, opening_balance, overdraft_limit)
        self._accounts[account_number] = account
        return account

    def get_account(self, account_number):
        """
        Look up an account by its number.

        Raises
        ------
        AccountNotFoundError
            If no account with this number is registered here.
        """
        try:
            return self._accounts[account_number]
        except KeyError:
            raise AccountNotFoundError(f"No account found with number '{account_number}' at {self.name}.") from None

    def deposit(self, account_number, amount):
        """Convenience wrapper: look up the account, then deposit into it."""
        self.get_account(account_number).deposit(amount)

    def withdraw(self, account_number, amount):
        """Convenience wrapper: look up the account, then withdraw from it."""
        self.get_account(account_number).withdraw(amount)

    def transfer(self, from_account_number, to_account_number, amount):
        """
        Move funds from one account to another.

        The withdrawal happens first; the deposit only happens if the
        withdrawal succeeded. If the deposit step somehow fails afterwards
        (e.g. a validation edge case), the withdrawn amount is refunded to
        the source so a failed transfer never destroys money.

        Raises
        ------
        ValueError
            If from_account_number equals to_account_number.
        AccountNotFoundError
            If either account doesn't exist.
        InsufficientFundsError
            If the source account can't cover the amount.
        InvalidAmountError
            If amount fails validation.
        """
        if from_account_number == to_account_number:
            raise ValueError("Cannot transfer to the same account.")

        source = self.get_account(from_account_number)
        destination = self.get_account(to_account_number)

        source.withdraw(amount)   # raises BEFORE anything is deposited, if invalid
        try:
            destination.deposit(amount)
        except InvalidAmountError:
            source.deposit(amount)   # refund - keep the books balanced no matter what
            raise

    def close_account(self, account_number):
        """
        Remove an account from the bank.

        Only allowed when the balance is exactly zero, to prevent silently
        destroying money that was never withdrawn or transferred out.

        Raises
        ------
        AccountNotFoundError
            If the account doesn't exist.
        ValueError
            If the account's balance is not zero.
        """
        account = self.get_account(account_number)
        if account.balance != 0:
            raise ValueError(
                f"Cannot close '{account_number}': balance is {account.balance:.2f}, not zero. "
                "Withdraw or transfer the remaining funds first."
            )
        del self._accounts[account_number]

    @property
    def total_holdings(self):
        """Read-only, computed property: sum of every account's balance, recalculated on every access."""
        return sum(acc.balance for acc in self._accounts.values())

    def list_accounts(self):
        """Return a list of every BankAccount currently registered at this bank."""
        return list(self._accounts.values())

    def __len__(self):
        return len(self._accounts)

    def __repr__(self):
        return f"Bank(name={self.name!r}, accounts={len(self._accounts)}, total_holdings={self.total_holdings:.2f})"
