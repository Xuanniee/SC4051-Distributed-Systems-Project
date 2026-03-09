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
from __future__ import annotations

from models.enums import StatusCode
from models.messages import StandardResponse
from services.callback_services import CallbackService
from storage.account_store import AccountStore


class BankService:
    """
    Implements banking operations against PostgreSQL-backed storage.
    """

    def __init__(self, account_store: AccountStore, callback_service: CallbackService) -> None:
        self.account_store = account_store
        self.callback_service = callback_service

    def close_account(self, name: str, account_number: int, password: str) -> StandardResponse:
        """
        Validates the account details and closes the account.
        After successful deletion, sends callback updates to active monitor clients.
        """

        account = self.account_store.get_account(account_number)

        if account is None:
            return StandardResponse(
                status=StatusCode.NOT_FOUND,
                message="Account not found",
            )

        if account.owner_name != name:
            return StandardResponse(
                status=StatusCode.BAD_REQUEST,
                message="Account owner name does not match",
            )

        if account.password != password:
            return StandardResponse(
                status=StatusCode.AUTH_FAILED,
                message="Authentication failed",
            )

        deleted_account = self.account_store.delete_account(account_number)

        if deleted_account is None:
            return StandardResponse(
                status=StatusCode.ERROR,
                message="Failed to close account",
            )

        self.callback_service.notify_account_closed(deleted_account)

        return StandardResponse(
            status=StatusCode.OK,
            message="Account closed successfully",
            account_number=deleted_account.account_number,
        )