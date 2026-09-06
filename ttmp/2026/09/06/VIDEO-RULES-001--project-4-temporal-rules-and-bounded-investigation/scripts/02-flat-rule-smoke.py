"""End-of-feature R1 oracle smoke and report figure; no model execution."""
from dataclasses import replace
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.rules.evaluate import Event,Coverage,evaluate,validate_rule
from video_workbench.temporal.store import Observation

rules=json.loads(Path('workbench/configs/rules/household-v1.json').read_text())['rules']
state,before,absent=rules
closed=Observation('closed-frame','run','state/F__linear_head','episode','microwave','door_open',False,7000000,7000000,7500000,('frame',),'producer','space','causal')
close=Event('close','episode','microwave','reviewed-events','CLOSE',5000000,5400000,5400000,5500000)
departure=Event('departure','episode','microwave','reviewed-events','departure',7000000,7000000,7000000,7000000)
cover=Coverage('coverage','episode','microwave','reviewed-events','OPEN',8000000,12000000,12000000,12000000,'oracle')
records=[]
def case(name,rule,status,reason,**kwargs):
    result=evaluate(rule,'episode','microwave',**kwargs)
    assert (result['status'],result['reason'])==(status,reason),(name,result)
    records.append({'case':name,'expected':status,'result':result})
case('missing departure does not pass',state,'UNKNOWN','trigger_not_observed',as_of_us=13000000)
case('closed sample at exact departure',state,'PASS','observed_state_match',events=[departure],observations=[closed],as_of_us=8000000)
case('state has not committed yet',state,'UNKNOWN','no_exact_state_sample',events=[departure],observations=[closed],as_of_us=7200000)
case('wrong appliance cannot satisfy rule',state,'UNKNOWN','no_exact_state_sample',events=[departure],observations=[replace(closed,entity='fridge')],as_of_us=8000000)
case('observed open at departure',state,'VIOLATION','observed_state_mismatch',events=[departure],observations=[replace(closed,value=True)],as_of_us=8000000)
case('uncertain departure cannot use nearby frame',state,'UNKNOWN','uncertain_trigger_requires_interval_evidence',events=[replace(departure,hi_us=7100000,available_us=7100000,committed_us=7100000)],observations=[closed],as_of_us=8000000)
case('close strictly before departure',before,'PASS','strictly_before',events=[close,departure],as_of_us=8000000)
case('equal timestamps are not before',before,'VIOLATION','not_strictly_before',events=[replace(close,lo_us=7000000,hi_us=7000000,available_us=7000000,committed_us=7000000),departure],as_of_us=8000000)
case('overlapping uncertainty stays unknown',before,'UNKNOWN','overlapping_event_uncertainty',events=[replace(close,lo_us=6900000,hi_us=7100000,available_us=7100000,committed_us=7100000),departure],as_of_us=8000000)
case('absence without coverage is unknown',absent,'UNKNOWN','event_coverage_gap',as_of_us=13000000)
case('covered absence passes',absent,'PASS','covered_event_absence',coverage=[cover],as_of_us=13000000)
case('future interval cannot pass',absent,'UNKNOWN','interval_not_finished',coverage=[cover],as_of_us=10000000)
case('coverage gap prevents absence',absent,'UNKNOWN','event_coverage_gap',coverage=[replace(cover,end_us=9000000),replace(cover,id='coverage2',start_us=10000000)],as_of_us=13000000)
opened=replace(departure,id='reopen',name='OPEN',lo_us=10000000,hi_us=10000000,available_us=10000000,committed_us=10000000)
case('observed reopening violates despite gaps',absent,'VIOLATION','prohibited_event_observed',events=[opened],as_of_us=11000000)
case('event at half-open end is outside',absent,'PASS','covered_event_absence',events=[replace(opened,lo_us=12000000,hi_us=12000000,available_us=12000000,committed_us=12000000)],coverage=[cover],as_of_us=13000000)
case('uncertain boundary event prevents pass',absent,'UNKNOWN','event_overlaps_interval_boundary',events=[replace(opened,lo_us=11900000,hi_us=12100000,available_us=12100000,committed_us=12100000)],coverage=[cover],as_of_us=13000000)
for bad in (dict(state,unexpected=True),dict(state,expected=0),dict(absent,end_us=absent['start_us'])):
    try:validate_rule(bad)
    except ValueError:pass
    else:raise AssertionError('invalid schema accepted')
root=Path(__file__).resolve().parents[1];out=root/'various/r1-oracle';out.mkdir(exist_ok=True)
(out/'results.json').write_text(json.dumps({'kind':'hand-derived numerical household oracle; no video quality claim','cases':records,'schema_rejections':3,'passed':True},indent=2)+'\n')
image=Image.new('RGB',(1200,80+len(records)*30),'white');d=ImageDraw.Draw(image)
d.text((15,12),'RULES R1: flat templates on hand-derived household evidence',fill='black')
d.text((15,34),'PASS = supported rule / VIOLATION = observed contradiction / UNKNOWN = evidence does not decide',fill='black')
for i,row in enumerate(records):
    y=65+i*30;r=row['result'];color={'PASS':'#268150','VIOLATION':'#b93632','UNKNOWN':'#987018'}[r['status']]
    d.text((15,y),row['case'],fill='black');d.text((380,y),r['status'],fill=color);d.text((490,y),r['reason'],fill='black')
image.save(out/'rule-outcomes.png')
print(f'{len(records)} oracle cases and 3 invalid schemas passed')
