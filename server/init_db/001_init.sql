CREATE TABLE IF NOT EXISTS accounts (
    account_number BIGINT PRIMARY KEY,
    owner_name TEXT NOT NULL,
    password TEXT NOT NULL,
    currency TEXT NOT NULL,
    balance DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS monitor_registrations (
    id BIGSERIAL PRIMARY KEY,
    client_ip TEXT NOT NULL,
    client_port INTEGER NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS request_history (
    request_id TEXT PRIMARY KEY,
    reply_payload BYTEA,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);