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

# Python Server Details to Reach it
SERVER_ADDR = ("127.0.0.1", 2222)
BUFFER_SIZE = 4096

def main() -> None:
    # Create a socket to start listening to
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to a fixed local port so you know where callbacks return
    client_socket.bind(("127.0.0.1", 9001))
    
    # Send a monitor Request to the Backend server to monitor for 5 mins
    request = MonitorRequest(duration_seconds=300)
    payload = bytes([OpCode.MONITOR_REGISTER.value]) + encode_monitor_request(request)

    # Send the request
    client_socket.sendto(payload, SERVER_ADDR)

    # Receive the monitor request registratin response first
    data, addr = client_socket.recvfrom(BUFFER_SIZE)
    response = decode_standard_response(data)
    print("Monitor registration response:", response)

    # Wait for all callback updates to be streamed
    print("Waiting for callback updates...\n")
    while True:
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        update = decode_callback_update(data)
        print("Received callback from server:")
        print(update)
        print()

if __name__ == "__main__":
    main()