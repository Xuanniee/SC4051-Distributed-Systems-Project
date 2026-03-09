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
from dataclasses import dataclass
from typing import Optional
from models.enums import Currency, StatusCode

@dataclass
class OpenAccountRequest:
	name: str
	password: str
	currency: Currency
	initial_balance: float

@dataclass
class CloseAccountRequest:
	name: str
	account_number: int
	password: str

@dataclass
class DepositWithdrawRequest:
	name: str
	account_number: int
	password: str
	currency: Currency
	amount: float

@dataclass
class StandardResponse:
    status: StatusCode
    message: str


@dataclass
class OpenAccountResponse(StandardResponse):
    account_number: Optional[int] = None


@dataclass
class BalanceResponse(StandardResponse):
    account_number: Optional[int] = None
    balance: Optional[float] = None
    currency: Optional[Currency] = None