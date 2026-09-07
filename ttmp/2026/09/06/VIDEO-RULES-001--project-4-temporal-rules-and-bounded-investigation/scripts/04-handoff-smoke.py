"""One completed-feature smoke: actual packets plus injected parser answers."""
from pathlib import Path
from dataclasses import asdict
import json
import sqlite3
from PIL import Image,ImageDraw
from video_workbench.rules.evaluate import Event,digest
from video_workbench.rules.stored import evaluate_stored
from video_workbench.rules.handoff import plan_request,evaluate_answer
from video_workbench.verifiers.contracts import validate_request,parse_answer
from video_workbench.registry import file_hash

root=Path(__file__).resolve().parents[1];out=root/'various/r3-handoff';out.mkdir(exist_ok=True)
samples=json.load(open('output/localization-v1/dataset/samples.json'));by={(s['episode_id'],s['requested_entity'],s['pts_us']):s for s in samples}
source=Path('output/temporal-v1/replay-v1/observations.sqlite');con=sqlite3.connect(source)
rows=[json.loads(r[0]) for r in con.execute("SELECT payload FROM observations WHERE stream_id LIKE 'state/%' ORDER BY observation_id")];con.close()
packets={};plans=[];first=None
for r in rows:
    if r['value'] is not None:continue
    s=by[r['episode_id'],r['entity'],r['event_us']]
    assert file_hash(s['image'])==s['image_sha256']
    e=Event('sample/'+r['observation_id'],r['episode_id'],r['entity'],'frame-sample','sample',r['event_us'],r['event_us'],r['event_us'],r['event_us'])
    rule={'schema_version':1,'rule_id':'closed-at-sampled-frame','op':'state_at_event','event_stream':'frame-sample','event_id':e.id,'state_stream':r['stream_id'],'property':'door_open','expected':False}
    baseline=evaluate_stored(source,r['run_id'],rule,r['episode_id'],r['entity'],[e],r['committed_us'])
    frames=[{'id':s['sample_id'],'episode_id':r['episode_id'],'entity_id':r['entity'],'pts_us':r['event_us'],'available_us':r['event_us'],'path':str(Path(s['image']).resolve()),'sha256':s['image_sha256']}]
    plan=plan_request(rule,baseline,e,frames,s['requested_class']);assert plan['status']=='ready'
    packets[plan['request']['request_id']]=plan['request'];plans.append(plan)
    if first is None:first=(r,e,rule,baseline,plan['request'])
r,e,rule,baseline,request=first;initial=json.dumps(baseline,sort_keys=True);results=[]
for answer,status in [('true','VIOLATION'),('false','PASS'),('unknown','UNKNOWN')]:
    raw=json.dumps({'request_id':request['request_id'],'entity_id':r['entity'],'answer':answer,'evidence_ids':[request['frames'][0]['id']],'rationale':'Injected contract fixture, not a model answer.'})
    result=evaluate_answer(rule,baseline,e,request,raw,r['run_id'],'injected-fixture',r['committed_us']+1000000)
    assert result['decision']['status']==status
    result['observation']=asdict(result['observation']);results.append(result)
assert json.dumps(baseline,sort_keys=True)==initial
for raw in ('not json',json.dumps({'request_id':request['request_id'],'entity_id':r['entity'],'answer':'true','evidence_ids':['invented'],'rationale':'bad'}),' {"answer":"true","answer":"false"} '):assert parse_answer(request,raw)['status']=='invalid'
missing=dict(baseline,reason='trigger_not_observed');assert plan_request(rule,missing,None,request['frames'],'fridge')['status']=='unavailable'
bad=dict(request,frames=[dict(request['frames'][0],pts_us=request['event_us']+1)]);bad['request_id']=digest({k:v for k,v in bad.items() if k!='request_id'})
try:validate_request(bad)
except ValueError:pass
else:raise AssertionError('future frame accepted')
(out/'requests.json').write_text(json.dumps(list(packets.values()),indent=2)+'\n')
(out/'answer-fixtures.json').write_text(json.dumps(results,indent=2)+'\n')
summary={'unknown_decisions':len(plans),'unique_requests':len(packets),'actual_model_calls':0,'injected_answer_cases':3,'invalid_response_cases':3,'future_packet_rejected':True,'missing_trigger_not_queried':True,'baseline_unchanged':True,'scope':'Full-frame verifier proposals for sparse point states; no procedural accuracy claim.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
image=Image.new('RGB',(1000,260),'white');d=ImageDraw.Draw(image)
d.text((15,15),'RULES handoff: actual requests, injected answers only',fill='black')
d.text((15,45),f'{len(plans)} unknown crop decisions -> {len(packets)} unique exact-frame requests -> 0 actual model calls',fill='black')
for i,x in enumerate(results):d.text((15,85+i*35),f'Injected {x["observation"]["value"]}: separate verifier condition = {x["decision"]["status"]}; original UNKNOWN is preserved',fill='black')
d.text((15,220),'Missing trigger: no request. Future frame or invented citation: rejected. No replacement or automatic retry.',fill='black')
image.save(out/'handoff-trace.png');print(json.dumps(summary,indent=2))
