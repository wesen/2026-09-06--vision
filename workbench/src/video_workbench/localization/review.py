"""Render source-bound manual rectangles for a second visual review pass."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

from video_workbench.index import write_json
from video_workbench.registry import file_hash
from .annotations import validate_review


def render_overlays(dataset, reviews_path, destination):
    samples_path = Path(dataset) / 'samples.json'
    samples = json.loads(samples_path.read_text())
    reviews = json.loads(Path(reviews_path).read_text())
    by_id = {r['sample_id']: r for r in reviews}
    sample_ids = {s['sample_id'] for s in samples}
    if len(by_id) != len(reviews) or len(sample_ids) != len(samples):
        raise ValueError('duplicate sample/review identity')
    if set(by_id) != sample_ids:
        raise ValueError('reviews must cover exactly the source population')
    groups = {}
    for sample in samples:
        validate_review(sample, by_id[sample['sample_id']])
        groups.setdefault(sample['episode_id'], []).append(sample)
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    index = []
    for ordinal, (episode, rows) in enumerate(groups.items()):
        rows.sort(key=lambda s: s['frame_index'])
        width = max(s['width'] for s in rows)
        height = max(s['height'] for s in rows) + 50
        canvas = Image.new('RGB', (2 * width, height * ((len(rows) + 1) // 2)), 'white')
        draw = ImageDraw.Draw(canvas)
        for i, sample in enumerate(rows):
            review = by_id[sample['sample_id']]
            x, y = i % 2 * width, i // 2 * height
            with Image.open(sample['image']) as source:
                if source.size != (sample['width'], sample['height']):
                    raise ValueError('source dimensions changed')
                canvas.paste(source.convert('RGB'), (x, y))
            rect = review['visible_xyxy']
            if rect is not None:
                x0, y0, x1, y1 = rect
                color = '#ff9900' if review['occluded'] else '#00ff00'
                draw.rectangle((x+x0, y+y0, x+x1-1, y+y1-1), outline=color, width=2)
            draw.text((x+4, y+height-47), f"{sample['sample_id']} / {sample['requested_class']} / frame {sample['frame_index']}", fill='black')
            draw.text((x+4, y+height-27), f"{review['visibility']} / truncated={review['truncated']}", fill='black')
        path = dest / f'overlay-{ordinal:02d}.jpg'
        canvas.save(path, quality=96)
        index.append({'episode_id': episode, 'sheet': path.name, 'sha256': file_hash(path), 'sample_ids': [s['sample_id'] for s in rows]})
    manifest = {'samples_sha256': file_hash(samples_path), 'reviews_sha256': file_hash(reviews_path), 'targets': len(samples), 'sheets': index, 'status': 'rendered for visual review; rendering does not certify annotation quality'}
    write_json(dest / 'manifest.json', manifest)
    return manifest
