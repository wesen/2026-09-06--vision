"""Isolated visibility worker. Only the host binds request/entity identities."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import time
from .adapter import check_packet
from .visibility import prompt


def run(model_path,request_path,result_path,variant):
    request=json.loads(Path(request_path).read_text());check_packet(request)
    import mlx.core as mx
    from mlx_vlm import load,generate
    from mlx_vlm.utils import load_config
    from mlx_vlm.prompt_utils import apply_chat_template
    started=time.monotonic();model,processor=load(model_path,trust_remote_code=False);loaded=time.monotonic()
    text=prompt(request,variant);formatted=apply_chat_template(processor,load_config(model_path),text,num_images=1)
    generated=generate(model,processor,formatted,image=[request['frames'][0]['path']],max_tokens=request['max_output_tokens'],temperature=0.0,verbose=False)
    record=dict(request_id=request['request_id'],raw=generated.text,prompt=text,formatted_prompt=formatted,mode='single_image',load_seconds=loaded-started,generation_seconds=time.monotonic()-loaded,peak_mlx_bytes=mx.get_peak_memory(),prompt_tokens=generated.prompt_tokens,generation_tokens=generated.generation_tokens,finish_reason=generated.finish_reason,versions={name:importlib.metadata.version(name) for name in ('mlx','mlx-vlm','transformers')})
    Path(result_path).write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('request');p.add_argument('result');p.add_argument('variant');a=p.parse_args();run(a.model,a.request,a.result,a.variant)
