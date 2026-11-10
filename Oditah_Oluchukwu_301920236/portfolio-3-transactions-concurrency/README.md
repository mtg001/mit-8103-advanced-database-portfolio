# Portfolio 3 - Transactions and concurrency

`transaction_demo.py` runs against the local SQLite database and captures four outcomes: a successful committed transfer, a deliberate rollback, rejection of an insufficient-funds transfer, and a two-connection writer-lock test. It uses integer kobo and writes the balance updates, transfer record and two ledger entries within one transaction.

SQLite's `BEGIN IMMEDIATE` takes the write reservation before the balance check. The concurrency test demonstrates that a second writer cannot proceed while the first holds that reservation. This is SQLite's concurrency model, not evidence of PostgreSQL row-level locking.

`transactions_postgresql.sql` is the PostgreSQL counterpart. It locks both account rows with `SELECT ... FOR UPDATE`, sorted by account ID to reduce deadlock risk, and commits the balance, transfer and ledger changes together. Production code must check account status, currency, sufficient funds, idempotency and validation before applying updates. The PostgreSQL script is a reference implementation and has not been executed against a PostgreSQL server in this environment.
