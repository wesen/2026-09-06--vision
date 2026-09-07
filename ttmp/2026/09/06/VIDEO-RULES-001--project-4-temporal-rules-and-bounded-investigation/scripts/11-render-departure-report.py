"""Render actual approved evidence and measured outcomes for the report."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];m=json.loads((root/'various/r4-measurement.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',18)
small=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',15)
canvas=Image.new('RGB',(1120,1590),'#f4f2eb');draw=ImageDraw.Draw(canvas)
draw.text((20,12),'CAMERA DEPARTURE / RGB EVIDENCE AND RULE DECISIONS',font=font,fill='#121820')
examples=[('ep-7d3106fb1cac9776','OPEN FRIDGE / MISSED VIOLATION'),('ep-c1c313b64f579794','OPEN MICROWAVE / DETECTED'),('ep-205a311600c89bf7','CLOSED FRIDGE / CORRECT PASS')]
for n,(eid,title) in enumerate(examples):
    t=next(t for t in m['traces'] if t['candidate']['episode_id']==eid);y=55+n*510
    canvas.paste(Image.open(t['frame']['path']).convert('RGB'),(12,y))
    x=670;draw.text((x,y+8),title,font=small,fill='#121820')
    lines=[eid,'',f"Candidate: {t['candidate']['event_us']/1e6:.1f}s",f"Available: {t['candidate']['available_us']/1e6:.1f}s",'',f"Stored baseline: {t['baseline']['status']}"]
    for family in ('qwen','cosmos'):
        r=t['models'][family];lines.extend(['',f"{family.upper()}: {r['decision']}",f"Call: {r['elapsed_seconds']:.2f}s",f"Answer: {r['answer']['answer']}"])
    for i,line in enumerate(lines):draw.text((x,y+45+i*24),line,font=small,fill='#121820')
canvas.save(root/'various/r4-evidence-comparison.png')
