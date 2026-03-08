"""
Stores monitor client registrations in memory.

This file should approximately contain:
	•	add monitor registration
	•	remove monitor registration
	•	retrieve active monitors
	•	remove expired monitors
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

from storage.db import get_db_cursor

@dataclass
class MonitorRegistration:
    client_ip: str
    client_port: int
    expires_at: datetime

class MonitorStore:
    """
    PostgreSQL-backed storage for monitoring registrations.
    """

    def add_registration(self, client_ip: str, client_port: int, duration_seconds: int) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)

        delete_existing_query = """
            DELETE FROM monitor_registrations
            WHERE client_ip = %s AND client_port = %s
        """

        insert_query = """
            INSERT INTO monitor_registrations (client_ip, client_port, expires_at)
            VALUES (%s, %s, %s)
        """

        with get_db_cursor(commit=True) as (_, cur):
            cur.execute(delete_existing_query, (client_ip, client_port))
            cur.execute(insert_query, (client_ip, client_port, expires_at))

    def get_active_registrations(self) -> List[MonitorRegistration]:
        query = """
            SELECT client_ip, client_port, expires_at
            FROM monitor_registrations
            WHERE expires_at > NOW()
            ORDER BY expires_at ASC
        """

        with get_db_cursor(commit=False) as (_, cur):
            cur.execute(query)
            rows = cur.fetchall()

        return [
            MonitorRegistration(
                client_ip=row[0],
                client_port=row[1],
                expires_at=row[2],
            )
            for row in rows
        ]

    def remove_expired_registrations(self) -> None:
        query = """
            DELETE FROM monitor_registrations
            WHERE expires_at <= NOW()
        """

        with get_db_cursor(commit=True) as (_, cur):
            cur.execute(query)