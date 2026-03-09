from __future__ import annotations
from models.enums import OpCode

class Dispatcher:
    """
    Routes incoming requests to the correct handler.
    """

    def __init__(self, banking_handlers, semantics_engine=None) -> None:
        self.banking_handlers = banking_handlers
        self.semantics_engine = semantics_engine

    def dispatch(self, opcode: int, payload: bytes, client_address):
        if opcode == OpCode.CLOSE_ACCOUNT:
            return self.banking_handlers.handle_close_account(payload, client_address)

        if opcode == OpCode.MONITOR:
            return self.banking_handlers.handle_monitor(payload, client_address)

        raise ValueError(f"Unsupported opcode: {opcode}")