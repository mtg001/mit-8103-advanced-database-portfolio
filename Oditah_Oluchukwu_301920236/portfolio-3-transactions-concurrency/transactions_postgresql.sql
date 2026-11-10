-- PostgreSQL transaction pattern for a real banking transfer.
-- Execute with psql after loading schema_postgresql.sql and representative test data.
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Lock both account rows in deterministic order to reduce deadlock risk.
SELECT account_id, balance_kobo, status
FROM accounts
WHERE account_id IN ('ACC0001','ACC0002')
ORDER BY account_id
FOR UPDATE;

-- Application must validate both rows exist, are ACTIVE, share NGN currency,
-- and the debit balance is >= the requested amount before executing updates.
UPDATE accounts SET balance_kobo = balance_kobo - 25000 WHERE account_id='ACC0001';
UPDATE accounts SET balance_kobo = balance_kobo + 25000 WHERE account_id='ACC0002';
INSERT INTO transfers(transfer_id,reference,debit_account_id,credit_account_id,amount_kobo,currency,status,description)
VALUES ('TRF-PG-DEMO-001','PG-DEMO-001','ACC0001','ACC0002',25000,'NGN','COMPLETED','PostgreSQL transaction demonstration');
INSERT INTO ledger_entries(transfer_id,account_id,direction,amount_kobo)
VALUES ('TRF-PG-DEMO-001','ACC0001','DEBIT',25000),
       ('TRF-PG-DEMO-001','ACC0002','CREDIT',25000);
COMMIT;

-- To test rollback safely, begin a new transaction, run test changes, then:
-- ROLLBACK;
-- Do not run the demo INSERT repeatedly with the same primary key/reference.
