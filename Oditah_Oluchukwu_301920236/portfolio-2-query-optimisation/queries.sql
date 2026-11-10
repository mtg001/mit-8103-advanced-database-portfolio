-- Query 1: customer account summary.
SELECT c.customer_id, c.first_name, c.last_name, a.account_number,
       a.account_type, a.balance_kobo, a.currency, a.status
FROM customers AS c
JOIN accounts AS a ON a.customer_id = c.customer_id
WHERE c.customer_id = 'CUST0001';

-- Query 2: transfer activity for one account, either outgoing or incoming.
SELECT transfer_id, reference, debit_account_id, credit_account_id,
       amount_kobo, status, initiated_at
FROM transfers
WHERE debit_account_id = 'ACC0001' OR credit_account_id = 'ACC0001'
ORDER BY initiated_at DESC
LIMIT 20;

-- Query 3: account statement. Optimised by a composite index on
-- (account_id, posted_at DESC) with direction and amount included in the index.
SELECT entry_id, direction, amount_kobo, posted_at
FROM ledger_entries
WHERE account_id = 'ACC0001'
  AND posted_at >= '2026-01-01T00:00:00'
  AND posted_at <  '2026-10-01T00:00:00'
ORDER BY posted_at DESC
LIMIT 100;

-- Query 4: monthly value sent by each account (illustrative aggregation).
SELECT account_id, substr(posted_at,1,7) AS posting_month,
       SUM(amount_kobo) AS total_debits_kobo, COUNT(*) AS debit_count
FROM ledger_entries
WHERE direction='DEBIT'
GROUP BY account_id, substr(posted_at,1,7)
ORDER BY posting_month DESC, total_debits_kobo DESC;

-- Query plan commands used by performance_demo.py:
-- EXPLAIN QUERY PLAN <statement> (SQLite)
-- For PostgreSQL: EXPLAIN (ANALYZE, BUFFERS) <statement>;
