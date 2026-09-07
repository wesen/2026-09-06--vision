"""Feature smoke: causal prefix, matching loss, unknowns, and immutable baseline."""
from pathlib import Path
import json
from video_workbench.rules.departure import DepartureDetector
from video_workbench.rules.measurement import match_events,measure

def event(i,t,open=True,episode='a'):
    return dict(event_id=i,event_us=t,door_open=open,episode_id=episode)

d=DepartureDetector('a');scores=[0,1,1,1,0,0,0,0,1,1,1,0,0,0]
outputs=[d.observe(str(i),i*100000,s) for i,s in enumerate(scores)]
assert [e['event_us'] for e in outputs if e]==[400000,1100000]
assert [e['available_us'] for e in outputs if e]==[600000,1300000]
for end in range(1,len(scores)+1):
    fresh=DepartureDetector('a')
    assert [fresh.observe(str(i),i*100000,s) for i,s in enumerate(scores[:end])]==outputs[:end]
try:d.observe('again',1300000,0)
except ValueError:pass
else:raise AssertionError('accepted backward/repeated PTS')
refs=[event('r1',0),event('r2',4),event('r3',20)]
preds=[event('p1',3),event('p2',7),event('p3',30)]
match=match_events(refs,preds,4)
assert match['pairs']==[('r1','p1'),('r2','p2')]
assert match['missed']==['r3'] and match['unmatched_candidates']==['p3']
m=measure(refs,preds,{'p1':'VIOLATION','p2':'UNKNOWN','p3':'VIOLATION'},3600000000,4)
assert m['violation_recall']==1/3 and m['missed_positive_events']==2
assert m['false_alerts_per_source_hour']==1 and m['unknown_fraction']==1/3
assert not match_events([event('r',1)], [event('p',1,episode='b')],4)['pairs']
assert measure([event('r',1)],[],{},1000000)['violation_recall']==0
assert measure([event('r',1,None)],[event('p',1)],{'p':'VIOLATION'},1000000)['unscorable_alerts']==1
root=Path('output/rules-departure-v1')
for packet in root.glob('*/*-packet.json'):
    p=json.loads(packet.read_text());before=p['baseline']
    assert before['as_of_us']==p['event']['available_us']
    for handoff in packet.parent.glob(p['event']['id']+'-*-handoff.json'):
        h=json.loads(handoff.read_text())
        assert h['source_evaluation_id']==before['evaluation_id']
        if h['status']=='ok':
            c=h['conditioned'];assert c['decision']['as_of_us']>=before['as_of_us']
            assert c['condition']=='separate_verifier_evidence'
    assert json.loads(packet.read_text())['baseline']==before
print('PASS: causal prefix, confirmation delay, rearming, ordering, optimal matching, missed positives, false alerts, unknowns, episode isolation, baseline preservation')
