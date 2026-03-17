from __future__ import annotations

from models.enums import OpCode
from models.messages import RequestMeta

class Dispatcher:
    """
    Routes incoming requests to the correct handler.
    """
    def __init__(self, banking_handlers, semantics_engine=None) -> None:
        """
        Constructor for the Dispatcher
        """
        self.banking_handlers = banking_handlers
        self.semantics_engine = semantics_engine
    
    def dispatch(self, opcode: OpCode, payload: bytes, client_address, request_meta: RequestMeta):
        """
        Call the correct banking handler to handle different requests
        """
        if opcode == OpCode.CLOSE_ACCOUNT:
            return self.banking_handlers.handle_close_account(payload, client_address, request_meta)

        if opcode == OpCode.MONITOR_REGISTER:
            return self.banking_handlers.handle_monitor(payload, client_address, request_meta)

        if opcode == OpCode.OPEN_ACCOUNT:
            return self.banking_handlers.handle_open_account(payload, client_address, request_meta)

        if opcode == OpCode.DEPOSIT:
            return self.banking_handlers.handle_deposit(payload, client_address, request_meta)

        if opcode == OpCode.WITHDRAW:
            return self.banking_handlers.handle_withdraw(payload, client_address, request_meta)

        if opcode == OpCode.TRANSFER:
            return self.banking_handlers.handle_transfer(payload, client_address, request_meta)

        raise ValueError(f"Unsupported opcode: {opcode}")