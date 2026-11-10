"""Transactional append-only local data plane. SQLite owns atomicity and locking."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from patterns import digest, update, MINUTE


def encode(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=FULL')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS inputs(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS observations(ticker TEXT,generation INTEGER,t INTEGER,hash TEXT,payload TEXT,
      PRIMARY KEY(ticker,generation,t));
    CREATE TABLE IF NOT EXISTS signals(ticker TEXT,generation INTEGER,t INTEGER,id TEXT,payload TEXT,
      PRIMARY KEY(ticker,generation,t));
    CREATE TABLE IF NOT EXISTS checkpoints(seq INTEGER PRIMARY KEY AUTOINCREMENT,ticker TEXT,generation INTEGER,
      state TEXT,input_id TEXT,FOREIGN KEY(input_id) REFERENCES inputs(id));
    CREATE TABLE IF NOT EXISTS captures(seq INTEGER PRIMARY KEY AUTOINCREMENT,ticker TEXT,generation INTEGER,
      retrieved_at TEXT,input_id TEXT);
    ''')
    for table in ('inputs', 'observations', 'signals', 'checkpoints', 'captures'):
        for action in ('UPDATE', 'DELETE'):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append-only table'); END")
    return db


def capture(path, batch, asof, rebuild=False, retrospective=False):
    with closing(connect(path)) as db:
        try:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT generation,state FROM checkpoints WHERE ticker=? ORDER BY seq DESC LIMIT 1', (batch['ticker'],)).fetchone()
            generation = (old[0]+1 if rebuild else old[0]) if old else 1
            state = None if rebuild or not old else json.loads(old[1])
            state, signals = update(batch, asof, state, retrospective)
            # Persist exactly the completed input revision, not unknown future bars.
            recorded = dict(batch, bars=[b for b in batch['bars'] if b['t']+MINUTE <= asof])
            input_id = digest(recorded)
            db.execute('INSERT OR IGNORE INTO inputs VALUES (?,?)', (input_id, encode(recorded)))
            captured = db.execute('SELECT 1 FROM captures WHERE ticker=? AND generation=? AND input_id=?', (batch['ticker'], generation, input_id)).fetchone()
            if not captured:
                db.execute('INSERT INTO captures(ticker,generation,retrieved_at,input_id) VALUES (?,?,?,?)', (batch['ticker'], generation, batch['source'].get('retrieved_at'), input_id))
            for b in recorded['bars']:
                bh = digest(b)
                existing = db.execute('SELECT hash FROM observations WHERE ticker=? AND generation=? AND t=?', (batch['ticker'], generation, b['t'])).fetchone()
                if existing and existing[0] != bh:
                    raise ValueError('observation revision requires explicit new generation')
                db.execute('INSERT OR IGNORE INTO observations VALUES (?,?,?,?,?)', (batch['ticker'], generation, b['t'], bh, encode(b)))
            for s in signals:
                prior = db.execute('SELECT id FROM signals WHERE ticker=? AND t=? ORDER BY generation DESC LIMIT 1', (batch['ticker'], s['as_of'])).fetchone()
                record = dict(s, generation=generation, supersedes_signal_id=prior[0] if prior else None)
                db.execute('INSERT INTO signals VALUES (?,?,?,?,?)', (batch['ticker'], generation, s['as_of'], s['signal_id'], encode(record)))
            if signals or not old:
                db.execute('INSERT INTO checkpoints(ticker,generation,state,input_id) VALUES (?,?,?,?)', (batch['ticker'], generation, encode(state), input_id))
            db.commit()
        except BaseException:
            db.rollback()
            raise
        latest = db.execute('SELECT payload FROM signals WHERE ticker=? ORDER BY generation DESC,t DESC LIMIT 1', (batch['ticker'],)).fetchone()
        return {'new_signals': len(signals), 'generation': generation,
                'latest': json.loads(latest[0]) if latest else None}


def export(path, ticker, output):
    with closing(connect(path)) as db, Path(output).open('w') as f:
        for (payload,) in db.execute('SELECT payload FROM signals WHERE ticker=? ORDER BY generation,t', (ticker,)):
            f.write(payload+'\n')


def latest(path, ticker):
    with closing(connect(path)) as db:
        row = db.execute('SELECT payload FROM signals WHERE ticker=? ORDER BY generation DESC,t DESC LIMIT 1', (ticker,)).fetchone()
        return json.loads(row[0]) if row else None


def export_input(path, ticker, output):
    with closing(connect(path)) as db:
        row = db.execute('SELECT i.payload FROM captures c JOIN inputs i ON c.input_id=i.id WHERE c.ticker=? ORDER BY c.seq DESC LIMIT 1', (ticker,)).fetchone()
        if row is None:
            raise ValueError('no captured input for ticker')
        Path(output).write_text(row[0]+'\n')
