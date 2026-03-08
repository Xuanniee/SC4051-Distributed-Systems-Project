# app/storage/db.py

from __future__ import annotations

import os
from contextlib import contextmanager
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "bank_db"),
        user=os.getenv("DB_USER", "bank_user"),
        password=os.getenv("DB_PASSWORD", "bank_password"),
    )

@contextmanager
def get_db_cursor(commit: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield conn, cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()