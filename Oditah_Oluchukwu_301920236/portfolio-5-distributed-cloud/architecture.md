# Portfolio 5 - Distributed and cloud database exercise

## Proposed deployment
The simulated bank's relational system is designed for a managed PostgreSQL deployment on Amazon RDS (or an equivalent managed PostgreSQL service).

### Logical topology
1. Mobile/web channels call stateless API services through an application load balancer.
2. The transaction service writes account, transfer and ledger changes to a PostgreSQL writer endpoint.
3. A Multi-AZ standby provides synchronous high-availability replication and automatic failover within a region.
4. A read replica / readable standby serves non-critical customer history, operations dashboards and reporting queries where supported by the chosen RDS deployment mode.
5. Backups and point-in-time recovery protect against logical and infrastructure failures. A separate region may host a cross-region replica for disaster recovery, subject to replication lag and recovery objectives.
6. Monitoring tracks replication lag, connection saturation, slow queries, lock waits, storage, failed logins and backup status.

## Replication and consistency
A synchronous standby is preferred for high availability because committed primary changes are replicated before acknowledgement according to the selected managed-service mode. Read replicas used for reporting can lag behind the writer. Therefore, account balances, transfer confirmation and other read-after-write critical paths must read from the writer (or use an explicitly consistent read design). A stale replica must not be treated as authoritative proof that a transfer failed.

## Sharding / partitioning strategy
At the first growth stage, use vertical scaling and partition large append-only ledger / transfer tables by posting month or business date. This supports retention management and time-range reporting without immediately distributing customer/account transactions across shards. If volume later requires horizontal partitioning, route a customer/account group consistently by a stable tenant or customer hash and keep the account balance, transfer state and ledger for a transfer within the same transactional boundary wherever possible.

Cross-shard transfers are materially more complex because they may need a distributed transaction or a carefully designed workflow (for example, reservation, posting and compensating reversal). Do not split a debit and credit across independent databases and assume a local SQL transaction will protect both. Use idempotency references, an outbox/event mechanism, reconciliation and explicit reversal states.

## Availability, recovery and security controls
- Deploy across separate Availability Zones and test failover procedures.
- Define and test recovery point objective (RPO) and recovery time objective (RTO); do not assume replica presence alone proves disaster recovery.
- Encrypt data at rest and in transit; keep database endpoints private; restrict access using least-privilege roles and network security rules.
- Store credentials and keys in a managed secret/key service, rotate them and audit privileged access.
- Take automated backups, test restores, and maintain an independent recovery copy.
- Use connection pooling and application retry with idempotency keys so failover does not create duplicate transfers.

## Limitations of this exercise
This portfolio provides a design and deployment plan, not a live cloud deployment. No AWS account, managed database, replica or failover test was provisioned in the authoring environment. The proposed design is based on current AWS RDS documentation and should be mapped to the exact engine, deployment mode, region, budget and availability target selected by the operator.
