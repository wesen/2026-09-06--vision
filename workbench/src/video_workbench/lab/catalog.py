"""Explicit local capabilities and label-free source discovery."""
from pathlib import Path
import json
from video_workbench.media import probe
from video_workbench.registry import file_hash

ROOT = Path(__file__).resolve().parents[4]
MODELS = {
    'yolo11n': ('perception', 'workbench/perception-env/.venv/bin/python', 'output/models/yolo11/yolo11n.pt'),
    'yolo11n-seg': ('perception', 'workbench/perception-env/.venv/bin/python', 'output/models/yolo11/yolo11n-seg.pt'),
    'qwen': ('reasoning', 'workbench/verify-env/.venv/bin/python', 'output/models/qwen3-vl-instruct-8b-8bit'),
    'cosmos': ('reasoning', 'workbench/verify-env/.venv/bin/python', 'output/models/cosmos-reason2-8b-8bit-local'),
    'pooled_images': ('embeddings', 'workbench/.venv/bin/python', 'output/models/qwen3-vl-embedding-2b-4bit'),
    'native_video': ('embeddings', 'output/mlx-video-fix/.venv/bin/python', 'output/mlx-video-fix/models/official'),
}

class Catalog:
    def __init__(self, root=ROOT):
        self.root=Path(root); self.sources={}; self.media={}
        # Manifest inputs contain model-safe identities, never scenario labels.
        for manifest in sorted((self.root/'output/virtualhome-corpus').glob('*/inputs.jsonl')):
            for line in manifest.read_text().splitlines():
                if not line.strip(): continue
                row=json.loads(line); video=(manifest.parent/row['video']).resolve()
                if not video.is_relative_to(manifest.parent.resolve()) or not video.is_file(): continue
                eid=manifest.parent.name+'--'+row['episode_id']
                source={k:row[k] for k in ('episode_id','split','split_group','video_sha256')}
                source.update(episode_id=eid,original_episode_id=row['episode_id'],video=str(video),dataset=manifest.parent.name)
                if eid in self.sources and self.sources[eid]['video_sha256'] != source['video_sha256']:
                    raise ValueError('conflicting source identity')
                self.sources[eid]=source

    def get(self,eid):
        if eid not in self.sources: raise ValueError('unknown registered source')
        source=dict(self.sources[eid]); path=Path(source['video'])
        if file_hash(path)!=source['video_sha256']: raise ValueError('registered source bytes changed')
        if eid not in self.media: self.media[eid]=probe(path)
        return dict(source,media=self.media[eid])

    def public(self):
        return [{k:v for k,v in s.items() if k!='video'} for s in self.sources.values()]

    def capabilities(self):
        return [dict(id=key,kind=kind,available=(self.root/python).is_file() and (self.root/model).exists(),
                     runtime=python,checkpoint=model)
                for key,(kind,python,model) in MODELS.items()]
