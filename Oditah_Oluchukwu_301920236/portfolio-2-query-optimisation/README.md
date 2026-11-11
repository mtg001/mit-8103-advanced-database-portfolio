# Portfolio 2 - Query processing and optimisation

The account-statement query filters by `account_id` and a `posted_at` range, sorts newest-first and returns a bounded page. The composite index follows the equality column first and the range/order column second. `direction` and `amount_kobo` are appended so the index can potentially cover the selected columns.

Run `python portfolio-2-query-optimisation/performance_demo.py` from the repository root after seeding. The script deliberately drops the composite index, captures `EXPLAIN QUERY PLAN`, measures 150 executions, creates the index, runs `ANALYZE`, and repeats the test. The actual captured plan and timings are stored in `evidence/`.

For PostgreSQL, use `EXPLAIN (ANALYZE, BUFFERS)` and inspect scan type, estimated versus actual rows, shared-buffer activity, planning time and execution time. PostgreSQL's `EXPLAIN ANALYZE` executes the statement, so use a transaction and rollback around data-changing statements.
