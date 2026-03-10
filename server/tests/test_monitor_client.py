"""
Test to be used with Action Client.

This test behaves as a second client monitoring the backend server for all the requests
"""
from __future__ import annotations
import socket

from models.enums import OpCode
from models.messages import MonitorRequest
from protocols.codecs import (
    decode_callback_update,
    decode_standard_response,
    encode_monitor_request,
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
    # Create a socket to start listening to
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to a fixed local port so you know where callbacks return
    client_socket.bind(("127.0.0.1", 9001))
    
    # Send a monitor Request to the Backend server to monitor for 5 mins
    request = MonitorRequest(duration_seconds=10)
    client_id = "monitor-client"
    request_id = 1
    header = encode_invocation_header(client_id, request_id)
    payload = bytes([OpCode.MONITOR_REGISTER.value]) + header + encode_monitor_request(request)

    # Send the request
    client_socket.sendto(payload, SERVER_ADDR)

    # Receive the monitor request registratin response first
    data, addr = client_socket.recvfrom(CLIENT_BUFFER_SIZE)
    response = decode_standard_response(data)
    print("Monitor registration response:", response)

    # Wait for all callback updates to be streamed
    print("Waiting for callback updates...\n")
    while True:
        data, addr = client_socket.recvfrom(CLIENT_BUFFER_SIZE)
        update = decode_callback_update(data)
        print("Received callback from server:")
        print(update)
        print()

if __name__ == "__main__":
    main()