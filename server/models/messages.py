"""
Defines request and response data structures.

This file should approximately contain:
	•	OpenAccountRequest
	•	CloseAccountRequest
	•	DepositWithdrawRequest
	•	MonitorRequest
	•	BalanceInquiryRequest
	•	TransferRequest
	•	StandardResponse
	•	CallbackUpdate
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from models.enums import Currency, StatusCode


@dataclass
class CloseAccountRequest:
    name: str
    account_number: int
    password: str


@dataclass
class MonitorRequest:
    duration_seconds: int


@dataclass
class StandardResponse:
    status: StatusCode
    message: str
    balance: Optional[float] = None
    account_number: Optional[int] = None


@dataclass
class CallbackUpdate:
    event_name: str
    account_number: int
    owner_name: str
    currency: Currency
    balance: float
    note: str