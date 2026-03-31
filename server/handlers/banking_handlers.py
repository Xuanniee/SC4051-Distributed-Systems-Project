"""
This file contains the necessary files to translate raw bytes into requests so that the correct functions can be called
"""
from __future__ import annotations
from typing import Tuple

from models.enums import OpCode, StatusCode
from models.messages import BalanceResponse, OpenAccountResponse, RequestMeta, StandardResponse
from protocols.codecs import (
    encode_balance_response,
    encode_open_account_response,
    encode_standard_response,
    decode_transfer_request,
)
from protocols.request_parser import parse_request

class BankingHandlers:
    def __init__(self, bank_service, monitor_service) -> None:
        """
        Initialise a handler to banking and monitor services
        RequestMeta is used in server.py to filter accordingly, but we will pass it here for future uses
        """
        self.bank_service = bank_service
        self.monitor_service = monitor_service
        
    def handle_open_account(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.OPEN_ACCOUNT, payload)
            response = self.bank_service.open_account(request)

            if isinstance(response, OpenAccountResponse):
                print(f"OpenAcc Res: ", response)
                return encode_open_account_response(response)
            
            print(f"OpenAcc Res: ", response)
            return encode_standard_response(response)

        except Exception as exc:
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Open account handler error: {exc}",
                )
            )

    def handle_close_account(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.CLOSE_ACCOUNT, payload)
            response = self.bank_service.close_account(request)
            print(f"CloseAcc Res: ", response)
            return encode_standard_response(response)

        except Exception as exc:
            print(f"CloseAcc Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Close account handler error: {exc}",
                )
            )

    def handle_monitor(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.MONITOR_REGISTER, payload)

            self.monitor_service.register_monitor(
                client_address=client_address,
                duration_seconds=request.duration_seconds,
            )

            response = StandardResponse(
                status=StatusCode.SUCCESS,
                message=f"Monitoring registered for {request.duration_seconds} seconds",
            )

            print(f"Monitor Res: ", response)
            return encode_standard_response(response)

        except Exception as exc:
            print(f"Monitor Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Monitor handler error: {exc}",
                )
            )

    def handle_withdraw(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.WITHDRAW, payload)
            response = self.bank_service.withdraw(request)

            if isinstance(response, BalanceResponse):
                print(f"Withdraw Res: ", response)
                return encode_balance_response(response)

            print(f"Withdraw Res: ", response)
            return encode_standard_response(response)

        except Exception as exc:
            print(f"Withdraw Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Withdraw handler error: {exc}",
                )
            )

    def handle_deposit(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.DEPOSIT, payload)
            response = self.bank_service.deposit(request)

            if isinstance(response, BalanceResponse):
                print(f"Deposit Res: ", response)
                return encode_balance_response(response)

            print(f"Deposit Res: ", response)
            return encode_standard_response(response)

        except Exception as exc:
            print(f"Deposit Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Deposit handler error: {exc}",
                )
            )
        
    def handle_balance_inquiry(
        self,
        payload: bytes,
        client_address: Tuple[str, int],
        request_meta: RequestMeta,
    ) -> bytes:
        try:
            request = parse_request(OpCode.BALANCE_INQUIRY, payload)
            response = self.bank_service.check_balance(request)
            if isinstance(response, BalanceResponse):
                print(f"Balance Res: ", response)
                return encode_balance_response(response)

            print(f"Deposit Res: ", response)
            return encode_standard_response(response)
        except Exception as exc:
            print(f"Deposit Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Balance inquiry handler error: {exc}",
                )
            )
    
    # Handler for transfer requests
    def handle_transfer(self, payload: bytes, client_address, request_meta=None) -> bytes:
        try:
            # After decoding, execute the transfer request
            request = decode_transfer_request(payload)
            response = self.bank_service.transfer(request)

            # Transfer will return a check balance functionality
            if isinstance(response, BalanceResponse):
                print(f"Transfer Res: ", response)
                return encode_balance_response(response)

            print(f"Transfer Res: ", response)
            return encode_standard_response(response)
        
        except Exception as exc:
            print(f"Transfer Res: ", response)
            return encode_standard_response(
                StandardResponse(
                    status=StatusCode.ERROR,
                    message=f"Transfer handler error: {exc}",
                )
            )