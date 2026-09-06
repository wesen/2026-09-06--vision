"""Read-only adapter from sampled observation memory to the pure evaluator."""
from pathlib import Path
import json
import sqlite3
from video_workbench.temporal.store import Observation
from .evaluate import evaluate,validate_rule


def evaluate_stored(path,run_id,rule,episode_id,entity_id,events,as_of_us,coverage=()):
    validate_rule(rule)
    observations=[]
    if rule['op']=='state_at_event':
        con=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
        try:
            rows=con.execute('SELECT payload FROM observations WHERE run_id=? AND stream_id=? AND episode_id=? AND entity=? AND property=? AND available_us<=? AND committed_us<=? ORDER BY observation_id',
                    (run_id,rule['state_stream'],episode_id,entity_id,rule['property'],as_of_us,as_of_us)).fetchall()
            observations=[Observation(**json.loads(r[0])) for r in rows]
        finally:con.close()
    result=evaluate(rule,episode_id,entity_id,events,observations,coverage,as_of_us)
    # Run identity distinguishes equal observations/evaluations in independent runs.
    from .evaluate import digest
    result['run_id']=run_id;result['evaluation_id']=digest({k:v for k,v in result.items() if k!='evaluation_id'})
    return result
