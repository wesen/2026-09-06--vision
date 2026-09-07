"""Single-image local runtime gate. Run in a separately supervised subprocess."""
from pathlib import Path
from dataclasses import asdict,is_dataclass
import argparse
import importlib.metadata
import inspect
import json
import time
from video_workbench.registry import file_hash
from .contracts import validate_request,parse_answer


def run(model_path,request_path,output,model_bundle=None,*,allow_markdown_fence=True):
    request=json.loads(Path(request_path).read_text());validate_request(request)
    for frame in request['frames']:
        if file_hash(frame['path'])!=frame['sha256']:raise ValueError('approved image bytes changed')
    if len(request['frames'])!=1:raise ValueError('V1 gate is single-image only')
    import mlx.core as mx
    from mlx_vlm import load,generate
    from mlx_vlm.utils import load_config
    from mlx_vlm.prompt_utils import apply_chat_template
    started=time.perf_counter()
    model,processor=load(model_path,trust_remote_code=False) if model_bundle is None else model_bundle
    loaded=time.perf_counter()
    config=load_config(model_path)
    schema={'request_id':request['request_id'],'entity_id':request['entity_id'],'answer':'true|false|unknown','evidence_ids':[request['frames'][0]['id']],'rationale':'brief visible evidence only'}
    prompt=request['question']+'\nReturn only one JSON object with exactly this structure. Use one answer enum, not the pipe-separated string.\n'+json.dumps(schema)+'\nApproved frame ID: '+request['frames'][0]['id']
    formatted=apply_chat_template(processor,config,prompt,num_images=1)
    result=generate(model,processor,formatted,image=[request['frames'][0]['path']],max_tokens=request['max_output_tokens'],temperature=0.0,verbose=False)
    finished=time.perf_counter();raw=result.text
    report={'status':'generated','mode':'single_image','request_id':request['request_id'],'model_path':model_path,
            'model_reused':model_bundle is not None,'model_config_sha256':file_hash(Path(model_path)/'config.json'),'prompt':prompt,'formatted_prompt':formatted,
            'raw':raw,'parsed':parse_answer(request,raw,allow_markdown_fence=allow_markdown_fence),'load_seconds':loaded-started,'generation_seconds':finished-loaded,
            'peak_mlx_memory_bytes':mx.get_peak_memory(),
            'generation':asdict(result) if is_dataclass(result) else str(result),
            'versions':{n:importlib.metadata.version(n) for n in ('mlx','mlx-vlm','transformers','huggingface-hub')},
            'api_signatures':{n:str(inspect.signature(fn)) for n,fn in [('load',load),('generate',generate),('apply_chat_template',apply_chat_template)]},
            'image_sha256':request['frames'][0]['sha256'],'claim':'Runtime image smoke only; schema success is not factual acceptance.'}
    Path(output).write_text(json.dumps(report,indent=2,default=str)+'\n');print(json.dumps({k:report[k] for k in ('status','load_seconds','generation_seconds','peak_mlx_memory_bytes')}),flush=True)
    return model,processor


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('model');parser.add_argument('request');parser.add_argument('output');args=parser.parse_args();run(args.model,args.request,args.output)
