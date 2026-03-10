from __future__ import annotations
from typing import Dict, Tuple


class AtMostOnceService:
    """
    Maintains reply history for at most once invocation
    """
    def __init__(self, max_history_size: int = 10000) -> None:
        """
        Constructor to initialise dictionary to store reply history
        """
        self.reply_history: Dict[Tuple[str, int], bytes] = {}
        self.max_history_size = max_history_size

    def _make_key(self, client_id: str, request_id: int) -> Tuple[str, int]:
        """
        Create a unique key for each request from a client
        """
        return (client_id, request_id)

    def has_reply(self, client_id: str, request_id: int) -> bool:
        """
        Check if we already replied the client before.
        """
        key = self._make_key(client_id, request_id)
        return key in self.reply_history

    def get_reply(self, client_id: str, request_id: int) -> bytes:
        """
        Retrieve the stored response to resend client
        """
        key = self._make_key(client_id, request_id)
        return self.reply_history[key]

    def store_reply(self, client_id: str, request_id: int, reply_bytes: bytes) -> None:
        """
        Store a response that we returned to the client
        """
        if len(self.reply_history) >= self.max_history_size:
            oldest_key = next(iter(self.reply_history))
            del self.reply_history[oldest_key]

        key = self._make_key(client_id, request_id)
        self.reply_history[key] = reply_bytes