"""
Implements core banking operations.
"""

from __future__ import annotations

from models.accounts import Account
from models.enums import Currency, StatusCode
from models.messages import (
    BalanceResponse,
    CallbackUpdate,
    CloseAccountRequest,
    DepositWithdrawRequest,
    OpenAccountRequest,
    OpenAccountResponse,
    StandardResponse,
)
from storage.account_store import accounts, generate_account_number


class BankService:
    def __init__(self, monitor_service=None) -> None:
        self.monitor_service = monitor_service

    def _notify(self, update: CallbackUpdate) -> None:
        """
        Most important update function to update all monitor clients
        Call this function in all banking operations
        """
        if self.monitor_service is not None:
            self.monitor_service.notify_update(update)

    def open_account(self, request: OpenAccountRequest):
        if not request.name or request.name.strip() == "":
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account holder name cannot be empty",
            )

        if request.initial_balance < 0:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Initial balance cannot be negative",
            )

        if not isinstance(request.currency, Currency):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid currency type",
            )

        if len(request.password) != Account.PASSWORD_LENGTH:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Password must be 8 characters long",
            )

        account_number = generate_account_number()

        account = Account(
            account_number=account_number,
            owner_name=request.name,
            password=request.password,
            currency=request.currency,
            balance=request.initial_balance,
        )

        accounts[account_number] = account

        self._notify(
            CallbackUpdate(
                event_name="ACCOUNT_OPENED",
                account_number=account.account_number,
                owner_name=account.owner_name,
                currency=account.currency,
                balance=account.balance,
                note="Account opened successfully",
            )
        )

        return OpenAccountResponse(
            status=StatusCode.SUCCESS,
            message="Account opened successfully",
            account_number=account_number,
        )

    def close_account(self, request: CloseAccountRequest):
        if not request.name or request.name.strip() == "":
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account holder name cannot be empty",
            )

        if request.account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account not found",
            )

        account = accounts[request.account_number]

        if account.owner_name != request.name:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account name does not match",
            )

        if not account.check_password(request.password):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid password",
            )

        callback_update = CallbackUpdate(
            event_name="ACCOUNT_CLOSED",
            account_number=account.account_number,
            owner_name=account.owner_name,
            currency=account.currency,
            balance=account.balance,
            note="Account closed successfully",
        )

        del accounts[request.account_number]

        self._notify(callback_update)

        return StandardResponse(
            status=StatusCode.SUCCESS,
            message="Account closed successfully",
        )

    def deposit(self, request: DepositWithdrawRequest):
        if request.account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account not found",
            )

        account = accounts[request.account_number]

        if account.owner_name != request.name:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account name does not match",
            )

        if not account.check_password(request.password):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid password",
            )

        if request.amount <= 0:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Deposit amount must be positive",
            )

        if request.currency != account.currency:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Currency mismatch",
            )

        account.deposit(request.amount)

        self._notify(
            CallbackUpdate(
                event_name="DEPOSIT",
                account_number=account.account_number,
                owner_name=account.owner_name,
                currency=account.currency,
                balance=account.balance,
                note=f"Deposited {request.amount}",
            )
        )

        return BalanceResponse(
            status=StatusCode.SUCCESS,
            message="Deposit successful",
            account_number=account.account_number,
            balance=account.balance,
            currency=account.currency,
        )

    def withdraw(self, request: DepositWithdrawRequest):
        if request.account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account not found",
            )

        account = accounts[request.account_number]

        if account.owner_name != request.name:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account name does not match",
            )

        if not account.check_password(request.password):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid password",
            )

        if request.amount <= 0:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Withdrawal amount must be positive",
            )

        if not account.can_withdraw(request.amount):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Insufficient funds",
            )

        if request.currency != account.currency:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Currency mismatch",
            )

        account.withdraw(request.amount)

        self._notify(
            CallbackUpdate(
                event_name="WITHDRAW",
                account_number=account.account_number,
                owner_name=account.owner_name,
                currency=account.currency,
                balance=account.balance,
                note=f"Withdrew {request.amount}",
            )
        )

        return BalanceResponse(
            status=StatusCode.SUCCESS,
            message="Withdrawal successful",
            account_number=account.account_number,
            balance=account.balance,
            currency=account.currency,
        )

    def check_balance(self, request: BalanceInquiryRequest):
        if request.account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account not found",
            )

        account = accounts[request.account_number]

        if account.owner_name != request.name:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Account name does not match",
            )

        if not account.check_password(request.password):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid password",
            )
        
        self._notify(
            CallbackUpdate(
                event_name="BALANCE_INQUIRY",
                account_number=account.account_number,
                owner_name=account.owner_name,
                currency=account.currency,
                balance=account.balance,
                note=f"Balance inquiry successful",
            )
        )

        return BalanceResponse(
            status=StatusCode.SUCCESS,
            message="Balance inquiry successful",
            balance=account.balance,
            currency=account.currency,
        )
