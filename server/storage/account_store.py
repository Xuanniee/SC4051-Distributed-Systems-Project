"""
Stores and manages bank account records in memory.

This file should approximately contain:
	•	create account
	•	get account by account number
	•	update account
	•	delete account
"""
from typing import Dict
from models.accounts import Account

# For saving accounts in RAM
accounts: Dict[int, Account] = {}

_next_account_number: int = 1001

def generate_account_number() -> int:
    global _next_account_number
    acc_num = _next_account_number
    _next_account_number += 1
    return acc_num

def delete_account(account_number: int) -> bool:
    if account_number not in accounts:
        return False
    del accounts[account_number]
    return True