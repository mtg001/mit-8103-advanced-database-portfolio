# Portfolio 1 - Database design and modelling

## Case study: Meridian Digital Bank (simulated)
Meridian Digital Bank is a fictional Nigerian digital bank used only for this academic portfolio. Its database supports customer onboarding, account maintenance, internal transfers, double-entry posting, customer transaction history and audit review. Users include customers, customer-support officers, operations staff, auditors and authorised banking services. All dataset values are synthetic and do not represent real people or a real bank.

## Main entities and relationships
- **Customer** has one or more **Accounts** (1:M).
- **Branch** serves one or more **Accounts** (1:M).
- **Transfer** identifies one debit account and one credit account. The two account roles are foreign keys to `accounts`.
- **LedgerEntry** records the debit/credit posting for a transfer. A successful simple transfer creates at least two entries with equal amounts and opposite directions.
- **AuditLog** records changes that require traceability.

The ER diagram is supplied as PNG, SVG and Graphviz source in this folder. `schema_sqlite.sql` is the executable reference schema used for local evidence. `schema_postgresql.sql` supplies the PostgreSQL deployment equivalent.

## Relational schema and integrity
Primary keys uniquely identify records. Foreign keys prevent orphan accounts, transfers and ledger entries. Unique constraints protect email, phone, account number and transfer reference. `CHECK` constraints enforce allowed statuses, NGN currency, positive amounts, non-negative balances and different source/destination accounts. Indexes support common customer, transfer, ledger and audit lookups. An account-balance trigger appends an audit row after a balance change.

Amounts are stored as integer kobo to avoid floating-point rounding. The `accounts.balance_kobo` value is a maintained balance projection; the immutable transfer/ledger trail is the transaction history. In a production deployment, reconciliation jobs should compare the balance projection with the ledger and alert on any mismatch.

## Normalisation
- **1NF:** attributes are atomic; repeating transfer entries are separate ledger rows, not comma-separated lists.
- **2NF:** the tables use single-column primary keys; non-key attributes depend on the whole key. Ledger facts are stored per entry rather than mixed into account or customer records.
- **3NF:** customer details, branch details, account details, transfer details and audit facts are separated. Non-key attributes do not depend transitively on another non-key attribute within the same table. Customer name is not copied into each account; branch city is stored with the branch rather than repeated in every account.

`balance_kobo` is deliberately maintained as an operational summary for fast account reads. It is a controlled denormalised projection, updated in the same transaction as ledger entries and checked through reconciliation; it is not a substitute for the ledger source of truth.

## Evidence and reproduction
Run `python portfolio-1-database-design/seed_data.py` from the repository root to recreate the deterministic synthetic dataset. The database is placed at `data/meridian_bank.db`.
