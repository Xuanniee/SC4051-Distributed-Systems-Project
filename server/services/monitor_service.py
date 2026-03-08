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

import threading
import time
from typing import Tuple

from storage.monitor_store import MonitorStore


class MonitorService:
    """
    Manages monitor client registration and expiry cleanup.
    """

    def __init__(self, monitor_store: MonitorStore, cleanup_interval_seconds: int = 5) -> None:
        self.monitor_store = monitor_store
        self.cleanup_interval_seconds = cleanup_interval_seconds

        self._cleanup_thread = None
        self._stop_event = threading.Event()

    def register_monitor(self, client_address: Tuple[str, int], duration_seconds: int) -> None:
        if duration_seconds <= 0:
            raise ValueError("Monitor duration must be greater than 0")

        client_ip, client_port = client_address
        self.monitor_store.add_registration(client_ip, client_port, duration_seconds)

    def get_active_monitors(self):
        return self.monitor_store.get_active_registrations()

    def cleanup_expired_monitors(self) -> None:
        self.monitor_store.remove_expired_registrations()

    def start_background_cleanup_if_needed(self) -> None:
        if self._cleanup_thread is not None and self._cleanup_thread.is_alive():
            return

        self._stop_event.clear()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
        )
        self._cleanup_thread.start()

    def stop_background_cleanup_if_needed(self) -> None:
        self._stop_event.set()

        if self._cleanup_thread is not None:
            self._cleanup_thread.join(timeout=1.0)

    def _cleanup_loop(self) -> None:
        while not self._stop_event.is_set():
            self.cleanup_expired_monitors()
            time.sleep(self.cleanup_interval_seconds)