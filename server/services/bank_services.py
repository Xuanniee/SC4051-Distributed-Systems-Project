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
    TransferRequest,
    BalanceInquiryRequest
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
    
    # Additional Non-Idempotent Operation for Project - Transfer Money
    def transfer(self, request: TransferRequest):
        # Check if the sender and receiver accounts exist
        if request.from_account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Sender bank account not found",
            )
        if request.to_account_number not in accounts:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Receiver account not found",
            )
        # Ensure not the same account
        if request.from_account_number == request.to_account_number:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Cannot transfer to the same account",
            )
        # Ensure that the sender is sending a positive value, cant be negative value to add monies to their own acc
        if request.amount <= 0:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Transfer amount must be positive",
            )

        sender_account = accounts[request.from_account_number]
        receiver_account = accounts[request.to_account_number]

        # Verify sender credentials to make sure it is a valid request
        if sender_account.owner_name != request.from_name:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Sender account name does not match. Invalid Request!",
            )
        if not sender_account.check_password(request.password):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Invalid password for Sender account Invalid Request!",
            )

        # Ensure that they have the same currency
        if sender_account.currency != request.currency or receiver_account.currency != request.currency:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Currency mismatch between sender and receiver bank accounts",
            )

        # Ensure that the sender have sufficient funds
        if not sender_account.can_withdraw(request.amount):
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Sender has insufficient funds! Invalid transfer!",
            )

        sender_account.withdraw(request.amount)
        receiver_account.deposit(request.amount)

        # Notify any monitoring client of the transfer transaction
        self._notify(
            CallbackUpdate(
                event_name="TRANSFER_OUT",
                account_number=sender_account.account_number,
                owner_name=sender_account.owner_name,
                currency=sender_account.currency,
                balance=sender_account.balance,
                note=f"Transferred {request.amount} to account {receiver_account.account_number}",
            )
        )
        self._notify(
            CallbackUpdate(
                event_name="TRANSFER_IN",
                account_number=receiver_account.account_number,
                owner_name=receiver_account.owner_name,
                currency=receiver_account.currency,
                balance=receiver_account.balance,
                note=f"Received {request.amount} from account {sender_account.account_number}",
            )
        )

        # Return the user the balance to indicate if transfer is successful or not
        return BalanceResponse(
            status=StatusCode.SUCCESS,
            message="Transfer successful",
            account_number=sender_account.account_number,
            balance=sender_account.balance,
            currency=sender_account.currency,
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
