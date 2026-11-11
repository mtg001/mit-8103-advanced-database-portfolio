"""Commit, rollback, insufficient-funds and concurrent-writer demonstrations."""
from pathlib import Path
import sqlite3, uuid, datetime as dt
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'meridian_bank.db'
OUT=Path(__file__).resolve().parent/'evidence'
OUT.mkdir(parents=True,exist_ok=True)

def connect(timeout=2.0):
    c=sqlite3.connect(DB, timeout=timeout, isolation_level=None)
    c.execute('PRAGMA foreign_keys=ON')
    c.execute(f'PRAGMA busy_timeout={int(timeout*1000)}')
    return c

def perform_transfer(con, src, dst, amount, reference):
    tid='TRF-DEMO-'+uuid.uuid4().hex[:12].upper()
    now=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    try:
        con.execute('BEGIN IMMEDIATE')
        srcrow=con.execute('SELECT balance_kobo,status FROM accounts WHERE account_id=?',(src,)).fetchone()
        dstrow=con.execute('SELECT balance_kobo,status FROM accounts WHERE account_id=?',(dst,)).fetchone()
        if not srcrow or not dstrow: raise ValueError('Account not found')
        if srcrow[1] != 'ACTIVE' or dstrow[1] != 'ACTIVE': raise ValueError('Both accounts must be active')
        if srcrow[0] < amount: raise ValueError('Insufficient funds')
        con.execute('UPDATE accounts SET balance_kobo=balance_kobo-? WHERE account_id=?',(amount,src))
        con.execute('UPDATE accounts SET balance_kobo=balance_kobo+? WHERE account_id=?',(amount,dst))
        con.execute('INSERT INTO transfers VALUES (?,?,?,?,?,?,?,?,?,?)',
                    (tid,reference,src,dst,amount,'NGN','COMPLETED','Demonstration transfer',now,now))
        con.executemany('INSERT INTO ledger_entries(transfer_id,account_id,direction,amount_kobo,posted_at) VALUES (?,?,?,?,?)',[
            (tid,src,'DEBIT',amount,now),(tid,dst,'CREDIT',amount,now)])
        con.commit()
        return tid
    except Exception:
        con.rollback()
        raise

def main():
    lines=['MERIDIAN DIGITAL BANK - TRANSACTION AND CONCURRENCY EVIDENCE']
    con=connect()
    before=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0001"').fetchone()[0]
    tid=perform_transfer(con,'ACC0001','ACC0002',25_000,'DEMO-COMMIT-001')
    after=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0001"').fetchone()[0]
    lines.append(f'COMMIT: transfer {tid} committed; debit account reduced by 25000 kobo: {before} -> {after}')
    assert before-after==25_000
    # Deliberate rollback: stage both account changes, then rollback before any ledger event.
    s0=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0001"').fetchone()[0]
    d0=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0002"').fetchone()[0]
    con.execute('BEGIN IMMEDIATE')
    con.execute('UPDATE accounts SET balance_kobo=balance_kobo-1000 WHERE account_id="ACC0001"')
    con.execute('UPDATE accounts SET balance_kobo=balance_kobo+1000 WHERE account_id="ACC0002"')
    con.rollback()
    s1=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0001"').fetchone()[0]
    d1=con.execute('SELECT balance_kobo FROM accounts WHERE account_id="ACC0002"').fetchone()[0]
    assert (s0,d0)==(s1,d1)
    lines.append(f'ROLLBACK: staged 1000-kobo debit/credit was rolled back; balances unchanged ({s0}={s1}; {d0}={d1})')
    # Invalid transfer: the function must rollback after insufficient funds.
    try:
        perform_transfer(con,'ACC0001','ACC0002',10**15,'DEMO-OVERDRAFT-001')
        raise AssertionError('Expected insufficient-funds rejection')
    except ValueError as e:
        lines.append(f'REJECTION: {e}; transaction rolled back')
    con.close()
    # SQLite concurrency: BEGIN IMMEDIATE on connection A reserves the writer slot.
    a=connect(timeout=2.0); b=connect(timeout=0.1)
    a.execute('BEGIN IMMEDIATE')
    try:
        try:
            b.execute('BEGIN IMMEDIATE')
            lines.append('CONCURRENCY: second writer unexpectedly acquired the lock')
            b.rollback()
        except sqlite3.OperationalError as e:
            lines.append(f'CONCURRENCY: second writer was blocked/rejected while first writer held BEGIN IMMEDIATE ({e})')
    finally:
        a.rollback(); a.close(); b.close()
    lines.append('ISOLATION NOTE: SQLite uses serialised writes; this local lock test is not a PostgreSQL MVCC test. The PostgreSQL example uses SELECT ... FOR UPDATE and documents row-level locking.')
    text='\n'.join(lines)+'\n'
    (OUT/'transaction_results.txt').write_text(text,encoding='utf-8')
    print(text)
if __name__=='__main__': main()
