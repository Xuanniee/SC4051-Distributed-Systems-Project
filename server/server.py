from __future__ import annotations
import argparse
import random
import socket

from handlers.dispatcher import Dispatcher
from handlers.banking_handlers import BankingHandlers
from models.enums import OpCode, StatusCode
from models.messages import StandardResponse
from protocols.codecs import encode_standard_response
from protocols.invocation_codecs import decode_invocation_header
from services.bank_services import BankService
from services.invocation_service import AtMostOnceService
from services.monitor_service import MonitorService
from config.config import HOST, PORT, BUFFER_SIZE


def build_error_response(message: str) -> bytes:
    return encode_standard_response(
        StandardResponse(
            status=StatusCode.ERROR,
            message=message,
        )
    )

def parse_args():
    """
    Function to allow user to change invokation semantics and vary data loss
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--semantics",
        choices=["at-least-once", "at-most-once"],
        default="at-most-once",
    )
    parser.add_argument(
        "--drop-reply-rate",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--drop-request-rate",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.0,
    )
    return parser.parse_args()

def should_drop_reply(drop_reply_rate: float) -> bool:
    """
    Random function to decide if we should drop a request to simulate data loss
    """
    if drop_reply_rate <= 0.0:
        return False
    return random.random() < drop_reply_rate

def should_drop_request(drop_request_rate: float) -> bool:
    """
    Random function to decide if we should drop a request to simulate data loss
    """
    if drop_request_rate <= 0.0:
        return False
    return random.random() < drop_request_rate

def main() -> None:
    args = parse_args()

    # Create a UDP socket to listen to
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"Bank server listening on {HOST}:{PORT}")

    # Create the services and handlers for all functionalities
    monitor_service = MonitorService(server_socket)
    bank_service = BankService(monitor_service=monitor_service)
    banking_handlers = BankingHandlers(bank_service, monitor_service)
    dispatcher = Dispatcher(banking_handlers)
    
	# Create the Invokation Semantic Services here
    at_most_once_service = AtMostOnceService()

    # While server is listening
    while True:
        try:
            # Extract the data payload and client IP
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            if should_drop_request(args.drop_request_rate):
                continue

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
                # Retrieve the request meta nad body
                request_meta, request_body = decode_invocation_header(payload)

                if args.semantics == "at-most-once":
                    # Cannot redo request, so return stored reply
                    if at_most_once_service.has_reply(
                        request_meta.client_id,
                        request_meta.request_id,
                    ):
                        # Retrun stored reply
                        response_bytes = at_most_once_service.get_reply(
                            request_meta.client_id,
                            request_meta.request_id,
                        )
                    else:
                        # Perform request since new and store
                        response_bytes = dispatcher.dispatch(
                            opcode,
                            request_body,
                            client_address,
                            request_meta,
                        )
                        at_most_once_service.store_reply(
                            request_meta.client_id,
                            request_meta.request_id,
                            response_bytes,
                        )
                else:
                    response_bytes = dispatcher.dispatch(
                        opcode,
                        request_body,
                        client_address,
                        request_meta,
                    )
            except Exception as exc:
                response_bytes = build_error_response(f"Dispatch error: {exc}")

			# Randomly drop data replies to simulate loss
            if should_drop_reply(args.drop_reply_rate):
                continue

            # After getting responses, return to client
            time.sleep(args.timeout)
            server_socket.sendto(response_bytes, client_address)

        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
        except Exception as exc:
            print(f"Server loop error: {exc}")

    server_socket.close()


if __name__ == "__main__":
    main()