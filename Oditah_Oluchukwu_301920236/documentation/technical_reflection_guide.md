 Individual technical reflection 


1. Why I selected a relational database

I selected a relational database for the core banking operations because account balances, transfers, and ledger entries require accuracy and consistency. A transfer involves more than one account, and both sides of the transaction must be recorded correctly. PostgreSQL and SQLite support transactions that allow related changes to be committed together or rolled back if something goes wrong.

2. Entity relationships and integrity constraints

The most important relationships were between customers and accounts, branches and accounts, transfers and accounts, and transfers and ledger entries.

I used primary keys to uniquely identify records and foreign keys to maintain relationships between the entities. I also used constraints to prevent invalid data, including negative account balances, invalid account statuses, unsupported currencies, and duplicate account numbers or transfer references. These constraints help protect the integrity of banking records.

3. Query optimisation and indexing

I tested an account-statement query against a synthetic dataset containing 24,000 ledger entries.

Before adding the composite covering index, SQLite performed a full table scan on ledger_entries and used a temporary B-tree to sort the results. After adding idx_ledger_account_posted, the query used an indexed search instead.

In my recorded local benchmark, the median execution time reduced from approximately 0.9649 milliseconds to 0.0534 milliseconds over 150 executions. This showed me how an appropriate index can improve query performance. I also learned that these results represent a local synthetic-data test rather than a guarantee of production performance.

4. Transactions and concurrency

I tested successful transfers, rollbacks, and insufficient-funds rejection. The successful transfer demonstrated that the debit and credit could be committed together. The rollback test showed that staged changes could be reversed without changing the original balances. The insufficient-funds test also demonstrated that an invalid transfer could be rejected without leaving partial changes.

My SQLite concurrency test showed that a second writer could be blocked while another transaction held a write lock using BEGIN IMMEDIATE. I learned that SQLite serialises writes, so this demonstration should not be confused with PostgreSQL's row-level locking and MVCC behaviour.

I subsequently executed the supplied PostgreSQL transaction demonstration in a separate test database. I verified that the debit and credit were committed, the transfer was marked COMPLETED, and matching ledger entries were created.

5. NoSQL data modelling

I used MongoDB for the NoSQL part of the portfolio. I designed the customer profile collection to hold a bounded summary of customer information because this information is frequently accessed together.

I kept transfer events in a separate collection because transaction histories can grow continuously. Keeping them separate avoids an ever-growing customer document and makes it easier to query, index, and manage transfer history independently.

6. Read replicas and consistency

Read replicas can improve the performance and availability of a banking system by distributing read requests across multiple database servers. However, replication can introduce a delay between the primary database and a replica.

For a recently completed transfer, reading from a replica before it has received the latest update could display an old account balance. This is a read-after-write consistency problem. For this reason, a banking application should retrieve critical post-transfer balances from the primary database or use an appropriate consistency mechanism.

7. My personal execution and learning experience

I personally set up and tested the database environments for this portfolio. I executed the SQLite workflow, examined query plans, tested transaction commit and rollback behaviour, and captured the results.

I also configured MongoDB locally as a replica set, executed the NoSQL implementation work, and checked its indexes and query execution statistics.

One challenge I encountered was distinguishing between the SQLite demonstration and the PostgreSQL implementation. I initially had PostgreSQL tables without test records. I loaded the PostgreSQL schema into a dedicated portfolio database, inserted synthetic test accounts, and executed the transfer demonstration. I verified that the debit account decreased from ₦100,000 to ₦99,750, while the credit account increased from ₦50,000 to ₦50,250. The transfer and both ledger entries were successfully recorded.

This practical work improved my understanding of relational database design, query optimisation, transaction management, indexing, and NoSQL modelling. It also taught me the importance of testing implementations and keeping evidence of the actual results.
