"""Capture before/after plans and timings for the account-statement query."""
from pathlib import Path
import sqlite3, time, statistics
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'meridian_bank.db'
OUT=Path(__file__).resolve().parent/'evidence'
OUT.mkdir(parents=True,exist_ok=True)
SQL="""SELECT entry_id, direction, amount_kobo, posted_at
FROM ledger_entries
WHERE account_id=? AND posted_at>=? AND posted_at<?
ORDER BY posted_at DESC LIMIT 100"""
PARAMS=('ACC0001','2026-01-01T00:00:00','2026-10-01T00:00:00')

def plan(con):
    return [row[3] for row in con.execute('EXPLAIN QUERY PLAN '+SQL,PARAMS)]
def median_ms(con, repeats=150):
    samples=[]
    for _ in range(repeats):
        t=time.perf_counter()
        con.execute(SQL,PARAMS).fetchall()
        samples.append((time.perf_counter()-t)*1000)
    return statistics.median(samples)

def main():
    con=sqlite3.connect(DB)
    con.execute('DROP INDEX IF EXISTS idx_ledger_account_posted')
    con.commit()
    before_plan=plan(con); before_ms=median_ms(con)
    con.execute('CREATE INDEX idx_ledger_account_posted ON ledger_entries(account_id, posted_at DESC, direction, amount_kobo)')
    con.execute('ANALYZE')
    con.commit()
    after_plan=plan(con); after_ms=median_ms(con)
    rows=con.execute(SQL,PARAMS).fetchall()
    out=[]
    out.append('MERIDIAN DIGITAL BANK - QUERY OPTIMISATION EVIDENCE')
    out.append(f'Rows returned by account statement query: {len(rows)}')
    out.append(f'Total ledger rows in benchmark table: {con.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0]}')
    out.append('')
    out.append('BEFORE COMPOSITE INDEX')
    out.extend('  '+x for x in before_plan)
    out.append(f'Median of 150 local executions: {before_ms:.4f} ms')
    out.append('')
    out.append('AFTER COMPOSITE COVERING INDEX')
    out.extend('  '+x for x in after_plan)
    out.append(f'Median of 150 local executions: {after_ms:.4f} ms')
    out.append('')
    out.append('INTERPRETATION')
    out.append('The before plan should scan ledger_entries. The after plan should search using idx_ledger_account_posted; the selected columns are included in the index, so SQLite may label it a covering-index search.')
    out.append('Timing is a local micro-benchmark on a synthetic dataset and is not a production performance guarantee. Cache state, host hardware, SQLite version and dataset size affect timings.')
    text='\n'.join(out)+'\n'
    (OUT/'query_plan_and_timing.txt').write_text(text,encoding='utf-8')
    (OUT/'query_plan_before.txt').write_text('\n'.join(before_plan)+'\n',encoding='utf-8')
    (OUT/'query_plan_after.txt').write_text('\n'.join(after_plan)+'\n',encoding='utf-8')
    con.close()
    print(text)
if __name__=='__main__': main()
