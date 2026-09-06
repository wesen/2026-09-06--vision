#!/usr/bin/env python3
"""Evaluate explicit P3 policy; export ranking, interventions, and performance."""
import json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
work=Path('output/mlx-video-fix/audit')
policy=json.loads((root/'various/audit-policy.json').read_text())
report=json.loads((root/'various/audit-comparison.json').read_text())
rows=report['comparisons']; fp=[r for r in rows if r['mode']=='mlx'];p=policy['fp32']
gates={r['case']:r['positions_equal'] and r['layers']['embedding']['cosine']>=p['embedding_min_cosine'] and r['layers']['embedding']['max_abs']<=p['embedding_max_abs'] and all(v['shape_equal'] and v['max_abs']<=p['intermediate_max_abs'] for k,v in r['layers'].items() if k!='embedding') for r in fp}
def vector(case,mode):
 a=np.load(work/f'{case}-hf-{mode}.npz')['embedding'].astype(float)[0]
 return a/np.linalg.norm(a)
candidates=['image','video','black','reverse','video1','video3','mixed']
rankings={};interventions={};performance={}
for mode in ['torch','mlx','bf16','quant','community']:
 q=vector('text',mode);scores={n:float(q@vector(n,mode)) for n in candidates}
 rankings[mode]={'scores':scores,'order':sorted(scores,key=lambda n:-scores[n])}
 interventions[mode]={'original_black_cosine':float(vector('video',mode)@vector('black',mode)),'original_reverse_cosine':float(vector('video',mode)@vector('reverse',mode))}
 runtime=json.loads((root/f'various/audit-{mode}.json').read_text());video=next(r for r in runtime['cases'] if r['case']=='video' and r['family']=='hf')
 performance[mode]={'load_materialized_seconds':runtime['load_materialized_seconds'],'video_first_seconds':video['first_seconds'],'video_warm_median_seconds':float(np.median(video['warm_seconds'])),'rss_peak_bytes':max(r['rss_peak_bytes'] for r in runtime['cases']),'mlx_peak_bytes':max((r.get('mlx_peak_bytes',0) for r in runtime['cases']),default=0)}
result={'created_at':report['created_at'],'fp32_gates':gates,'fp32_passed':len(gates)==8 and all(gates.values()),'rankings':rankings,'interventions':interventions,'performance':performance,'native_rollout_precision':'FP32 only','quantized_rollout_accepted':False,
 'policy':'audit-policy.json','limitations':['Eight development fixtures, one text query; not a retrieval benchmark.','First per-shape inference is not cold filesystem cache.','RSS and MLX peaks include untimed diagnostics.','Community checkpoint differences cannot all be attributed to quantization.']}
(root/'various/audit-gates.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert result['fp32_passed'],gates
