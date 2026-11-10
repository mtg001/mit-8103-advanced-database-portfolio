# Portfolio 4 - NoSQL and advanced data models

## Selected model: MongoDB document database
The NoSQL design uses two main collections:

1. `customer_profiles` stores a customer-facing profile. Frequently retrieved contact, KYC state, account summaries and a short recent-transfer list are embedded so a dashboard can be served with one document read.
2. `transfer_events` stores the complete transfer event stream as separate documents. A customer activity query is supported by a compound index on `{ customerId: 1, createdAt: -1 }`; `reference` has a unique index for idempotency.
3. `accounts` stores the current account balance projection, while `ledger_entries` stores the balanced debit and credit postings. A transfer updates both accounts, the transfer event and the two ledger entries within one multi-document transaction.

This is a deliberate hybrid of embedding and referencing. Embedding is suitable for small, frequently read data that is used with the parent customer profile. A full transfer history is kept separately because it can grow without bound and must be paginated. The profile's `recentTransfers` array is a bounded cache only; `transfer_events` remains the full history.

## Suitability and trade-offs
- Flexible nested documents map naturally to customer dashboard data and optional KYC metadata.
- Embedded profile data reduces joins / round trips for a common read path.
- Duplicated account summaries require controlled updates and reconciliation.
- Multi-document transactions preserve atomicity for a transfer, but create coordination cost; use them for financial invariants rather than every dashboard read.
- Indexes speed customer activity lookups but increase storage and write-maintenance cost.

## Implementation evidence
`mongodb_implementation.js` is a runnable `mongosh` script. It clears only the named demo records, inserts profiles and accounts, creates indexes, runs a dashboard read and an explainable activity-feed query, then demonstrates a multi-document transaction. MongoDB transactions require a replica set or sharded deployment. `sample_documents.json` contains the corresponding document examples.

**Environment qualification:** MongoDB Server / `mongosh` was not available in the authoring environment, so the MongoDB script is supplied but has not been executed here. The JSON file was syntax-checked locally. Before submission, run the script on a local MongoDB replica set or Atlas test deployment and save screenshots of the inserted documents, index list, explain output and transaction result. Do not describe the MongoDB commands as executed until you have run them.
