# Integration test client for transfer functionality.

# This test sends real UDP requests to the backend server.
# It creates accounts first, then sends multiple invalid transfer
# requests, followed by one valid transfer request.

from __future__ import annotations

import socket

from config.config import SERVER_ADDR, CLIENT_BUFFER_SIZE
from models.enums import OpCode, StatusCode, Currency
from models.messages import OpenAccountRequest, TransferRequest
from protocols.codecs import (
    decode_balance_response,
    decode_open_account_response,
    decode_standard_response,
    encode_open_account_request,
    encode_transfer_request,
)
from protocols.invocation_codecs import encode_invocation_header


def build_packet(opcode: OpCode, client_id: str, request_id: int, body: bytes) -> bytes:
    """
    Build a request packet in the format:
    [1-byte opcode][invocation header][encoded body]
    """
    header = encode_invocation_header(client_id, request_id)
    return bytes([opcode.value]) + header + body


def send_request(
    client_socket: socket.socket,
    opcode: OpCode,
    client_id: str,
    request_id: int,
    body: bytes,
) -> bytes:
    """
    Send one UDP request to the server and return the raw reply bytes.
    """
    payload = build_packet(opcode, client_id, request_id, body)
    client_socket.sendto(payload, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)
    return data


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

    raw_reply = send_request(
        client_socket=client_socket,
        opcode=OpCode.OPEN_ACCOUNT,
        client_id=client_id,
        request_id=request_id,
        body=encode_open_account_request(request),
    )

    response = decode_open_account_response(raw_reply)
    print(f"Open account response for {name}:", response)

    if response.status != StatusCode.SUCCESS:
        raise RuntimeError(f"Failed to open account for {name}: {response.message}")

    if response.account_number is None:
        raise RuntimeError(f"Server did not return an account number for {name}")

    return response.account_number


def send_bad_transfer_requests(
    client_socket: socket.socket,
    client_id: str,
    starting_request_id: int,
    sender_account_number: int,
    receiver_account_number: int,
    different_currency_account_number: int,
) -> int:
    """
    Send a sequence of invalid transfer requests and print the server responses.

    Returns the next request_id to use after all bad requests have been sent.
    """
    # Cannot find sender account, or receiver acc, or send to same account
    bad_requests = [
        (
            "sender account not found",
            TransferRequest(
                from_name="Alice",
                from_account_number=999999,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "receiver account not found",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=888888,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "same account",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=sender_account_number,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "zero amount",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=0.0,
            ),
        ),
        (
            "negative amount",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=-20.0,
            ),
        ),
        (
            "wrong sender name",
            TransferRequest(
                from_name="Mallory",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "wrong password",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="wrongpass",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "currency mismatch with receiver",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=different_currency_account_number,
                currency=Currency.SGD,
                amount=50.0,
            ),
        ),
        (
            "currency mismatch with request currency",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.USD,
                amount=50.0,
            ),
        ),
        (
            "insufficient funds",
            TransferRequest(
                from_name="Alice",
                from_account_number=sender_account_number,
                password="pass1234",
                to_account_number=receiver_account_number,
                currency=Currency.SGD,
                amount=99999.0,
            ),
        ),
    ]

    request_id = starting_request_id

    for case_name, request in bad_requests:
        raw_reply = send_request(
            client_socket=client_socket,
            opcode=OpCode.TRANSFER,
            client_id=client_id,
            request_id=request_id,
            body=encode_transfer_request(request),
        )

        response = decode_standard_response(raw_reply)
        print(f"Bad transfer case [{case_name}] ->", response)

        request_id += 1

    return request_id


def send_good_transfer_request(
    client_socket: socket.socket,
    client_id: str,
    request_id: int,
    sender_account_number: int,
    receiver_account_number: int,
) -> None:
    """
    Send one valid transfer request and print the success response.
    """
    request = TransferRequest(
        from_name="Alice",
        from_account_number=sender_account_number,
        password="pass1234",
        to_account_number=receiver_account_number,
        currency=Currency.SGD,
        amount=75.0,
    )

    raw_reply = send_request(
        client_socket=client_socket,
        opcode=OpCode.TRANSFER,
        client_id=client_id,
        request_id=request_id,
        body=encode_transfer_request(request),
    )

    response = decode_balance_response(raw_reply)
    print("Good transfer response:", response)


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("127.0.0.1", 9002))

    client_id = "transfer-test-client"
    request_id = 1

    try:
        # Create an account for sender
        sender_account_number = open_account(
            client_socket=client_socket,
            client_id=client_id,
            request_id=request_id,
            name="Alice",
            password="pass1234",
            currency=Currency.SGD,
            initial_balance=500.0,
        )
        request_id += 1

        # Create receiver account
        receiver_account_number = open_account(
            client_socket=client_socket,
            client_id=client_id,
            request_id=request_id,
            name="Bob",
            password="word5678",
            currency=Currency.SGD,
            initial_balance=120.0,
        )
        request_id += 1

        # Open account for different currency
        different_currency_account_number = open_account(
            client_socket=client_socket,
            client_id=client_id,
            request_id=request_id,
            name="Charlie",
            password="diff9999",
            currency=Currency.USD,
            initial_balance=300.0,
        )
        request_id += 1

        # Send a bad request
        request_id = send_bad_transfer_requests(
            client_socket=client_socket,
            client_id=client_id,
            starting_request_id=request_id,
            sender_account_number=sender_account_number,
            receiver_account_number=receiver_account_number,
            different_currency_account_number=different_currency_account_number,
        )

        # Send good request to make sure it works
        send_good_transfer_request(
            client_socket=client_socket,
            client_id=client_id,
            request_id=request_id,
            sender_account_number=sender_account_number,
            receiver_account_number=receiver_account_number,
        )

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()