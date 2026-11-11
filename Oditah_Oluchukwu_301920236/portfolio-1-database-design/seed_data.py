"""Create a fully synthetic, deterministic demo dataset."""
from pathlib import Path
import sqlite3, random, datetime as dt
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'meridian_bank.db'
SCHEMA = ROOT / 'portfolio-1-database-design' / 'schema_sqlite.sql'

def seed(reset=True, transfer_count=12000, customer_count=120):
    if reset and DB.exists(): DB.unlink()
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript(SCHEMA.read_text(encoding='utf-8'))
    con.executemany('INSERT OR IGNORE INTO branches VALUES (?,?,?,?)', [
        ('BR001','Victoria Island','Lagos','Lagos'),
        ('BR002','Ikeja','Ikeja','Lagos'),
        ('BR003','Wuse','Abuja','FCT')])
    base = dt.datetime(2026, 10, 1, 12, 0, 0)
    customers=[]; accounts=[]; balances={}
    for i in range(1, customer_count+1):
        cid=f'CUST{i:04d}'; aid=f'ACC{i:04d}'
        customers.append((cid, f'Customer{i}', 'Demo', f'customer{i}@example.test', f'080{i:08d}', base.isoformat(timespec='seconds')))
        accounts.append((aid,cid, ['BR001','BR002','BR003'][(i-1)%3], f'{1000000000+i:010d}', 'SAVINGS' if i%2 else 'CURRENT', 'NGN', 100_000_000, 'ACTIVE', base.isoformat(timespec='seconds')))
        balances[aid]=100_000_000
    con.executemany('INSERT INTO customers VALUES (?,?,?,?,?,?)', customers)
    con.executemany('INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?,?)', accounts)
    rng=random.Random(8103)
    transfer_rows=[]; ledger_rows=[]
    start=base-dt.timedelta(days=365)
    for n in range(1, transfer_count+1):
        src_idx=rng.randrange(customer_count); dst_idx=rng.randrange(customer_count-1)
        if dst_idx >= src_idx: dst_idx += 1
        src=f'ACC{src_idx+1:04d}'; dst=f'ACC{dst_idx+1:04d}'
        amount=rng.randint(1_000, 100_000) # NGN 10.00 to NGN 1,000.00 in kobo
        if balances[src] < amount:  # maintain non-negative balances
            src, dst = dst, src
        if balances[src] < amount:  # practically unreachable with opening balances
            continue
        balances[src]-=amount; balances[dst]+=amount
        event_time=start+dt.timedelta(seconds=rng.randint(0,365*24*3600))
        ts=event_time.isoformat(timespec='seconds')
        tid=f'TRF{n:08d}'; ref=f'MERIDIAN-{n:08d}'
        transfer_rows.append((tid,ref,src,dst,amount,'NGN','COMPLETED','Synthetic portfolio transaction',ts,ts))
        ledger_rows.append((tid,src,'DEBIT',amount,ts))
        ledger_rows.append((tid,dst,'CREDIT',amount,ts))
    con.executemany('UPDATE accounts SET balance_kobo=? WHERE account_id=?', [(bal, aid) for aid,bal in balances.items()])
    con.executemany('INSERT INTO transfers VALUES (?,?,?,?,?,?,?,?,?,?)', transfer_rows)
    con.executemany('INSERT INTO ledger_entries(transfer_id,account_id,direction,amount_kobo,posted_at) VALUES (?,?,?,?,?)', ledger_rows)
    con.commit()
    result={
      'database': str(DB), 'customers': len(customers), 'accounts': len(accounts),
      'transfers': len(transfer_rows), 'ledger_entries': len(ledger_rows),
      'branches': con.execute('SELECT COUNT(*) FROM branches').fetchone()[0],
      'synthetic_data': True
    }
    con.close()
    return result
if __name__=='__main__': print(seed())
