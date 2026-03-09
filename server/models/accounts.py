"""
Defines the account data model.
This file should approximately contain:
    •   Account dataclass or class
    •   account number
    •   owner name
    •   password
    •   currency
    •   balance
    •   any helper methods related to account state
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class Currency(Enum):
    SGD = 1
    USD = 2
    EUR = 3
    GBP = 4


@dataclass
class Account:
    account_number: int
    owner_name: str
    password: str
    currency: Currency
    balance: float = field(default=0.0)

    PASSWORD_LENGTH = 8

    def check_password(self, candidate: str) -> bool:
        return self.password == candidate

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        self.balance -= amount

    def can_withdraw(self, amount: float) -> bool:
        return amount > 0 and self.balance >= amount

    def to_dict(self) -> Dict[str, object]:
        return {
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "currency": self.currency.name,
            "balance": self.balance,
        }