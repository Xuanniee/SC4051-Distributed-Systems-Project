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
from storage.accounts_store import accounts, generate_account_number
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