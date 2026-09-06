#!/usr/bin/env python3
"""Fresh-process native adapter validation and isolated development subset build."""
from datetime import datetime,timezone
from pathlib import Path
import json,resource,time
import numpy as np
from PIL import Image
from video_workbench.native_video import NativeVideoEmbedder
from video_workbench.native_index import build_native
from video_workbench.index import Index
from video_workbench.registry import Registry
root=Path(__file__).resolve().parents[1]
started=time.perf_counter();encoder=NativeVideoEmbedder();loaded=time.perf_counter()-started
encoder.mx.reset_peak_memory()
frames=[Image.fromarray(a) for a in np.load('output/mlx-video-fix/probes/fixture.npz')['frames']]
started=time.perf_counter();video=encoder.video(frames,[0,400000,800000,1200000]);cold=time.perf_counter()-started
ref=np.load('output/mlx-video-fix/audit/video-hf-mlx.npz')['embedding'][0]
assert np.max(np.abs(video-ref))<1e-4
warm=[]
for _ in range(3):
 started=time.perf_counter();again=encoder.video(frames,[0,400000,800000,1200000]);warm.append(time.perf_counter()-started)
 assert np.array_equal(video,again)
# New long-lived adapter must match reference after video -> text -> odd/single.
checks={}
for name,call in [('text',lambda:encoder.text('A person closing the fridge door.')),
                  ('video1',lambda:encoder.video(frames[:1],[0])),
                  ('video3',lambda:encoder.video(frames[:3],[0,400000,800000]))]:
 actual=call();expected=np.load(f'output/mlx-video-fix/audit/{name}-hf-mlx.npz')['embedding'][0]
 checks[name]=float(np.max(np.abs(actual-expected)));assert checks[name]<1e-4
import sqlite3
registry=Registry.__new__(Registry)
registry.db=sqlite3.connect('file:output/video-workbench/registry.sqlite?mode=ro',uri=True)
registry.db.row_factory=sqlite3.Row
# Read-only access to parent registry; no ingest or corpus mutations.
class Subset:
 def episodes(self):
  return [e for e in registry.episodes('development') if e['episode_id']=='ep-368d6331fc690a2c']
subset=Subset();assert len(subset.episodes())==1
build_root='output/mlx-video-fix/workbench-native-smoke'
built=build_native(subset,encoder,build_root,seconds=2,fps=2,splits=('development',))
reused=build_native(subset,encoder,build_root,seconds=2,fps=2,splits=('development',))
assert reused['fresh_clips']==0 and built['index_id']==reused['index_id']
hits=Index(built['manifest'],encoder.space.id).search(encoder.text('A person closing the fridge door.'),encoder.space.id,k=3,split='development')
registry.close()
report={'created_at':datetime.now(timezone.utc).isoformat(),'load_materialized_seconds':loaded,'cold_first_inference_including_processor_seconds':cold,'warm_including_processor_seconds':warm,
        'fixture_max_abs':float(np.max(np.abs(video-ref))),'mixed_order_reference_max_abs':checks,'space_id':encoder.space.id,
        'build':built,'reuse':reused,'hits':hits,'mlx_peak_bytes':encoder.mx.get_peak_memory(),'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'Fresh process, warm filesystem cache; one development episode, separate output root; peaks include subset build.'}
(root/'various/native-integration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
