"""
Implements request handlers for banking-related operations.

This file should approximately contain:
	•	one handler per request type
	•	decode request payload
	•	call the relevant service method
	•	convert result into response object
	•	encode response object into payload bytes
"""
from __future__ import annotations
from typing import Tuple

from models.enums import OpCode, StatusCode
from models.messages import StandardResponse
from protocols.codecs import encode_standard_response
from protocols.request_parser import parse_request


class BankingHandlers:
    """
    Decodes requests, calls service logic, and returns encoded responses.
    """

    def __init__(self, bank_service, monitor_service) -> None:
        self.bank_service = bank_service
        self.monitor_service = monitor_service

    def handle_close_account(self, payload: bytes, client_address: Tuple[str, int]) -> bytes:
        try:
            request = parse_request(OpCode.CLOSE_ACCOUNT, payload)

            response = self.bank_service.close_account(
                name=request.name,
                account_number=request.account_number,
                password=request.password,
            )

            return encode_standard_response(response)

        except Exception as exc:
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Close account handler error: {exc}",
                )
            )

    def handle_monitor(self, payload: bytes, client_address: Tuple[str, int]) -> bytes:
        try:
            request = parse_request(OpCode.MONITOR, payload)

            self.monitor_service.register_monitor(
                client_address=client_address,
                duration_seconds=request.duration_seconds,
            )

            response = StandardResponse(
                status=StatusCode.OK,
                message=f"Monitoring registered for {request.duration_seconds} seconds",
            )

            return encode_standard_response(response)

        except Exception as exc:
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Monitor handler error: {exc}",
                )
            )