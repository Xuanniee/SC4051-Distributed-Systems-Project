"""
Serialisation and De-serialisation layer

For encoding and decoding various types of messags to the UDP socket
"""
from __future__ import annotations

from models.enums import Currency, StatusCode
from models.messages import (
    BalanceResponse,
    CallbackUpdate,
    CloseAccountRequest,
    DepositWithdrawRequest,
    MonitorRequest,
    OpenAccountRequest,
    OpenAccountResponse,
    StandardResponse,
)
from protocols.marshaller import BufferReader, BufferWriter

def encode_open_account_request(message: OpenAccountRequest) -> bytes:
    writer = BufferWriter()
    writer.write_str(message.name)
    writer.write_str(message.password)
    writer.write_u8(message.currency.value)
    writer.write_f64(message.initial_balance)
    return writer.to_bytes()

def decode_open_account_request(payload: bytes) -> OpenAccountRequest:
    reader = BufferReader(payload)
    return OpenAccountRequest(
        name=reader.read_str(),
        password=reader.read_str(),
        currency=Currency(reader.read_u8()),
        initial_balance=reader.read_f64(),
    )

def encode_close_account_request(message: CloseAccountRequest) -> bytes:
    writer = BufferWriter()
    writer.write_str(message.name)
    writer.write_u32(message.account_number)
    writer.write_str(message.password)
    return writer.to_bytes()

def decode_close_account_request(payload: bytes) -> CloseAccountRequest:
    reader = BufferReader(payload)
    return CloseAccountRequest(
        name=reader.read_str(),
        account_number=reader.read_u32(),
        password=reader.read_str(),
    )

def encode_deposit_withdraw_request(message: DepositWithdrawRequest) -> bytes:
    writer = BufferWriter()
    writer.write_str(message.name)
    writer.write_u32(message.account_number)
    writer.write_str(message.password)
    writer.write_u8(message.currency.value)
    writer.write_f64(message.amount)
    return writer.to_bytes()

def decode_deposit_withdraw_request(payload: bytes) -> DepositWithdrawRequest:
    reader = BufferReader(payload)
    return DepositWithdrawRequest(
        name=reader.read_str(),
        account_number=reader.read_u32(),
        password=reader.read_str(),
        currency=Currency(reader.read_u8()),
        amount=reader.read_f64(),
    )

def encode_monitor_request(message: MonitorRequest) -> bytes:
    writer = BufferWriter()
    writer.write_u32(message.duration_seconds)
    return writer.to_bytes()

def decode_monitor_request(payload: bytes) -> MonitorRequest:
    reader = BufferReader(payload)
    return MonitorRequest(
        duration_seconds=reader.read_u32(),
    )


def encode_standard_response(message: StandardResponse) -> bytes:
    writer = BufferWriter()
    writer.write_u8(message.status.value)
    writer.write_str(message.message)
    return writer.to_bytes()

def decode_standard_response(payload: bytes) -> StandardResponse:
    reader = BufferReader(payload)
    return StandardResponse(
        status=StatusCode(reader.read_u8()),
        message=reader.read_str(),
    )

def encode_open_account_response(message: OpenAccountResponse) -> bytes:
    writer = BufferWriter()
    writer.write_u8(message.status.value)
    writer.write_str(message.message)
    writer.write_u32(message.account_number if message.account_number is not None else 0)
    return writer.to_bytes()

def decode_open_account_response(payload: bytes) -> OpenAccountResponse:
    reader = BufferReader(payload)
    return OpenAccountResponse(
        status=StatusCode(reader.read_u8()),
        message=reader.read_str(),
        account_number=reader.read_u32(),
    )

def encode_balance_response(message: BalanceResponse) -> bytes:
    writer = BufferWriter()
    writer.write_u8(message.status.value)
    writer.write_str(message.message)
    writer.write_u32(message.account_number if message.account_number is not None else 0)
    writer.write_f64(message.balance if message.balance is not None else 0.0)
    writer.write_u8(message.currency.value if message.currency is not None else 0)
    return writer.to_bytes()

def decode_balance_response(payload: bytes) -> BalanceResponse:
    reader = BufferReader(payload)
    status = StatusCode(reader.read_u8())
    message = reader.read_str()
    account_number = reader.read_u32()
    balance = reader.read_f64()
    currency_raw = reader.read_u8()

    currency = None if currency_raw == 0 else Currency(currency_raw)

    return BalanceResponse(
        status=status,
        message=message,
        account_number=account_number,
        balance=balance,
        currency=currency,
    )

def encode_callback_update(message: CallbackUpdate) -> bytes:
    writer = BufferWriter()
    writer.write_str(message.event_name)
    writer.write_u32(message.account_number)
    writer.write_str(message.owner_name)
    writer.write_u8(message.currency.value)
    writer.write_f64(message.balance)
    writer.write_str(message.note)
    return writer.to_bytes()

def decode_callback_update(payload: bytes) -> CallbackUpdate:
    reader = BufferReader(payload)
    return CallbackUpdate(
        event_name=reader.read_str(),
        account_number=reader.read_u32(),
        owner_name=reader.read_str(),
        currency=Currency(reader.read_u8()),
        balance=reader.read_f64(),
        note=reader.read_str(),
    )