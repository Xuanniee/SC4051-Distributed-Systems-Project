from __future__ import annotations

from models.enums import Currency, StatusCode
from models.messages import (
    CallbackUpdate,
    CloseAccountRequest,
    MonitorRequest,
    StandardResponse,
)
from protocols.marshaller import BufferReader, BufferWriter


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

    writer.write_u8(int(message.status))
    writer.write_str(message.message)

    writer.write_u8(1 if message.balance is not None else 0)
    if message.balance is not None:
        writer.write_f64(message.balance)

    writer.write_u8(1 if message.account_number is not None else 0)
    if message.account_number is not None:
        writer.write_u32(message.account_number)

    return writer.to_bytes()


def decode_standard_response(payload: bytes) -> StandardResponse:
    reader = BufferReader(payload)

    status = StatusCode(reader.read_u8())
    message = reader.read_str()

    has_balance = reader.read_u8()
    balance = reader.read_f64() if has_balance else None

    has_account_number = reader.read_u8()
    account_number = reader.read_u32() if has_account_number else None

    return StandardResponse(
        status=status,
        message=message,
        balance=balance,
        account_number=account_number,
    )


def encode_callback_update(message: CallbackUpdate) -> bytes:
    writer = BufferWriter()

    writer.write_str(message.event_name)
    writer.write_u32(message.account_number)
    writer.write_str(message.owner_name)
    writer.write_u8(int(message.currency))
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