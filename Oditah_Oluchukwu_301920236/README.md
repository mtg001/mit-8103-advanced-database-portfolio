MIT 8103 Advanced Database Systems - Practical Portfolio

Case study: Meridian Digital Bank (simulated)  
Student: Oditah Oluchukwu Michael  
Student ID: 301920236  
Assessment: First Semester Continuous Assessment, 2026/2027  
Course: MIT 8103 - Advanced Database Systems


Repository: https://github.com/mtg001/mit-8103-advanced-database-portfolio

This repository contains the MIT 8103 Advanced Database Systems practical portfolio, including database design, query optimisation, transaction processing, NoSQL implementation, and distributed cloud architecture.

Case study
Meridian Digital Bank is a fictional Nigerian digital banking scenario. The database supports customer onboarding, account management, account-to-account transfers, double-entry ledger posting, account statements, and audit trails. All sample data is synthetic.

Repository structure
- `portfolio-1-database-design/` - ER diagram, SQLite reference schema, PostgreSQL schema, seed script and normalisation.
- `portfolio-2-query-optimisation/` - SQL examples, query-plan/performance script and captured local evidence.
- `portfolio-3-transactions-concurrency/` - commit, rollback, insufficient-funds and writer-lock demo; PostgreSQL row-locking script.
- `portfolio-4-nosql/` - MongoDB document model, JSON sample documents, `mongosh` implementation and validation note.
- `portfolio-5-distributed-cloud/` - managed-cloud architecture, replication, partitioning, consistency, security and recovery design, plus a rendered architecture diagram.
- `documentation/` - final summary, reflection guide, AI-use declaration and references.
- `data/` - generated SQLite database containing synthetic data (recreated by the seed script).
- `evidence/` - overall test log.

 Local run instructions
Requires Python 3.10+ and only the Python standard library for the relational demo.

From the repository root:

```bash
python portfolio-1-database-design/seed_data.py
python portfolio-2-query-optimisation/performance_demo.py
python portfolio-3-transactions-concurrency/transaction_demo.py
```

Or run all local relational steps in one command:

```bash
python run_portfolio.py
```

The scripts recreate a local SQLite database and write evidence under the relevant `evidence/` folders. They use synthetic data only. The query-plan timing is a small local benchmark, not a production capacity claim.



