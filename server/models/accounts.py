"""
Defines the account data model.

This file should approximately contain:
	•	Account dataclass or class
	•	account number
	•	owner name
	•	password
	•	currency
	•	balance
	•	any helper methods related to account state
"""

from __future__ import annotations
from dataclasses import dataclass

from models.enums import Currency

@dataclass
class Account:
    account_number: int
    owner_name: str
    password: str
    currency: Currency
    balance: float