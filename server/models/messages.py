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
class BalanceInquiryRequest:
	name: str
	account_number: int
	password: str

@dataclass
class StandardResponse:
    status: StatusCode
    message: str

@dataclass
class OpenAccountResponse(StandardResponse):
    account_number: Optional[int] = None

@dataclass
class BalanceResponse(StandardResponse):
    balance: Optional[float] = None
    currency: Optional[Currency] = None
    
# Monitoring API Messages ################################################################################################
@dataclass
class MonitorRequest:
    duration_seconds: int

@dataclass
class CallbackUpdate:
    event_name: str
    account_number: int
    owner_name: str
    currency: Currency
    balance: float
    note: str

# Metadata about a Request to implement at most once semantics
@dataclass(frozen=True)
class RequestMeta:
    client_id: str
    request_id: int