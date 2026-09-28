"""
demo.py
=======
Walks through the bank system deliberately pairing each HAPPY PATH with
its corresponding NEGATIVE/EDGE CASE, so you can see exactly which
exception fires and why, section by section.

    python demo.py
"""

from bank import Bank
from account import BankAccount
from exceptions import (
    BankError,
    InvalidAmountError,
    InsufficientFundsError,
    AccountNotFoundError,
    DuplicateAccountError,
    InvalidAccountTypeError,
)


def section(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


# ---------------------------------------------------------------------
section("1. OPENING ACCOUNTS - happy path")
# ---------------------------------------------------------------------

bank = Bank("Kolkata Central Bank")

raju_savings = bank.open_account("SAV-001", "Raju", "SAVINGS", opening_balance=5000)
priya_current = bank.open_account("CUR-001", "Priya", "CURRENT", opening_balance=1000, overdraft_limit=2000)

print("raju_savings:------------", raju_savings)
print("priya_current:-----------", priya_current)
print("Total accounts created across the whole program:", BankAccount.total_accounts_created)


# ---------------------------------------------------------------------
section("1b. OPENING ACCOUNTS - negative/edge cases")
# ---------------------------------------------------------------------

try:
    bank.open_account("SAV-001", "Someone Else")   # duplicate account number
except DuplicateAccountError as e:
    print("Caught DuplicateAccountError:", e)

try:
    bank.open_account("SAV-002", "Meera", account_type="CRYPTO")   # invalid type
except InvalidAccountTypeError as e:
    print("Caught InvalidAccountTypeError:", e)

try:
    bank.open_account("SAV-003", "Meera", opening_balance=-500)   # negative opening balance
except InvalidAmountError as e:
    print("Caught InvalidAmountError:", e)

try:
    bank.open_account("SAV-004", "")   # empty owner name
except ValueError as e:
    print("Caught ValueError:", e)


# ---------------------------------------------------------------------
section("2. DEPOSITS - happy path and negative cases")
# ---------------------------------------------------------------------

raju_savings.deposit(1500)
print("After deposit -> balance:", raju_savings.balance)

try:
    raju_savings.deposit(-100)   # negative deposit
except InvalidAmountError as e:
    print("Caught InvalidAmountError:", e)

try:
    raju_savings.deposit(0)   # zero deposit - not allowed (must be strictly positive)
except InvalidAmountError as e:
    print("Caught InvalidAmountError:", e)

try:
    raju_savings.deposit("500")   # wrong type entirely
except InvalidAmountError as e:
    print("Caught InvalidAmountError:", e)

try:
    raju_savings.deposit(True)   # bool masquerading as int - explicitly rejected
except InvalidAmountError as e:
    print("Caught InvalidAmountError:", e)


# ---------------------------------------------------------------------
section("3. WITHDRAWALS - SAVINGS floor vs CURRENT overdraft")
# ---------------------------------------------------------------------

raju_savings.withdraw(2000)
print("Raju (SAVINGS) after withdrawing 2000 -> balance:", raju_savings.balance)

try:
    raju_savings.withdraw(999999)   # far more than balance, SAVINGS has no overdraft
except InsufficientFundsError as e:
    print("Caught InsufficientFundsError (SAVINGS floor):", e)

# Priya's CURRENT account CAN go negative, up to her overdraft_limit of 2000
priya_current.withdraw(2500)   # balance was 1000 -> now -1500, still within -2000 floor
print("Priya (CURRENT) after withdrawing 2500 -> balance:", priya_current.balance)

try:
    priya_current.withdraw(1000)   # would push balance to -2500, past -2000 floor
except InsufficientFundsError as e:
    print("Caught InsufficientFundsError (CURRENT overdraft floor):", e)


# ---------------------------------------------------------------------
section("4. TRANSFERS - happy path and edge cases")
# ---------------------------------------------------------------------

meera_savings = bank.open_account("SAV-005", "Meera", "SAVINGS", opening_balance=3000)

bank.transfer("SAV-005", "SAV-001", 500)
print("After transfer 500, Meera:", meera_savings.balance, "| Raju:", raju_savings.balance)

try:
    bank.transfer("SAV-005", "SAV-005", 100)   # same account both sides
except ValueError as e:
    print("Caught ValueError (self-transfer):", e)

try:
    bank.transfer("SAV-005", "SAV-999", 100)   # destination doesn't exist
except AccountNotFoundError as e:
    print("Caught AccountNotFoundError:", e)

try:
    bank.transfer("SAV-005", "SAV-001", 999999)   # source can't cover it
except InsufficientFundsError as e:
    print("Caught InsufficientFundsError (transfer):", e)
print("Meera's balance UNCHANGED after the failed transfer above:", meera_savings.balance)


# ---------------------------------------------------------------------
section("5. ENCAPSULATION IN ACTION - protecting internal state")
# ---------------------------------------------------------------------

# balance has NO public setter - this line would raise AttributeError if uncommented:
# raju_savings.balance = 1000000
print("There is no way to do `raju_savings.balance = ...` - only deposit()/withdraw() can change it.")

# transactions returns a COPY, so mutating what you get back doesn't touch the real history
history_copy = raju_savings.transactions
history_copy.append({"type": "FAKE_HACK", "amount": 999999, "balance_after": 999999})
print("Length of the copy after appending a fake entry:", len(history_copy))
print("Length of the REAL history (unaffected):", len(raju_savings.transactions))


# ---------------------------------------------------------------------
section("6. CLOSING ACCOUNTS - must be zero balance first")
# ---------------------------------------------------------------------

temp_account = bank.open_account("SAV-006", "Temp Holder", opening_balance=100)

try:
    bank.close_account("SAV-006")   # non-zero balance
except ValueError as e:
    print("Caught ValueError (non-zero balance):", e)

temp_account.withdraw(100)   # zero it out first
bank.close_account("SAV-006")   # now succeeds
print("SAV-006 closed successfully. Total accounts remaining at bank:", len(bank))

try:
    bank.get_account("SAV-006")   # confirm it's really gone
except AccountNotFoundError as e:
    print("Confirmed removed - caught AccountNotFoundError:", e)


# ---------------------------------------------------------------------
section("7. ALTERNATE CONSTRUCTOR - from_dict()")
# ---------------------------------------------------------------------

payload = {
    "account_number": "SAV-007",
    "owner_name": "Ankit",
    "account_type": "savings",   # lowercase - gets normalized inside __init__
    "opening_balance": 750,
}
ankit_account = BankAccount.from_dict(payload)
print("Built via from_dict():", ankit_account)


# ---------------------------------------------------------------------
section("8. CATCHING BY BASE CLASS - BankError")
# ---------------------------------------------------------------------

# Because every specific exception inherits from BankError, code that doesn't
# care WHICH bank error occurred - only THAT one did - can catch broadly:
for bad_amount in [-50, 0, "oops"]:
    try:
        raju_savings.deposit(bad_amount)
    except BankError as e:
        print(f"deposit({bad_amount!r}) failed with a BankError: {e}")


# ---------------------------------------------------------------------
section("SUMMARY")
# ---------------------------------------------------------------------

print(bank)
print("Accounts at this bank:")
for acc in bank.list_accounts():
    print(" -", acc)
print("\nTotal Bank instances ever created:", Bank.total_banks_created)
print("Total BankAccount instances ever created:", BankAccount.total_accounts_created)
