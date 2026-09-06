#!/usr/bin/env python3
"""Build a local evaluator gallery and group inspection sheets from complete episodes."""
import argparse
from collections import defaultdict
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path('output/virtualhome-corpus/home-v1'))
args = parser.parse_args()
root = args.root.resolve()
groups = defaultdict(list)
rows = []
for item in json.loads((root / 'plan.json').read_text()):
    path = root / 'episodes' / item['episode_id'] / 'manifest.json'
    if not path.exists():
        continue
    m = json.loads(path.read_text())
    if m['status'] != 'complete':
        continue
    groups[m['split_group']].append(m)
    title = f"{m['episode_id']} / {m['split']} / {m['family']} / {m['variant']}"
    attempt = m['attempt']
    rows.append(f'<article><h2>{html.escape(title)}</h2>'
                f'<p>{m["frame_count"]} frames; {html.escape(m["rule_truth"]["verdict"])} (endpoint world truth)</p>'
                f'<video controls preload="none" width="640" src="{html.escape(m["video"])}"></video>'
                f'<p><a href="{html.escape(attempt)}/manifest.json">Manifest</a> · '
                f'<a href="{html.escape(attempt)}/annotations.json">Weak annotations</a></p>'
                f'<img loading="lazy" width="640" src="{html.escape(attempt)}/contact-sheet.jpg"></article>')
for group, episodes in groups.items():
    panels = []
    for m in episodes:
        with Image.open(root / m['attempt'] / 'contact-sheet.jpg') as source:
            panel = source.convert('RGB')
            panel.thumbnail((640, 900))
        panels.append((m, panel))
    row_height = max(panel.height for _, panel in panels) + 44
    sheet = Image.new('RGB', (1280, ((len(panels)+1)//2)*row_height), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, (m, panel) in enumerate(panels):
        x, y = (i % 2)*640, (i//2)*row_height
        draw.text((x+5,y+4), f"{group} / {m['family']} / {m['variant']}", fill='black')
        draw.text((x+5,y+22), m['episode_id'], fill='black')
        sheet.paste(panel, (x,y+44))
    sheet.save(root / f'inspection-{group}.jpg', quality=92)
(root / 'gallery.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<title>VirtualHome household corpus — evaluator gallery</title>
<style>body{font:16px system-ui;max-width:1300px;margin:2rem auto;background:#eee;color:#111}article{background:white;padding:1rem;margin:2rem 0}h2{font-size:18px}video,img{max-width:100%;vertical-align:top}</style>
<h1>Household corpus evaluator gallery</h1>
<p>This labeled gallery is for inspection, not model input. Action interiors are weak labels;
final verdicts are simulator endpoint truth. Precise boundaries and dense visual state supervision are unverified.</p>
''' + '\n'.join(rows) + '</html>')
print(json.dumps({'gallery': str(root/'gallery.html'), 'complete': len(rows), 'groups': list(groups)}))
