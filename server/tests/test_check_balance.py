"""
Integration-style test for the `check_balance` functionality.

This script:
- Opens an account
- Sends several BALANCE_INQUIRY requests (valid and invalid)
- Prints the server responses for manual verification
"""

from __future__ import annotations

import socket

from config.config import SERVER_ADDR, CLIENT_BUFFER_SIZE
from models.enums import Currency, OpCode
from models.messages import OpenAccountRequest, BalanceInquiryRequest
from protocols.codecs import (
    decode_balance_response,
    decode_open_account_response,
    decode_standard_response,
    encode_balance_inquiry_request,
    encode_open_account_request,
)
from protocols.invocation_codecs import encode_invocation_header


def build_packet(opcode: OpCode, client_id: str, request_id: int, body: bytes) -> bytes:
    """
    Build a request packet in the format:
    [1-byte opcode][invocation header][encoded body]
    """
    header = encode_invocation_header(client_id, request_id)
    return bytes([opcode.value]) + header + body


def open_account(
    client_socket: socket.socket,
    client_id: str,
    request_id: int,
    name: str,
    password: str,
    currency: Currency,
    initial_balance: float,
) -> int:
    """
    Open an account and return the assigned account number.
    """
    request = OpenAccountRequest(
        name=name,
        password=password,
        currency=currency,
        initial_balance=initial_balance,
    )

    payload = encode_open_account_request(request)
    packet = build_packet(OpCode.OPEN_ACCOUNT, client_id, request_id, payload)
    client_socket.sendto(packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        response = decode_open_account_response(data)
        print("Open account response:", response)
    except Exception:
        err = decode_standard_response(data)
        raise RuntimeError(f"Failed to open account: {err}") from None

    if response.account_number is None:
        raise RuntimeError("Server did not return an account number")

    return response.account_number


def run_balance_inquiry_tests() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_id = "check-balance-client"
    request_id = 1

    try:
        # 1. Create a test account
        account_number = open_account(
            client_socket=client_socket,
            client_id=client_id,
            request_id=request_id,
            name="Alice",
            password="pass1234",
            currency=Currency.SGD,
            initial_balance=500.0,
        )
        request_id += 1

        # 2. Prepare a series of balance inquiry test cases
        test_cases = [
            (
                "valid balance inquiry",
                BalanceInquiryRequest(
                    name="Alice",
                    account_number=account_number,
                    password="pass1234",
                ),
            ),
            (
                "non-existent account",
                BalanceInquiryRequest(
                    name="Alice",
                    account_number=account_number + 9999,
                    password="pass1234",
                ),
            ),
            (
                "wrong account holder name",
                BalanceInquiryRequest(
                    name="Mallory",
                    account_number=account_number,
                    password="pass1234",
                ),
            ),
            (
                "wrong password",
                BalanceInquiryRequest(
                    name="Alice",
                    account_number=account_number,
                    password="wrongpass",
                ),
            ),
        ]

        for case_name, request in test_cases:
            payload = encode_balance_inquiry_request(request)
            packet = build_packet(OpCode.BALANCE_INQUIRY, client_id, request_id, payload)
            client_socket.sendto(packet, SERVER_ADDR)
            data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

            print(f"\nBalance inquiry case [{case_name}]:")
            try:
                response = decode_balance_response(data)
                print(response)
            except Exception:
                err = decode_standard_response(data)
                print("StandardResponse:", err)

            request_id += 1

        print("\nExpected behavior:")
        print("- 'valid balance inquiry' should return SUCCESS with balance 500.0 SGD")
        print("- 'non-existent account' should return an ERROR 'Account not found'")
        print("- 'wrong account holder name' should return an ERROR 'Account name does not match'")
        print("- 'wrong password' should return an ERROR 'Invalid password'")

    finally:
        client_socket.close()


def main() -> None:
    run_balance_inquiry_tests()


if __name__ == "__main__":
    main()

