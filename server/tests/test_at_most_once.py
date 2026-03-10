"""
This test ensures that the at most once invokation is working on the server side with a simple non-idempotent
deposit request.

Client will be the one sending the request id and client id. Server will not assign these values but simply
judge from provided values if it has seen request before
"""
from __future__ import annotations
import socket

from models.enums import Currency, OpCode
from models.messages import DepositWithdrawRequest, OpenAccountRequest
from protocols.codecs import (
    decode_balance_response,
    decode_open_account_response,
    decode_standard_response,
    encode_deposit_withdraw_request,
    encode_open_account_request,
)
from protocols.invocation_codecs import encode_invocation_header
from config.config import SERVER_ADDR, CLIENT_BUFFER_SIZE


def build_packet(opcode: OpCode, client_id: str, request_id: int, body: bytes) -> bytes:
    """
    Encode the request header so server can identify if client request is a duplicate
    """
    header = encode_invocation_header(client_id, request_id)
    return bytes([opcode.value]) + header + body


def main() -> None:
    # Create a UDP socket on the client device
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_id = "clientA"

    # 1. Open account with backend server
    open_req = OpenAccountRequest(
        name="Cloud",
        password="12345678",
        currency=Currency.SGD,
        initial_balance=1000.0,
    )
    # Every request need to be wrapped with client id and request id now b4 sending
    open_body = encode_open_account_request(open_req)
    open_packet = build_packet(OpCode.OPEN_ACCOUNT, client_id, 1, open_body)
    client_socket.sendto(open_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        open_res = decode_open_account_response(data)
        print("Open response:", open_res)
    except Exception:
        print("Open failed:", decode_standard_response(data))
        return

    account_number = open_res.account_number

    # 2. Deposit once (Should not be duplicated)
    deposit_req = DepositWithdrawRequest(
        name="Cloud",
        account_number=account_number,
        password="12345678",
        currency=Currency.SGD,
        amount=200.0,
    )
    deposit_body = encode_deposit_withdraw_request(deposit_req)

    # Send the request a duplicate number of times
    duplicate_request_id = 42
    packet1 = build_packet(OpCode.DEPOSIT, client_id, duplicate_request_id, deposit_body)
    packet2 = build_packet(OpCode.DEPOSIT, client_id, duplicate_request_id, deposit_body)

    client_socket.sendto(packet1, SERVER_ADDR)
    data1, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        deposit_res_1 = decode_balance_response(data1)
        print("First deposit response:", deposit_res_1)
    except Exception:
        print("First deposit failed:", decode_standard_response(data1))
        return

    client_socket.sendto(packet2, SERVER_ADDR)
    data2, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        deposit_res_2 = decode_balance_response(data2)
        print("Second deposit response:", deposit_res_2)
    except Exception:
        print("Second deposit failed:", decode_standard_response(data2))
        return

    print()
    print("Expected at-most-once behavior:")
    print("- first balance should be 1200.0")
    print("- second balance should still be 1200.0")
    print("- not 1400.0")

    client_socket.close()


if __name__ == "__main__":
    main()