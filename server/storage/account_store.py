"""
Stores and manages bank account records in memory.

This file should approximately contain:
	•	create account
	•	get account by account number
	•	update account
	•	delete account
"""
from typing import Dict
from models.account import Account

accounts: Dict[int, Account] = {}

_next_account_number: int = 1001


def generate_account_number() -> int:
    global _next_account_number
    acc_num = _next_account_number
    _next_account_number += 1
    return acc_num