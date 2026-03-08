"""
Defines enum types used throughout the backend.

This file should approximately contain:
	•	Currency
	•	OpCode
	•	StatusCode
	•	MessageType
"""
from __future__ import annotations
from enum import IntEnum

class Currency(IntEnum):
    SGD = 1
    USD = 2
    EUR = 3
    GBP = 4

class OpCode(IntEnum):
    OPEN_ACCOUNT = 1
    CLOSE_ACCOUNT = 2
    DEPOSIT = 3
    WITHDRAW = 4
    MONITOR = 5
    BALANCE_INQUIRY = 6
    TRANSFER = 7

class StatusCode(IntEnum):
    OK = 0
    ERROR = 1
    BAD_REQUEST = 2
    AUTH_FAILED = 3
    NOT_FOUND = 4