"""Evaluate actual sparse state predictions; sample triggers are not departures."""
from pathlib import Path
from collections import Counter
import json
import sqlite3
from video_workbench.rules.evaluate import Event
from video_workbench.rules.stored import evaluate_stored
from video_workbench.registry import file_hash

source=Path('output/temporal-v1/replay-v1/observations.sqlite')
con=sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)
try:rows=[json.loads(r[0]) for r in con.execute("SELECT payload FROM observations WHERE stream_id LIKE 'state/%' ORDER BY observation_id")]
finally:con.close()
records=[]
for row in rows:
    # The frame-sample event is an explicit diagnostic binding, never departure truth.
    event=Event('sample/'+row['observation_id'],row['episode_id'],row['entity'],'frame-sample','sample',row['event_us'],row['event_us'],row['event_us'],row['event_us'])
    rule={'schema_version':1,'rule_id':'closed-at-sampled-frame','op':'state_at_event','event_stream':'frame-sample','event_id':event.id,'state_stream':row['stream_id'],'property':'door_open','expected':False}
    kwargs=dict(path=source,run_id=row['run_id'],rule=rule,episode_id=row['episode_id'],entity_id=row['entity'],events=[event])
    before=evaluate_stored(**kwargs,as_of_us=row['committed_us']-1)
    after=evaluate_stored(**kwargs,as_of_us=row['committed_us'])
    assert before['status']=='UNKNOWN'
    expected='UNKNOWN' if row['value'] is None else ('PASS' if row['value'] is False else 'VIOLATION')
    assert after['status']==expected,(row,after)
    assert evaluate_stored(**kwargs,as_of_us=row['committed_us'])==after
    records.append({'source_observation_id':row['observation_id'],'stream_id':row['stream_id'],'before':before,'after':after})
root=Path(__file__).resolve().parents[1];out=root/'various/r2-stored';out.mkdir(exist_ok=True)
(out/'evaluations.json').write_text(json.dumps(records,indent=2)+'\n')
summary={'kind':'actual predicted state at explicit sampled-frame triggers; not departure/continuous rule accuracy',
         'rows':len(rows),'source_sqlite_sha256':file_hash(source),'before':dict(Counter(r['before']['status'] for r in records)),
         'after':dict(Counter(r['after']['status'] for r in records)),
         'streams':{stream:dict(Counter(r['after']['status'] for r in records if r['stream_id']==stream)) for stream in sorted({r['stream_id'] for r in records})},
         'reopened_query_equal':True,'evaluation_policy':'immutable repeated evaluations; no replacement or supersession'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
