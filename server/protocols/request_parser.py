"""
decode the payload into the correct request object
"""
from __future__ import annotations

from models.enums import OpCode
from protocols.codecs import (
    decode_close_account_request,
    decode_deposit_withdraw_request,
    decode_monitor_request,
    decode_open_account_request,
)

def parse_request(opcode: OpCode, payload: bytes):
    if opcode == OpCode.OPEN_ACCOUNT:
        return decode_open_account_request(payload)

    if opcode == OpCode.CLOSE_ACCOUNT:
        return decode_close_account_request(payload)

    if opcode == OpCode.DEPOSIT:
        return decode_deposit_withdraw_request(payload)

    if opcode == OpCode.WITHDRAW:
        return decode_deposit_withdraw_request(payload)

    if opcode == OpCode.MONITOR_REGISTER:
        return decode_monitor_request(payload)

    raise ValueError(f"Unsupported opcode for request parsing: {opcode}")