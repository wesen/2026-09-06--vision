"""Download exactly the checkpoint used by the pooled-image baseline.

Run from repository root with workbench/.venv/bin/python. No shared HF cache
or model config is edited; all downloaded assets live in ignored output/.
"""
from huggingface_hub import snapshot_download
from video_workbench.embedding import MODEL_ID, REVISION

print(snapshot_download(
    MODEL_ID, revision=REVISION,
    local_dir='output/models/qwen3-vl-embedding-2b-4bit',
    allow_patterns=['*.json','*.safetensors','*.jinja','*.txt','README.md'],
))
