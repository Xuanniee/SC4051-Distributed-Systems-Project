"""
This test ensures that the at least once invocation is working on the server side with a simple non-idempotent
withdraw request and transfer request.
"""
from __future__ import annotations
import socket

from models.enums import Currency, OpCode
from models.messages import DepositWithdrawRequest, OpenAccountRequest, TransferRequest
from protocols.codecs import (
    decode_balance_response,
    decode_open_account_response,
    decode_standard_response,
    encode_deposit_withdraw_request,
    encode_open_account_request,
    encode_transfer_request,
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

    # 1. Send an Acc creation request to the server
    open_req = OpenAccountRequest(
        name="Sephiroth",
        password="password",
        currency=Currency.SGD,
        initial_balance=1000.0,
    )

    open_body = encode_open_account_request(open_req)
    open_packet = build_packet(OpCode.OPEN_ACCOUNT, client_id, 1, open_body)
    client_socket.sendto(open_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        open_res = decode_open_account_response(data)
        print("Open response:", open_res)
    except Exception:
        print("Open response decoding failed")
        return
    
    account_number1 = open_res.account_number

    open_req = OpenAccountRequest(
        name="Cloud",
        password="password",
        currency=Currency.SGD,
        initial_balance=500.0,
    )

    open_body = encode_open_account_request(open_req)
    open_packet = build_packet(OpCode.OPEN_ACCOUNT, client_id, 2, open_body)
    client_socket.sendto(open_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        open_res = decode_open_account_response(data)
        print("Open response:", open_res)
    except Exception:
        print("Open response decoding failed")
        return

    account_number2 = open_res.account_number

    # 2. Withdraw once (Should be applied)
    withdraw_req = DepositWithdrawRequest(
        name="Sephiroth",
        account_number=account_number1,
        password="password",
        currency=Currency.SGD,
        amount=100.0,
    )
    withdraw_body = encode_deposit_withdraw_request(withdraw_req)
    withdraw_packet = build_packet(OpCode.WITHDRAW, client_id, 1, withdraw_body)
    client_socket.sendto(withdraw_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        withdraw_res = decode_balance_response(data)
        print("First withdraw response:", withdraw_res)
    except Exception:
        print("First withdraw failed:", decode_standard_response(data))
        return
    
    # 3. Withdraw again (Should be duplicated)
    withdraw_req = DepositWithdrawRequest(
        name="Sephiroth",
        account_number=account_number1,
        password="password",
        currency=Currency.SGD,
        amount=100.0,
    )
    withdraw_body = encode_deposit_withdraw_request(withdraw_req)
    withdraw_packet = build_packet(OpCode.WITHDRAW, client_id, 1, withdraw_body)
    client_socket.sendto(withdraw_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)

    try:
        withdraw_res = decode_balance_response(data)
        print("Second withdraw response:", withdraw_res)
    except Exception:
        print("Second withdraw failed:", decode_standard_response(data))
        return
    
    # Transfer from account 1 to account 2
    transfer_req = TransferRequest( 
        from_name="Sephiroth",
        from_account_number=account_number1,
        to_account_number=account_number2,
        password="password",
        currency=Currency.SGD,
        amount=100.0,
    )
    transfer_body = encode_transfer_request(transfer_req)
    transfer_packet = build_packet(OpCode.TRANSFER, client_id, 1, transfer_body)
    client_socket.sendto(transfer_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)
    try:
        transfer_res = decode_balance_response(data)
        print("Transfer response:", transfer_res)
    except Exception:
        print("Transfer failed:", decode_standard_response(data))
        return
    # 4. Transfer again (Should be duplicated)
    transfer_req = TransferRequest(
        from_name="Sephiroth",
        from_account_number=account_number1,
        to_account_number=account_number2,
        password="password",
        currency=Currency.SGD,
        amount=50.0,
    )
    transfer_body = encode_transfer_request(transfer_req)
    transfer_packet = build_packet(OpCode.TRANSFER, client_id, 1, transfer_body)
    client_socket.sendto(transfer_packet, SERVER_ADDR)
    data, _ = client_socket.recvfrom(CLIENT_BUFFER_SIZE)
    try:
        transfer_res = decode_balance_response(data)
        print("Transfer response:", transfer_res)
    except Exception:
        print("Transfer failed:", decode_standard_response(data))
        return

if __name__ == "__main__":
    main()  