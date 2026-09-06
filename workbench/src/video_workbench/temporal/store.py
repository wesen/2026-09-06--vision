"""Small append-only observation store for replay, with no state extrapolation.

Observations concern exact sampled timestamps. Event, evidence availability, and
commit clocks are integer microseconds within an explicitly named replay run.
There is no expiry policy, revision chain, or inferred continuous state.
"""
from dataclasses import dataclass,asdict
import json
import sqlite3


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    run_id: str
    stream_id: str
    episode_id: str
    entity: str
    property: str
    value: object
    event_us: int
    available_us: int
    committed_us: int
    evidence_ids: tuple[str,...]
    producer: str
    feature_space_id: str
    mode: str
    unknown_reason: str | None = None

    def validate(self):
        for name in ('observation_id','run_id','stream_id','episode_id','entity','property','producer','feature_space_id'):
            if not isinstance(getattr(self,name),str) or not getattr(self,name):raise ValueError('observation identity required')
        if any(type(t) is not int or t<0 for t in (self.event_us,self.available_us,self.committed_us)):raise ValueError('nonnegative integer clocks required')
        if not self.event_us<=self.available_us<=self.committed_us:raise ValueError('event/availability/commit ordering invalid')
        if self.mode not in ('causal','offline'):raise ValueError('invalid inference mode')
        if not self.evidence_ids or any(not isinstance(e,str) or not e for e in self.evidence_ids):raise ValueError('source evidence required')
        if len(set(self.evidence_ids))!=len(self.evidence_ids):raise ValueError('duplicate evidence citation')
        if (self.value is None)!=(self.unknown_reason is not None):raise ValueError('unknown values require a reason, known values forbid it')
        canonical(asdict(self));return self


MIGRATION_1='''
CREATE TABLE observations (
 observation_id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL, stream_id TEXT NOT NULL, episode_id TEXT NOT NULL,
 entity TEXT NOT NULL, property TEXT NOT NULL, event_us INTEGER NOT NULL,
 available_us INTEGER NOT NULL, committed_us INTEGER NOT NULL, payload TEXT NOT NULL
);
CREATE INDEX observation_query ON observations(run_id,stream_id,episode_id,entity,property,event_us,committed_us);
CREATE TRIGGER observations_no_update BEFORE UPDATE ON observations BEGIN SELECT RAISE(ABORT,'observations are append-only'); END;
CREATE TRIGGER observations_no_delete BEFORE DELETE ON observations BEGIN SELECT RAISE(ABORT,'observations are append-only'); END;
PRAGMA user_version=1;
'''


class Store:
    def __init__(self,path):
        self.connection=sqlite3.connect(str(path),isolation_level=None)
        self.connection.row_factory=sqlite3.Row
        version=self.connection.execute('PRAGMA user_version').fetchone()[0]
        if version==0:
            try:self.connection.executescript('BEGIN IMMEDIATE;\n'+MIGRATION_1+'\nCOMMIT;')
            except Exception:
                if self.connection.in_transaction:self.connection.rollback()
                self.connection.close();raise
        elif version!=1:
            self.connection.close();raise ValueError('unsupported observation schema')

    def close(self):self.connection.close()

    def append(self,observation):
        """Insert atomically; exact retries preserve the original commitment time."""
        observation.validate();payload=asdict(observation);con=self.connection
        con.execute('BEGIN IMMEDIATE')
        try:
            previous=con.execute('SELECT payload FROM observations WHERE observation_id=?',(observation.observation_id,)).fetchone()
            if previous:
                old=json.loads(previous['payload']);new=json.loads(canonical(payload))
                for r in (old,new):r.pop('committed_us')
                if old!=new:raise ValueError('observation ID reused with changed content')
                con.commit();return False
            latest=con.execute('SELECT MAX(committed_us) FROM observations WHERE run_id=?',(observation.run_id,)).fetchone()[0]
            if latest is not None and observation.committed_us<latest:raise ValueError('run commitment clock moved backwards')
            stream=con.execute('SELECT payload FROM observations WHERE run_id=? AND stream_id=? LIMIT 1',(observation.run_id,observation.stream_id)).fetchone()
            if stream:
                old=json.loads(stream['payload'])
                if any(old[k]!=payload[k] for k in ('producer','feature_space_id','mode')):raise ValueError('mixed producers in observation stream')
            con.execute('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?)',
                (observation.observation_id,observation.run_id,observation.stream_id,observation.episode_id,observation.entity,observation.property,observation.event_us,observation.available_us,observation.committed_us,canonical(payload)))
            con.commit();return True
        except Exception:
            con.rollback();raise

    def state_at(self,run_id,stream_id,episode_id,entity,property,event_us,as_of_us):
        """Return evidence at exactly event_us; never hold a sampled state forward."""
        if type(event_us) is not int or type(as_of_us) is not int or min(event_us,as_of_us)<0:raise ValueError('integer query clocks required')
        rows=self.connection.execute('SELECT payload FROM observations WHERE run_id=? AND stream_id=? AND episode_id=? AND entity=? AND property=? AND event_us=? AND available_us<=? AND committed_us<=? ORDER BY observation_id',
                (run_id,stream_id,episode_id,entity,property,event_us,as_of_us,as_of_us)).fetchall()
        records=[json.loads(r['payload']) for r in rows]
        result={'status':'unknown','value':None,'event_us':event_us,'as_of_us':as_of_us,
                'observation_ids':[r['observation_id'] for r in records],
                'evidence_ids':sorted({e for r in records for e in r['evidence_ids']})}
        if not records:return dict(result,reason='no_visible_sample')
        if any(r['value'] is None for r in records):return dict(result,reason='source_unknown',source_reasons=sorted({r['unknown_reason'] for r in records if r['unknown_reason']}))
        if len({canonical(r['value']) for r in records})!=1:return dict(result,reason='disagreeing_samples')
        return dict(result,status='supported',value=records[0]['value'],reason='observed_sample')
