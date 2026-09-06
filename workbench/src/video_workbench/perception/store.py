"""Immutable successful runs, with failed attempts left inspectable."""
from pathlib import Path
import json
import os
from video_workbench.registry import file_hash


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.partial')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    os.replace(temp,path)


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def publish_episode(folder,manifest):
    folder=Path(folder)
    if (folder/'manifest.json').exists():
        raise ValueError('episode already published')
    manifest=dict(manifest,artifacts={p.name:file_hash(p) for p in sorted(folder.glob('*.jsonl'))})
    write_json(folder/'manifest.json',manifest)
    return manifest


def verify_episode(folder):
    folder=Path(folder)
    manifest=json.loads((folder/'manifest.json').read_text())
    for name,sha in manifest['artifacts'].items():
        p=(folder/name).resolve()
        if not p.is_relative_to(folder.resolve()) or file_hash(p)!=sha:
            raise ValueError('perception artifact changed')
    return manifest
