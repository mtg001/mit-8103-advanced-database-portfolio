PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS branches (
    branch_id       TEXT PRIMARY KEY,
    branch_name     TEXT NOT NULL,
    city            TEXT NOT NULL,
    state            TEXT NOT NULL DEFAULT 'Lagos'
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT NOT NULL UNIQUE,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id      TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL REFERENCES customers(customer_id),
    branch_id       TEXT NOT NULL REFERENCES branches(branch_id),
    account_number  TEXT NOT NULL UNIQUE CHECK (length(account_number) = 10),
    account_type    TEXT NOT NULL CHECK (account_type IN ('SAVINGS','CURRENT')),
    currency        TEXT NOT NULL CHECK (currency = 'NGN'),
    balance_kobo    INTEGER NOT NULL DEFAULT 0 CHECK (balance_kobo >= 0),
    status          TEXT NOT NULL CHECK (status IN ('ACTIVE','FROZEN','CLOSED')),
    opened_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id       TEXT PRIMARY KEY,
    reference         TEXT NOT NULL UNIQUE,
    debit_account_id  TEXT NOT NULL REFERENCES accounts(account_id),
    credit_account_id TEXT NOT NULL REFERENCES accounts(account_id),
    amount_kobo       INTEGER NOT NULL CHECK (amount_kobo > 0),
    currency          TEXT NOT NULL CHECK (currency = 'NGN'),
    status            TEXT NOT NULL CHECK (status IN ('PENDING','COMPLETED','FAILED','REVERSED')),
    description       TEXT,
    initiated_at      TEXT NOT NULL,
    completed_at      TEXT,
    CHECK (debit_account_id <> credit_account_id)
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    entry_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    transfer_id    TEXT NOT NULL REFERENCES transfers(transfer_id),
    account_id     TEXT NOT NULL REFERENCES accounts(account_id),
    direction      TEXT NOT NULL CHECK (direction IN ('DEBIT','CREDIT')),
    amount_kobo    INTEGER NOT NULL CHECK (amount_kobo > 0),
    posted_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type    TEXT NOT NULL,
    entity_id      TEXT NOT NULL,
    action         TEXT NOT NULL,
    event_time     TEXT NOT NULL,
    details        TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_transfers_debit_time ON transfers(debit_account_id, initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_transfers_credit_time ON transfers(credit_account_id, initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ledger_transfer ON ledger_entries(transfer_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity_time ON audit_logs(entity_type, entity_id, event_time DESC);

CREATE TRIGGER IF NOT EXISTS trg_account_balance_audit
AFTER UPDATE OF balance_kobo ON accounts
WHEN OLD.balance_kobo <> NEW.balance_kobo
BEGIN
    INSERT INTO audit_logs(entity_type, entity_id, action, event_time, details)
    VALUES ('ACCOUNT', NEW.account_id, 'BALANCE_UPDATED', CURRENT_TIMESTAMP,
            'Previous balance_kobo=' || OLD.balance_kobo || '; new balance_kobo=' || NEW.balance_kobo);
END;
