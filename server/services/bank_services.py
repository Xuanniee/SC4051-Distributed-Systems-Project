"""
Implements core banking operations.

This file should approximately contain:
	•	open account
	•	close account
	•	deposit
	•	withdraw
	•	idempotent extra operation
	•	non-idempotent extra operation
	•	authentication checks
	•	account existence checks
	•	balance validation
"""
from models.accounts import Account
from models.enums import Currency, OpCode, StatusCode
from storage.account_store import accounts, generate_account_number
from models.messages import OpenAccountRequest, CloseAccountRequest, DepositWithdrawRequest, StandardResponse, OpenAccountResponse, BalanceResponse

def open_account(request: OpenAccountRequest) -> StandardResponse:
    if not request.name or request.name.strip() == "":
        return StandardResponse(status=StatusCode.ERROR, message="Account holder name cannot be empty")

    if request.initial_balance < 0:
        return StandardResponse(status=StatusCode.ERROR, message="Initial balance cannot be negative")

    if not isinstance(request.currency, Currency):
        return StandardResponse(status=StatusCode.ERROR, message="Invalid currency type")

    if len(request.password) != Account.PASSWORD_LENGTH:
        return StandardResponse(status=StatusCode.ERROR, message="Password must be 8 characters long")

    account_number = generate_account_number()

    account = Account(
        account_number=account_number,
        owner_name=request.name,
        password=request.password,
        currency=request.currency,
        balance=request.initial_balance,
    )

    accounts[account_number] = account

    return OpenAccountResponse(status=StatusCode.SUCCESS, message="Account opened successfully", account_number=account_number)

def close_account(request: CloseAccountRequest) -> StandardResponse:
	if not request.name or request.name.strip() == "":
		return StandardResponse(status=StatusCode.ERROR, message="Account holder name cannot be empty")

	if request.account_number not in accounts:
		return StandardResponse(status=StatusCode.ERROR, message="Account not found")

	if not accounts[request.account_number].check_password(request.password):
		return StandardResponse(status=StatusCode.ERROR, message="Invalid password")
	
	if accounts[request.account_number].name != request.name:
		return StandardResponse(status=StatusCode.ERROR, message="Account name does not match")

	del accounts[request.account_number]

	return StandardResponse(status=StatusCode.SUCCESS, message="Account closed successfully")

def deposit(request: DepositWithdrawRequest) -> StandardResponse:
	if request.account_number not in accounts:
		return StandardResponse(status=StatusCode.ERROR, message="Account not found")

	if accounts[request.account_number].name != request.name:
		return StandardResponse(status=StatusCode.ERROR, message="Account name does not match")

	if not accounts[request.account_number].check_password(request.password):
		return StandardResponse(status=StatusCode.ERROR, message="Invalid password")

	if request.amount <= 0:
		return StandardResponse(status=StatusCode.ERROR, message="Deposit amount must be positive")

	if request.currency != accounts[request.account_number].currency:
		return StandardResponse(status=StatusCode.ERROR, message="Currency mismatch")

	accounts[request.account_number].deposit(request.amount)

	return StandardResponse(status=StatusCode.SUCCESS, message="Deposit successful")

def withdraw(request: DepositWithdrawRequest) -> StandardResponse:
	if request.account_number not in accounts:
		return StandardResponse(status=StatusCode.ERROR, message="Account not found")

	if accounts[request.account_number].name != request.name:
		return StandardResponse(status=StatusCode.ERROR, message="Account name does not match")

	if not accounts[request.account_number].check_password(request.password):
		return StandardResponse(status=StatusCode.ERROR, message="Invalid password")

	if request.amount <= 0:
		return StandardResponse(status=StatusCode.ERROR, message="Withdrawal amount must be positive")

	if not accounts[request.account_number].can_withdraw(request.amount):
		return StandardResponse(status=StatusCode.ERROR, message="Insufficient funds")

	if request.currency != accounts[request.account_number].currency:
		return StandardResponse(status=StatusCode.ERROR, message="Currency mismatch")

	accounts[request.account_number].withdraw(request.amount)

	return StandardResponse(status=StatusCode.SUCCESS, message="Withdrawal successful", balance=accounts[request.account_number].balance)


# from __future__ import annotations

# from models.enums import StatusCode
# from models.messages import StandardResponse
# from services.callback_services import CallbackService
# from storage.account_store import AccountStore


# class BankService:
#     """
#     Implements banking operations against PostgreSQL-backed storage.
#     """

#     def __init__(self, account_store: AccountStore, callback_service: CallbackService) -> None:
#         self.account_store = account_store
#         self.callback_service = callback_service

#     def close_account(self, name: str, account_number: int, password: str) -> StandardResponse:
#         """
#         Validates the account details and closes the account.
#         After successful deletion, sends callback updates to active monitor clients.
#         """

#         account = self.account_store.get_account(account_number)

#         if account is None:
#             return StandardResponse(
#                 status=StatusCode.NOT_FOUND,
#                 message="Account not found",
#             )

#         if account.owner_name != name:
#             return StandardResponse(
#                 status=StatusCode.BAD_REQUEST,
#                 message="Account owner name does not match",
#             )

#         if account.password != password:
#             return StandardResponse(
#                 status=StatusCode.AUTH_FAILED,
#                 message="Authentication failed",
#             )

#         deleted_account = self.account_store.delete_account(account_number)

#         if deleted_account is None:
#             return StandardResponse(
#                 status=StatusCode.ERROR,
#                 message="Failed to close account",
#             )

#         self.callback_service.notify_account_closed(deleted_account)

#         return StandardResponse(
#             status=StatusCode.OK,
#             message="Account closed successfully",
#             account_number=deleted_account.account_number,
#         )

