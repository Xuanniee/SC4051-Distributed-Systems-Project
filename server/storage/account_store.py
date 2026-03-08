"""
Stores and manages bank account records in memory.

This file should approximately contain:
	•	create account
	•	get account by account number
	•	update account
	•	delete account
"""
from __future__ import annotations

from typing import Optional

from app.models.account import Account
from app.models.enums import Currency
from app.storage.db import get_db_cursor

class AccountStore:
    """
    PostgreSQL-backed storage for bank accounts.
    """

    def get_account(self, account_number: int) -> Optional[Account]:
        query = """
            SELECT account_number, owner_name, password, currency, balance
            FROM accounts
            WHERE account_number = %s
        """

        with get_db_cursor(commit=False) as (_, cur):
            cur.execute(query, (account_number,))
            row = cur.fetchone()

        if row is None:
            return None

        return Account(
            account_number=row[0],
            owner_name=row[1],
            password=row[2],
            currency=Currency[row[3]],
            balance=float(row[4]),
        )

    def delete_account(self, account_number: int) -> Optional[Account]:
        """
        Deletes an account and returns the deleted row as an Account object.
        Uses RETURNING so the deleted account details are still available for callback notification.
        """

        query = """
            DELETE FROM accounts
            WHERE account_number = %s
            RETURNING account_number, owner_name, password, currency, balance
        """

        with get_db_cursor(commit=True) as (_, cur):
            cur.execute(query, (account_number,))
            row = cur.fetchone()

        if row is None:
            return None

        return Account(
            account_number=row[0],
            owner_name=row[1],
            password=row[2],
            currency=Currency[row[3]],
            balance=float(row[4]),
        )