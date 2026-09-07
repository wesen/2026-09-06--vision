"""Score frozen population, including misses; retain exact per-event evidence."""
from pathlib import Path
import json,statistics
from video_workbench.registry import file_hash
from video_workbench.rules.measurement import measure
root=Path(__file__).resolve().parents[1];review=root/'various/r4-review';out=Path('output/rules-departure-v1')
records=json.loads((review/'recordings.json').read_text());by_id={r['episode_id']:r for r in records}
references=json.loads((review/'reviewed-events.json').read_text())
for r in references:r['event_us']=by_id[r['episode_id']]['pts_us'][r['frame_index']]
run=json.loads((out/'run.json').read_text())
assert file_hash(review/'protocol.json')==run['protocol_sha256']
assert file_hash(review/'recordings.json')==run['recordings_sha256']
candidates=[];decisions={k:{} for k in ['baseline','qwen','cosmos']};traces=[]
for row in records:
    dest=out/row['episode_id'];summary=json.loads((dest/'complete.json').read_text())
    assert file_hash(dest/'frames.jsonl')==summary['frames_sha256']
    candidates.extend(summary['candidates'])
    for c in summary['candidates']:
        packet=json.loads((dest/(c['event_id']+'-packet.json')).read_text())
        decisions['baseline'][c['event_id']]=packet['baseline']['status']
        trace=dict(candidate=c,split=row['split'],baseline=packet['baseline'],frame=packet['frame'],models={})
        for family in ('qwen','cosmos'):
            result=json.loads((dest/(c['event_id']+'-'+family+'-handoff.json')).read_text())
            verifier=result.get('verifier',{});runtime=verifier.get('runtime',{})
            status=result.get('conditioned',{}).get('decision',{}).get('status',packet['baseline']['status'] if result['status']=='not_needed' else 'UNKNOWN')
            decisions[family][c['event_id']]=status
            trace['models'][family]=dict(decision=status,runtime_status=result['status'],request_id=verifier.get('request_id'),answer=verifier.get('answer'),elapsed_seconds=verifier.get('elapsed_seconds'),prompt_tokens=runtime.get('prompt_tokens'),generation_tokens=runtime.get('generation_tokens'),peak_mlx_bytes=runtime.get('peak_mlx_bytes'),profile_sha256=verifier.get('profile_sha256'))
        traces.append(trace)
report=dict(protocol_sha256=run['protocol_sha256'],reviewed_events_sha256=file_hash(review/'reviewed-events.json'),detector=run['detector'],splits={},traces=traces)
for split in ('development','test','all'):
    eps={r['episode_id'] for r in records if split=='all' or r['split']==split}
    refs=[r for r in references if r['episode_id'] in eps];preds=[r for r in candidates if r['episode_id'] in eps]
    duration=sum(r['duration_us'] for r in records if r['episode_id'] in eps)
    report['splits'][split]={}
    for family in decisions:
        metrics=measure(refs,preds,{p['event_id']:decisions[family][p['event_id']] for p in preds},duration)
        if family!='baseline':
            costs=[t['models'][family] for t in traces if t['candidate']['episode_id'] in eps]
            elapsed=[c['elapsed_seconds'] for c in costs if c['elapsed_seconds'] is not None]
            metrics['cost']=dict(requests=len(elapsed),total_wall_seconds=sum(elapsed),median_wall_seconds=statistics.median(elapsed) if elapsed else None,max_wall_seconds=max(elapsed) if elapsed else None,prompt_tokens=sum(c['prompt_tokens'] or 0 for c in costs),generation_tokens=sum(c['generation_tokens'] or 0 for c in costs),peak_mlx_bytes=max((c['peak_mlx_bytes'] or 0 for c in costs),default=0))
        report['splits'][split][family]=metrics
(out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'various/r4-measurement.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['splits'],indent=2))
