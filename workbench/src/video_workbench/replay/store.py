"""One writer; immutable rows and bounded read-only as-of pagination."""
from pathlib import Path
import json
import sqlite3
from video_workbench.rules.evaluate import digest


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


class ReplayStore:
    def __init__(self, path, *, readonly=False):
        path = Path(path).resolve()
        self.readonly = readonly
        self.con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) if readonly else sqlite3.connect(path)
        self.con.row_factory = sqlite3.Row
        if not readonly:
            self.con.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS records (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT UNIQUE NOT NULL,
                    kind TEXT NOT NULL,
                    case_id TEXT,
                    cycle INTEGER NOT NULL,
                    event_us INTEGER NOT NULL,
                    available_us INTEGER NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS records_horizon ON records(available_us, seq);
                CREATE TRIGGER IF NOT EXISTS records_no_update BEFORE UPDATE ON records
                    BEGIN SELECT RAISE(ABORT, 'replay records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS records_no_delete BEFORE DELETE ON records
                    BEGIN SELECT RAISE(ABORT, 'replay records are immutable'); END;
            ''')

    def close(self):
        self.con.close()

    def append(self, kind, payload, *, event_us, available_us, cycle=0, case_id=None, record_id=None):
        if self.readonly:
            raise ValueError('read-only replay store')
        if any(type(v) is not int or v < 0 for v in (event_us, available_us, cycle)) or event_us > available_us:
            raise ValueError('invalid replay clocks')
        if not isinstance(kind, str) or not kind:
            raise ValueError('record kind required')
        text = canonical(payload)
        if len(text.encode()) > 1_048_576:
            raise ValueError('replay payload exceeds 1 MiB')
        row = dict(kind=kind, case_id=case_id, cycle=cycle, event_us=event_us, available_us=available_us, payload=payload)
        record_id = record_id or digest(row)
        old = self.con.execute('SELECT * FROM records WHERE record_id=?', (record_id,)).fetchone()
        if old:
            if any(old[k] != v for k, v in dict(kind=kind, case_id=case_id, cycle=cycle, event_us=event_us, available_us=available_us, payload=text).items()):
                raise ValueError('record identity reused with changed content')
            return old['seq']
        latest = self.con.execute('SELECT MAX(available_us) FROM records').fetchone()[0]
        if latest is not None and available_us < latest:
            raise ValueError('replay commit horizon moved backwards')
        with self.con:
            cursor = self.con.execute('INSERT INTO records(record_id,kind,case_id,cycle,event_us,available_us,payload) VALUES(?,?,?,?,?,?,?)', (record_id,kind,case_id,cycle,event_us,available_us,text))
        return cursor.lastrowid

    def events(self, *, as_of_us, after=0, limit=200):
        if any(type(v) is not int or v < 0 for v in (as_of_us,after,limit)) or not 1 <= limit <= 500:
            raise ValueError('invalid cursor, horizon, or page limit')
        rows = self.con.execute('SELECT * FROM records WHERE seq>? AND available_us<=? ORDER BY seq LIMIT ?', (after,as_of_us,limit)).fetchall()
        result = [dict(r) for r in rows]
        for r in result:
            r['payload'] = json.loads(r['payload'])
        return dict(events=result, next_after=result[-1]['seq'] if result else after, as_of_us=as_of_us)
