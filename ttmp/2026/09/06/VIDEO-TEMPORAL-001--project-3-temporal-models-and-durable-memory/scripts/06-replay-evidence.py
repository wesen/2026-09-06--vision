"""Save a compact actual replay trail and diagram for the memory report."""
from pathlib import Path
import json
import shutil
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];out=root/'various/replay-v1';out.mkdir(exist_ok=True)
cache=Path('output/temporal-v1/replay-v1')
shutil.copy2(cache/'manifest.json',out/'manifest.json')
rows=[json.loads(l) for l in (cache/'observations.jsonl').read_text().splitlines()]
queries=json.loads((cache/'queries.json').read_text())
linear=next(r for r in rows if r['stream_id']=='action/linear')
smooth=next(r for r in rows if r['stream_id']=='action/smooth' and r['episode_id']==linear['episode_id'] and r['event_us']==linear['event_us'])
state=next(r for r in rows if r['stream_id']=='state/F__linear_head' and r['value'] is not None)
examples=[state,linear,smooth];ids={r['observation_id'] for r in examples}
(out/'examples.json').write_text(json.dumps({'observations':examples,'queries':[r for r in queries if any(i in ids for i in r['after']['observation_ids'])]},indent=2)+'\n')
image=Image.new('RGB',(1120,410),'white');d=ImageDraw.Draw(image)
d.text((15,14),'Replay visibility: an observation can describe an earlier time and arrive later',fill='black')
d.text((15,36),'Actual predictions; simulated 250 ms commit delay. Event circle / evidence availability square / durable commit triangle.',fill='black')
maximum=max(r['committed_us'] for r in examples)*1.1
for i,r in enumerate(examples):
    y=110+i*85;d.text((15,y-8),r['stream_id'],fill='black');d.line((205,y,1080,y),fill='#cccccc')
    pos=lambda t:205+int(860*t/maximum)
    e,a,c=map(pos,(r['event_us'],r['available_us'],r['committed_us']))
    d.ellipse((e-5,y-5,e+5,y+5),outline='#222222',width=2)
    d.rectangle((a-4,y-15,a+4,y-7),fill='#3478b8')
    d.polygon([(c,y+7),(c-5,y+16),(c+5,y+16)],fill='#db7939')
    d.text((205,y+25),f'event={r["event_us"]/1e6:.2f}s  available={r["available_us"]/1e6:.2f}s  commit={r["committed_us"]/1e6:.2f}s  value={r["value"]}',fill='black')
d.text((15,370),'Queries require an exact sample and both availability <= as-of and commitment <= as-of. No state is held through gaps.',fill='black')
image.save(out/'replay-clocks.png')
print(json.dumps({r['stream_id']:{k:r[k] for k in ('event_us','available_us','committed_us','value')} for r in examples},indent=2))
