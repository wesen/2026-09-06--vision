"""Import measured state/action observations and exercise exact-time replay.

This is a local simulation of commitment delays, not a measured live run.
Source observations remain immutable. Oracle localization inputs are excluded.
"""
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .store import Store,Observation,canonical


def identity(row):return hashlib.sha256(canonical(row).encode()).hexdigest()


def state_observations(handoff,run_id,commit_delay_us):
    root=Path(handoff);manifest=json.loads((root/'manifest.json').read_text())
    source=root/'production.jsonl'
    if manifest['status']!='complete' or file_hash(source)!=manifest['streams']['production']['sha256']:raise ValueError('state handoff mismatch')
    rows=[json.loads(line) for line in source.read_text().splitlines()]
    if len(rows)!=manifest['streams']['production']['rows']:raise ValueError('state handoff count mismatch')
    observations=[];source_sha256=file_hash(source)
    for row in rows:
        if row['oracle_assisted']:raise ValueError('oracle evidence in production handoff')
        data=dict(run_id=run_id,stream_id='state/'+row['condition'],episode_id=row['episode_id'],entity=row['entity_id'],property=row['property'],value=row['value'],
                  event_us=row['sample_us'],available_us=row['available_us'],committed_us=row['available_us']+commit_delay_us,
                  evidence_ids=tuple(row['evidence_ids']),producer=row['producer_id'],feature_space_id=row['feature_space_id'],mode='causal',unknown_reason=row['unknown_reason'])
        observations.append(Observation(observation_id=identity(dict(source_sha256=source_sha256,sample_id=row['sample_id'],**data)),**data).validate())
    return observations


def action_observations(comparison,run_id,commit_delay_us):
    source=Path(comparison);report=json.loads(source.read_text());observations=[];source_sha256=file_hash(source)
    for method in ('linear','smooth'):
        producer=identity({'comparison_sha256':source_sha256,'method':method})
        for split,part in report['methods'][method]['metrics'].items():
            for eid,row in part['episodes'].items():
                for i,pred in enumerate(row['predictions']):
                    data=dict(run_id=run_id,stream_id='action/'+method,episode_id=eid,entity=eid+':actor',property='action',value=report['classes'][pred] if pred>=0 else None,
                              event_us=row['cell_end_us'][i],available_us=row['available_us'][i],committed_us=row['available_us'][i]+commit_delay_us,
                              evidence_ids=tuple(row['dependency_evidence_ids'][i] or row['evidence_ids'][i]),producer=producer,feature_space_id=row['feature_space_id'],mode=row['mode'],unknown_reason='missing_feature' if pred<0 else None)
                    observations.append(Observation(observation_id=identity(dict(index=i,**data)),**data).validate())
    return observations


def run(state_handoff,classical_comparison,destination,commit_delay_us=250000):
    dest=Path(destination)
    if dest.exists():raise ValueError('fresh replay destination required')
    if type(commit_delay_us) is not int or commit_delay_us<0:raise ValueError('nonnegative integer replay delay required')
    run_id='temporal-replay-v1'
    observations=state_observations(state_handoff,run_id,commit_delay_us)+action_observations(classical_comparison,run_id,commit_delay_us)
    observations.sort(key=lambda r:(r.committed_us,r.observation_id))
    dest.mkdir(parents=True);store=Store(dest/'observations.sqlite')
    try:
        inserted=sum(store.append(o) for o in observations)
        retries=sum(store.append(o) for o in observations)
        # Each actual observation is checked before and at durable availability.
        checks=[]
        for o in observations:
            args=(o.run_id,o.stream_id,o.episode_id,o.entity,o.property,o.event_us)
            before=store.state_at(*args,as_of_us=max(0,o.committed_us-1))
            after=store.state_at(*args,as_of_us=o.committed_us)
            if o.committed_us>0 and o.observation_id in before['observation_ids']:raise ValueError('future observation leaked')
            if o.observation_id not in after['observation_ids']:raise ValueError('committed observation missing')
            checks.append({'query':list(args),'before':before,'after':after})
        sample=next(o for o in observations if o.stream_id=='state/F__linear_head' and o.value is not None)
        # One microsecond after a sparse sampled frame must not inherit it.
        gap=store.state_at(sample.run_id,sample.stream_id,sample.episode_id,sample.entity,sample.property,sample.event_us+1,as_of_us=sample.committed_us+1000000)
        if gap['status']!='unknown':raise ValueError('sparse observation extrapolated')
    finally:store.close()
    store=Store(dest/'observations.sqlite')
    try:
        for check in checks:
            for name in ('before','after'):
                actual=store.state_at(*check['query'],as_of_us=check[name]['as_of_us'])
                if actual!=check[name]:raise ValueError('replay changed after restart')
    finally:store.close()
    (dest/'observations.jsonl').write_text(''.join(canonical(asdict(o))+'\n' for o in observations))
    write_json(dest/'queries.json',checks)
    report={'status':'complete','run_id':run_id,'inserted':inserted,'retry_inserts':retries,'checked_queries':len(checks)*2,'restart_equal':True,
            'gap_query':gap,'streams':{stream:{'rows':sum(o.stream_id==stream for o in observations),'mode':next(o.mode for o in observations if o.stream_id==stream)} for stream in sorted({o.stream_id for o in observations})},
            'clock_policy':f'Simulated commitment = source/result availability + {commit_delay_us}us; not live measured latency.',
            'coverage_policy':'Exact sampled timestamps only; no continuous state, expiry, revisions, or carry-forward.',
            'state_handoff_sha256':file_hash(Path(state_handoff)/'manifest.json'),'classical_comparison_sha256':file_hash(classical_comparison),
            'artifacts':{name:file_hash(dest/name) for name in ('observations.jsonl','queries.json','observations.sqlite')},
            'code_sha256':{name:file_hash(Path(__file__).parent/name) for name in ('store.py','replay.py')}}
    write_json(dest/'manifest.json',report);return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('state_handoff');parser.add_argument('classical_comparison');parser.add_argument('destination');args=parser.parse_args()
    print(json.dumps(run(args.state_handoff,args.classical_comparison,args.destination),indent=2))
