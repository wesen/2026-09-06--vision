"""Archive the completed runtime gate and render its input/response audit figure."""
from pathlib import Path
import json
import shutil
import textwrap
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
source=Path('output/verifier-v1/image-gate')
out=root/'various/v1-image-gate';out.mkdir(parents=True,exist_ok=True)
for p in source.iterdir():
    if p.suffix in ('.json','.log'):shutil.copyfile(p,out/p.name)
request=json.loads((source/'request.json').read_text())
shutil.copyfile(request['frames'][0]['path'],out/'approved-frame.png')
lines=['V1 — one image, runtime smoke only','256 output tokens; identical question and image','']
for name in ['qwen3-vl-instruct-2b-8bit','cosmos-reason2-2b-8bit']:
    d=json.loads((out/(name+'.json')).read_text())
    lines += [name, f"JSON status: {d['parsed']['status']} | generated tokens: {d['generation']['generation_tokens']}",f"Load {d['load_seconds']:.2f}s | generation {d['generation_seconds']:.2f}s",f"Peak MLX: {d['peak_mlx_memory_bytes']/1e9:.3f} GB",'Raw response:',textwrap.fill(d['raw'],68),'']
lines += ['Cosmos code fences are rejected, not silently removed.','A valid citation is not proof of factual support.','No held-out accuracy claim follows from this example.']
canvas=Image.new('RGB',(1600,1000),'white');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',15)
source_image=Image.open(out/'approved-frame.png').convert('RGB')
source_image.thumbnail((730,800));canvas.paste(source_image,(20,70))
draw.text((20,20),'Exact approved frame | 12.700 s | microwave',font=font,fill='black')
draw.multiline_text((770,20),'\n'.join(lines),font=font,fill='black',spacing=5)
canvas.save(out/'runtime-audit.png')
print(out/'runtime-audit.png')
