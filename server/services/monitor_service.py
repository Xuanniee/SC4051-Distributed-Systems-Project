"""
Implements monitoring registration and lifecycle logic.

This file should approximately contain:
	•	register monitor client
	•	remove expired monitor clients
	•	retrieve active monitor clients
	•	validate monitoring interval
	•	cleanup helpers
"""
from __future__ import annotations

import socket
import time
from typing import List, Tuple

from models.messages import CallbackUpdate
from protocols.codecs import encode_callback_update


class MonitorService:
    """
    Keeps track of monitoring clients and sends callback updates to active clients.
    """
    def __init__(self, udp_socket: socket.socket) -> None:
        """
        Constructor for setting up a UDP socket and tracking the list of clients to send callback updates to
        """
        self.udp_socket = udp_socket
        self.monitors: List[dict] = []

    def register_monitor(self, client_address: Tuple[str, int], duration_seconds: int) -> None:
        """
        Registers a new client for callback updates for some period of time
        """
        if duration_seconds <= 0:
            raise ValueError("Monitor duration must be positive")

        # Calculate the expiry time
        expiry_time = time.time() + duration_seconds

        # Remove any existing clients
        self.monitors = [
            m for m in self.monitors
            if m["client_address"] != client_address
        ]

        # Always add the client new
        self.monitors.append(
            {
                "client_address": client_address,
                "expiry_time": expiry_time,
            }
        )

    def remove_expired_monitors(self) -> None:
        """
        De-registers clients whose monitoring periods have lapsed
        """
        now = time.time()

        # Remove expired clients
        self.monitors = [
            m for m in self.monitors
            if m["expiry_time"] > now
        ]

    def notify_update(self, update: CallbackUpdate) -> None:
        """
        Update every client that is active monitoring
        """
        # Remove any expired monitors so we don not errorneous udpate
        self.remove_expired_monitors()

        # Encode the banking acc details callabck
        payload = encode_callback_update(update)

        # Push the update
        for monitor in self.monitors:
            try:
                self.udp_socket.sendto(payload, monitor["client_address"])
            except Exception:
                # Ignore failed callback sends so normal banking flow is not blocked
                pass