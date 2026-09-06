"""Render actual frozen measurements as an HTML page for a report screenshot."""
from pathlib import Path
from html import escape
import json

TICKET=Path(__file__).resolve().parent.parent
DATA=TICKET/'various/evaluation'
dev=json.loads((DATA/'development.json').read_text())
test=json.loads((DATA/'test-report.json').read_text())
serve=json.loads((DATA/'serving-index.json').read_text())
def pct(x):return '—' if x is None else f'{100*x:.2f}%'
rows=''.join(f"<tr><td>{c['configuration']['seconds']}s / {c['configuration']['fps']} FPS</td><td>{pct(c['evaluation']['metrics']['5']['success'])}</td><td>{pct(c['evaluation']['metrics']['5']['interval_recall'])}</td><td>{c['evaluation']['metrics']['5']['best_iou']:.3f}</td></tr>" for c in dev['candidates'])
qrows=''.join(f"<tr><td>{escape(q['query'])}</td><td>{pct(q['metrics']['5']['success'])}</td><td>{pct(q['metrics']['5']['interval_recall'])}</td><td>{q['top_score']:.3f}</td></tr>" for q in test['evaluation']['queries'])
html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Frozen retrieval evaluation</title>
<style>body{{font:16px system-ui;background:#f1f0e9;color:#19242a;margin:0}}main{{max-width:1100px;margin:30px auto;padding:30px;background:white;border-top:12px solid #2a6550}}h1{{font-size:34px;margin:8px 0}}small{{letter-spacing:.15em}}.facts{{display:flex;gap:30px;padding:20px;background:#e5eee6}}.facts strong{{font-size:28px;display:block}}table{{width:100%;border-collapse:collapse;margin:15px 0 30px}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #c4cac3}}.note{{background:#fff1d4;border-left:5px solid #bd872e;padding:18px;line-height:1.5}}footer{{font-size:12px;color:#53665d;overflow-wrap:anywhere}}</style>
<main><small>VIDEO-SEARCH-001 / FROZEN EVALUATION</small><h1>Coarse candidates, weak localization.</h1><p>Qwen3-VL-Embedding 2B · MLX 4-bit · explicitly pooled images · one VirtualHome apartment</p>
<div class="facts"><div><strong>10s / 1 FPS</strong>development-selected setting</div><div><strong>75%</strong>test Success@5</div><div><strong>68.75%</strong>test interval Recall@5</div><div><strong>0.095</strong>test best IoU@5</div></div>
<p class="note"><b>Interpretation:</b> Random ranking reached {pct(test['evaluation']['random_success_at_5'])} Success@5. Long windows and a tiny candidate pool make query success easy. Four positive query families and weak interiors do not establish reliable action localization or generalization.</p>
<h2>Development sweep — group g03</h2><table><tr><th>Window / sampling</th><th>Success@5</th><th>Interval Recall@5</th><th>Best IoU@5</th></tr>{rows}</table>
<h2>Held-out results — group g04, evaluated once</h2><table><tr><th>Query</th><th>Success@5</th><th>Interval Recall@5</th><th>Top cosine</th></tr>{qrows}</table>
<p>Negative controls remain in the report. Their positive-recall metrics are undefined; search still returns candidates. No abstention threshold was fitted.</p>
<footer>Serving index: {serve['index_id']} · {serve['chunks']} windows / 24 videos · {serve['feature_bytes']:,} matrix bytes<br>Measured MLX peak: {test['mlx_peak_bytes']/1e9:.2f} GB. Mean-pooled frames discard order. Source: committed protocol and evaluation JSON.</footer></main></html>'''
p=TICKET/'various/evaluation-summary.html';p.write_text(html);print(p)
