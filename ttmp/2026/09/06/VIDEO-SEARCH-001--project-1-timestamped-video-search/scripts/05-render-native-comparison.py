"""Render frozen metrics and actual sampled frames from each system's first hit."""
from pathlib import Path
from html import escape
import json
from video_workbench.registry import Registry,file_hash
from video_workbench.media import decode_selected
S=Path(__file__).resolve().parents[1];out=S/'various/native-pooled-v1'
reports={m:json.loads((out/(m+'.json')).read_text())['evaluation'] for m in ('native_video','pooled_images')}
rows=[]
for k in ('1','5','10'):
 for metric in ('success','interval_recall','best_iou'):
  rows.append('<tr><td>'+metric+' @ '+k+'</td>'+''.join(f'<td>{reports[m]["metrics"][k][metric]:.4f}</td>' for m in reports)+'</tr>')
html='''<!doctype html><meta charset="utf-8"><link rel="icon" href="data:,"><title>Native versus pooled / fixed development evidence</title><style>body{font:17px system-ui;background:#edf0ed;color:#19302c;margin:40px auto;max-width:1250px}h1{font-size:34px}section{background:white;border:1px solid #cad4ce;padding:24px;margin:22px 0}table{border-collapse:collapse;width:100%}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left}.frames{display:flex;gap:8px}.frames figure{margin:0;width:25%}img{width:100%}figcaption{font:12px monospace}.note{background:#fff0ca;padding:18px;line-height:1.5}code{font-size:13px}</style><p>VIDEO-SEARCH-001 / REPAIRED MLX</p><h1>Native video versus pooled images</h1><p>55 identical clips · six development videos · 2 seconds · 2 FPS · six fixed queries</p><p class="note">FP32 native versus 4-bit pooled is a system comparison. Source intervals and selected timestamps match exactly; precision and preprocessing differ. Weak program labels, one development group, no held-out evaluation.</p><section><h2>Four positive query families / macro metrics</h2><table><tr><th>Metric</th><th>Native FP32</th><th>Pooled 4-bit</th></tr>'''+''.join(rows)+'</table></section>'
registry=Registry('output/video-workbench/registry.sqlite');episodes={e['episode_id']:e for e in registry.episodes('development')}
for mode,report in reports.items():
 q=report['queries'][0];hit=q['hits'][0];ep=episodes[hit['episode_id']];assert file_hash(ep['video'])==ep['video_sha256']
 manifest=json.loads((out/(mode+'-manifest.json')).read_text());chunk=next(c for c in manifest['chunks'] if c['chunk_id']==hit['chunk_id']);ids=[ep['media']['pts_us'].index(t) for t in chunk['selected_pts_us']];images=decode_selected(ep['video'],ids)
 html+=f'<section><h2>{escape(mode)} / first result</h2><p>{escape(q["query"])}</p><p><code>{ep["episode_id"]} / {hit["start_us"]/1e6:.1f}–{hit["end_us"]/1e6:.1f}s</code></p><div class="frames">'
 for i in ids:
  name=f'{mode}-frame-{i}.png';images[i].save(out/name);html+=f'<figure><img src="{name}"><figcaption>PTS {ep["media"]["pts_us"][i]/1e6:.3f}s</figcaption></figure>'
 html+='</div><p>Actual sampled source frames. Retrieval rank is not an action annotation.</p></section>'
registry.close();html+='<section><h2>What changed</h2><p>Interval Recall@5: 0.2500 → 0.4375. Success@5 stays 0.5000. Both systems miss both microwave query families in the top five. Native success@10 rises from 0.50 to 0.75.</p><p>Unsupported queries still return hits. Raw cosine scores cannot be compared as calibrated probabilities across feature spaces.</p></section>'
(out/'comparison.html').write_text(html)
