"""
Simple one-off unit test to ensure that core banking functionalities work
"""
from storage.account_store import accounts
from services.bank_services import BankService
from models.messages import OpenAccountRequest, CloseAccountRequest
from models.enums import Currency

accounts.clear()

bank_service = BankService()

print("Before opening:", accounts)

open_req = OpenAccountRequest(
    name="Alice",
    password="12345678",
    currency=Currency.SGD,
    initial_balance=1000.0
)

open_res = bank_service.open_account(open_req)
print("Open response:", open_res)
print("After opening:", accounts)

if not accounts:
    raise RuntimeError("Account was not created")

acc_num = next(iter(accounts.keys()))

close_req = CloseAccountRequest(
    name="Alice",
    account_number=acc_num,
    password="12345678"
)

close_res = bank_service.close_account(close_req)
print("Close response:", close_res)
print("After closing:", accounts)