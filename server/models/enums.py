"""
Defines enum types used throughout the backend.

This file should approximately contain:
	•	Currency
	•	OpCode
	•	StatusCode
	•	MessageType
"""
from enum import Enum

class Currency(Enum):
    SGD = 1
    USD = 2
    EUR = 3
    GBP = 4

class OpCode(Enum):
    OPEN_ACCOUNT = 1
    CLOSE_ACCOUNT = 2
    DEPOSIT = 3
    WITHDRAW = 4
    MONITOR_REGISTER = 5
    TRANSFER = 6

class StatusCode(Enum):
    SUCCESS = 0
    ERROR = 1
    INVALID_PASSWORD = 2
    ACCOUNT_NOT_FOUND = 3
    INSUFFICIENT_FUNDS = 4
    INVALID_REQUEST = 5

class MessageType(Enum):
    REQUEST = 1
    REPLY = 2
    CALLBACK = 3