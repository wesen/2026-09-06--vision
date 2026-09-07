"""Archive portable run evidence and outcome-specific latency from committed rows."""
from pathlib import Path
from collections import defaultdict
import json,sqlite3
from video_workbench.registry import file_hash
root=Path(__file__).resolve().parents[1];dest=root/'various/p4-measurements';dest.mkdir(exist_ok=True)
runs={'recorded_microwave':'replay-5e4499f558614b62','live_fridge':'replay-0adb49ee32254188','overload':'replay-ea4ed99ac2dc407a','browser_started':'replay-da07533583334f49'}
reports={}
for name,run_id in runs.items():
    source=Path('output/replay-workbench')/run_id
    summary=json.loads((source/'summary.json').read_text());assert summary['status']=='complete'
    config=json.loads((source/'config.json').read_text())
    con=sqlite3.connect((source/'replay.sqlite').resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    rows=[dict(r) for r in con.execute('SELECT * FROM records ORDER BY seq')];con.close()
    groups=defaultdict(list)
    for r in rows:
        r['payload']=json.loads(r['payload'])
        assert r['event_us']<=r['available_us']
        if r['kind']=='job':groups[r['payload']['job_kind']+'/'+r['payload']['status']].append(r['payload'])
    latency={}
    for key,jobs in groups.items():
        latency[key]={}
        for metric in ('queue_seconds','service_seconds','total_seconds'):
            values=sorted(j[metric] for j in jobs)
            latency[key][metric]=dict(count=len(values),p50=values[len(values)//2],p95=values[min(len(values)-1,int(.95*len(values)))],max=max(values))
    scheduler=summary['scheduler'];assert scheduler['high_jobs']<=scheduler['max_jobs'] and scheduler['high_bytes']<=scheduler['max_bytes']
    assert scheduler['counts']['submitted']==sum(scheduler['counts'].get(k,0) for k in ('completed','failed','dropped','expired','timeout','cancelled'))
    gaps=[r for r in rows if r['kind']=='gap'];cases=[r for r in rows if r['kind']=='candidate'];decisions=[r for r in rows if r['kind']=='decision']
    report=dict(config=config,summary=summary,latency_by_kind_and_outcome=latency,candidates=cases,decisions=decisions,gap_records=len(gaps),source_sqlite_sha256=file_hash(source/'replay.sqlite'))
    (dest/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    # Perception payloads can be reconstructed from the hash-bound source trace;
    # retain every job and gap plus rule/state evidence in a portable event log.
    with (dest/(name+'-events.jsonl')).open('w') as f:
        for r in rows:
            if r['kind']!='perception':f.write(json.dumps(r,separators=(',',':'))+'\n')
    reports[name]=dict(run_id=run_id,wall_seconds=summary['wall_seconds'],counts=summary['counts'],latency=latency,peak_host_and_worker_rss_bytes=summary['peak_host_and_worker_rss_bytes'])
print(json.dumps(reports,indent=2))
