"""
Test to be used with Monitor Client.

This test behaves as the first client making requsts to the backend server
"""
from __future__ import annotations
import socket
import time

from models.enums import Currency, OpCode
from models.messages import (
    CloseAccountRequest,
    DepositWithdrawRequest,
    OpenAccountRequest,
)
from protocols.codecs import (
    decode_balance_response,
    decode_standard_response,
    decode_open_account_response,
    encode_close_account_request,
    encode_deposit_withdraw_request,
    encode_open_account_request,
)

# Python Server Details to Reach it
SERVER_ADDR = ("127.0.0.1", 2222)
BUFFER_SIZE = 4096


def main() -> None:
    # Start listening on a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 1. Send an Acc creation requst to the server
    open_req = OpenAccountRequest(
        name="Sephiroth",
        password="password",
        currency=Currency.SGD,
        initial_balance=1000.0,
    )
    packet = bytes([OpCode.OPEN_ACCOUNT.value]) + encode_open_account_request(open_req)
    client_socket.sendto(packet, SERVER_ADDR)

    # Open Request might not always succeed 
    data, _ = client_socket.recvfrom(BUFFER_SIZE)
    try:
        open_res = decode_open_account_response(data)
        print("Open response:", open_res)
        print()
    except Exception:
        err = decode_standard_response(data)
        print("Open failed with StandardResponse:", err)
        print()
        return
    
    # Extract the account number and sleep for 5s
    account_number = open_res.account_number
    time.sleep(5)

    # 2. Deposit Money into the Account
    ## Create a deposit requst and send it
    deposit_req = DepositWithdrawRequest(
        name="Sephiroth",
        account_number=account_number,
        password="password",
        currency=Currency.SGD,
        amount=200.0,
    )
    packet = bytes([OpCode.DEPOSIT.value]) + encode_deposit_withdraw_request(deposit_req)
    client_socket.sendto(packet, SERVER_ADDR)

    # See response, there should be 1,200 in acc now
    data, _ = client_socket.recvfrom(BUFFER_SIZE)
    try:
        deposit_res = decode_balance_response(data)
        print("Deposit req response:", deposit_res)
        print()
    except Exception:
        err = decode_standard_response(data)
        print("Deposit failed with StandardResponse:", err)
        print()
        client_socket.close()
        return

    time.sleep(5)

    # 3. Withdraw: Make a withdraw req and send it
    withdraw_req = DepositWithdrawRequest(
        name="Sephiroth",
        account_number=account_number,
        password="password",
        currency=Currency.SGD,
        amount=150.0,
    )
    packet = bytes([OpCode.WITHDRAW.value]) + encode_deposit_withdraw_request(withdraw_req)
    client_socket.sendto(packet, SERVER_ADDR)

    # See response, there should be 1,050 in acc now
    data, _ = client_socket.recvfrom(BUFFER_SIZE)
    try:
        withdraw_res = decode_balance_response(data)
        print("Withdraw req response:", withdraw_res)
        print()
    except Exception:
        err = decode_standard_response(data)
        print("Withdraw failed with StandardResponse:", err)
        print()
        client_socket.close()
        return
    time.sleep(5)

    # 4. Close account after testing both wirhtdraw and deposit
    close_req = CloseAccountRequest(
        name="Sephiroth",
        account_number=account_number,
        password="password",
    )
    packet = bytes([OpCode.CLOSE_ACCOUNT.value]) + encode_close_account_request(close_req)
    client_socket.sendto(packet, SERVER_ADDR)

    # Ensure acc close
    data, _ = client_socket.recvfrom(BUFFER_SIZE)
    try:
        close_res = decode_standard_response(data)
        print("Close acc response:", close_res)
        print()
    except Exception as exc:
        print("Close response decode failed:", exc)
        print("Raw response bytes:", data)
        print()


    # Stop connecting as we are no longer making requets
    client_socket.close()

if __name__ == "__main__":
    main()