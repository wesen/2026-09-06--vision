"""Run with workbench/.venv/bin/python; writes measured capability evidence."""
from pathlib import Path
import json, time, platform
import numpy as np
import av
from PIL import Image
from dataclasses import asdict
from video_workbench.embedding import QwenEmbedder
import psutil
started=time.perf_counter()
e=QwenEmbedder('output/models/qwen3-vl-embedding-2b-4bit')
load_seconds=time.perf_counter()-started
root=Path('output/virtualhome-corpus/home-v1')
row=json.loads((root/'inputs.jsonl').read_text().splitlines()[0])
with av.open(str(root/row['video'])) as c:
 frames=[f.to_image() for i,f in enumerate(c.decode(video=0)) if i in (20,30)]
text=e.text('A person opening the fridge door')
a=e.image(frames[0]);b=e.image(frames[1]); repeat=e.image(frames[0])
black=e.image(Image.new('RGB',(320,240),'black'))
try:e.video(frames)
except NotImplementedError as error:native=str(error)
report={'space':asdict(e.space),'space_id':e.space.id,'artifacts':e.artifacts,'load_seconds':load_seconds,
 'timings_seconds':e.timings,'shape':list(a.shape),'finite':bool(np.isfinite(a).all()),
 'norm':float(np.linalg.norm(a)), 'repeat_max_abs':float(np.max(np.abs(a-repeat))),
 'different_frame_cosine':float(a@b),'black_frame_cosine':float(a@black),
 'query_image_cosine':float(text@a),'native_video':{'supported':False,'reason':native},
 'rss_bytes':psutil.Process().memory_info().rss,'mlx_peak_bytes':e.mx.get_peak_memory(),
 'platform':platform.platform()}
p=Path('ttmp/2026/09/06/COSMOS-EMBED-001--embedding-runtime-baseline-on-mlx/various/runtime-smoke.json')
p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
