"""
Handles outgoing callback notifications to monitor clients.

This file should approximately contain:
	•	function to build callback update payloads
	•	function to send updates to all active monitor clients
	•	integration with UDP socket wrapper
	•	optional logic to skip expired clients before sending
"""
from __future__ import annotations

from models.accounts import Account
from models.messages import CallbackUpdate
# from protocol.codecs import encode_callback_update
from services.monitor_service import MonitorService


class CallbackService:
    """
    Sends callback updates to active monitoring clients.
    """

    def __init__(self, monitor_service: MonitorService, udp_socket_wrapper) -> None:
        self.monitor_service = monitor_service
        self.udp_socket_wrapper = udp_socket_wrapper

    def notify_account_closed(self, account: Account) -> None:
        update = CallbackUpdate(
            event_name="ACCOUNT_CLOSED",
            account_number=account.account_number,
            owner_name=account.owner_name,
            currency=account.currency,
            balance=account.balance,
            note="Account was closed",
        )
        self._broadcast_update(update)

    def _broadcast_update(self, update: CallbackUpdate) -> None:
        payload = encode_callback_update(update)

        for registration in self.monitor_service.get_active_monitors():
            self.udp_socket_wrapper.sendto(
                payload,
                (registration.client_ip, registration.client_port),
            )