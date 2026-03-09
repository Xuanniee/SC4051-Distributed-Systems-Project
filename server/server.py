from __future__ import annotations
import socket

from handlers.dispatcher import Dispatcher
from handlers.banking_handlers import BankingHandlers
from models.enums import OpCode, StatusCode
from models.messages import StandardResponse
from protocols.codecs import encode_standard_response
from services.bank_services import BankService
from services.monitor_service import MonitorService
from config.config import HOST, PORT, BUFFER_SIZE

def build_error_response(message: str) -> bytes:
    return encode_standard_response(
        StandardResponse(
            status=StatusCode.ERROR,
            message=message,
        )
    )


def main() -> None:
    # Create a UDP socket to listen to
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"Bank server listening on {HOST}:{PORT}")

	# Create the services and handlers for all functionalities
    monitor_service = MonitorService(server_socket)
    bank_service = BankService(monitor_service=monitor_service)
    banking_handlers = BankingHandlers(bank_service, monitor_service)
    dispatcher = Dispatcher(banking_handlers)

	# While server is listening
    while True:
        try:
            # Extract the data payload and client IP
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            if not data:
                continue

            # First byte is opcode - Indicates what type of request is received
            raw_opcode = data[0]
            # Rest is Payload
            payload = data[1:]

			# Parse the Data Opcode, followed by trying to pass the request to the dispatcher to 
			# handle routing
            try:
                opcode = OpCode(raw_opcode)
            except ValueError:
                response = build_error_response(f"Invalid opcode: {raw_opcode}")
                server_socket.sendto(response, client_address)
                continue

            try:
                response_bytes = dispatcher.dispatch(opcode, payload, client_address)
            except Exception as exc:
                response_bytes = build_error_response(f"Dispatch error: {exc}")

			# After getting responses, return to client
            server_socket.sendto(response_bytes, client_address)

        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
        except Exception as exc:
            print(f"Server loop error: {exc}")

    server_socket.close()

if __name__ == "__main__":
    main()