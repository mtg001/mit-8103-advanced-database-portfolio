-- PostgreSQL deployment equivalent (PostgreSQL 16+ syntax; validate against target server version).
CREATE TABLE branches (
    branch_id TEXT PRIMARY KEY,
    branch_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Lagos'
);
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    branch_id TEXT NOT NULL REFERENCES branches(branch_id),
    account_number CHAR(10) NOT NULL UNIQUE,
    account_type TEXT NOT NULL CHECK (account_type IN ('SAVINGS','CURRENT')),
    currency CHAR(3) NOT NULL CHECK (currency = 'NGN'),
    balance_kobo BIGINT NOT NULL DEFAULT 0 CHECK (balance_kobo >= 0),
    status TEXT NOT NULL CHECK (status IN ('ACTIVE','FROZEN','CLOSED')),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE transfers (
    transfer_id TEXT PRIMARY KEY,
    reference TEXT NOT NULL UNIQUE,
    debit_account_id TEXT NOT NULL REFERENCES accounts(account_id),
    credit_account_id TEXT NOT NULL REFERENCES accounts(account_id),
    amount_kobo BIGINT NOT NULL CHECK (amount_kobo > 0),
    currency CHAR(3) NOT NULL CHECK (currency = 'NGN'),
    status TEXT NOT NULL CHECK (status IN ('PENDING','COMPLETED','FAILED','REVERSED')),
    description TEXT,
    initiated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CHECK (debit_account_id <> credit_account_id)
);
CREATE TABLE ledger_entries (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transfer_id TEXT NOT NULL REFERENCES transfers(transfer_id),
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    direction TEXT NOT NULL CHECK (direction IN ('DEBIT','CREDIT')),
    amount_kobo BIGINT NOT NULL CHECK (amount_kobo > 0),
    posted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE audit_logs (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_transfers_debit_time ON transfers(debit_account_id, initiated_at DESC);
CREATE INDEX idx_transfers_credit_time ON transfers(credit_account_id, initiated_at DESC);
CREATE INDEX idx_ledger_transfer ON ledger_entries(transfer_id);
CREATE INDEX idx_ledger_account_posted ON ledger_entries(account_id, posted_at DESC) INCLUDE (direction, amount_kobo);
CREATE INDEX idx_audit_entity_time ON audit_logs(entity_type, entity_id, event_time DESC);


-- Audit account balance changes in the same database transaction.
CREATE OR REPLACE FUNCTION audit_account_balance_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.balance_kobo IS DISTINCT FROM NEW.balance_kobo THEN
        INSERT INTO audit_logs(entity_type, entity_id, action, event_time, details)
        VALUES ('ACCOUNT', NEW.account_id, 'BALANCE_UPDATED', now(),
                jsonb_build_object('old_balance_kobo', OLD.balance_kobo,
                                   'new_balance_kobo', NEW.balance_kobo));
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_account_balance_audit
AFTER UPDATE OF balance_kobo ON accounts
FOR EACH ROW EXECUTE FUNCTION audit_account_balance_change();
