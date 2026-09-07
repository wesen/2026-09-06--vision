"""Run explicit final feature smoke through the real local HTTP API."""
import json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8780'
def api(path,body=None):
    r=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=30) as response:return json.load(response)
def run(options):
    result=api('/v1/lab/runs',options);rid=result['run_id']
    while True:
        r=api('/v1/lab/runs/'+rid)
        if r['status'] not in ('running','preparing'):break
        time.sleep(.3)
    assert r['status']=='completed',r
    return r
if __name__=='__main__':
    sources=api('/v1/lab/catalog')['sources'];source=next(s for s in sources if s['dataset']=='paired-actions-v4' and s['split']=='test')
    base=dict(episode_id=source['episode_id'],start_us=0,end_us=1000000,fps=10,component='tracking',model='yolo11n')
    track=run(base)
    action=api('/v1/lab/actions/inspect',dict(episode_id=source['episode_id'],start_us=0,end_us=2000000,fps=2,crop=None))
    assert action['records'],action
    rule=api('/v1/lab/runs/run-fc7db205cb284dcd/rule',dict(event_us=9000000,expected_open=False))
    missing=api('/v1/lab/runs/run-fc7db205cb284dcd/rule',dict(event_us=9100000,expected_open=False))
    assert missing['decision']['status']=='UNKNOWN'
    review=api('/v1/lab/runs/'+track['run_id']+'/reviews',dict(verdict='unjudgeable',note='Automated UI smoke annotation: verifies persistence only, not a human accuracy judgment.'))
    exported=api('/v1/lab/runs/'+track['run_id']+'/export')
    assert exported['reviews'][0]['review_id']==review['review_id']
    assert exported['reviews'][0]['source']['split']=='test'
    comparison=api('/v1/lab/compare?a=run-c91ef4d1a5c54ed9&b=run-cb3fcc4c7afa4e55')
    assert comparison['same_evidence'] and not comparison['same_feature_space']
    output=dict(tracking_run=track['run_id'],tracking_records=len(track['result']['records']),saved_action_rows=len(action['records']),exact_rule=rule['decision']['status'],missing_rule=missing['decision']['status'],review_id=review['review_id'],comparison=comparison)
    (ROOT/'various/final-api-smoke.json').write_text(json.dumps(output,indent=2)+'\n')
    (ROOT/'various/openapi.json').write_text(json.dumps(api('/openapi.json'),indent=2)+'\n')
    print(json.dumps(output,indent=2))
