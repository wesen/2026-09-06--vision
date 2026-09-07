"""Bounded local single-image execution; failures never become negative answers."""
from pathlib import Path
import json
import os
import signal
import subprocess
import time
from PIL import Image
from video_workbench.registry import file_hash
from .contracts import validate_request
from .profiles import validate_profile, profile_hash, CONTRACT_VERSION
from .visibility import parse_visibility, prompt, SCHEMA_VERSION, experiment_prompt, parse_experiment
from .recovery import parse_with_recovery, RECOVERY_VERSION


def check_packet(request):
    validate_request(request)
    if len(request['frames']) != 1:
        raise ValueError('only single_image is accepted; multi-image/native-video remain unsupported')
    frame=request['frames'][0];path=Path(frame['path'])
    if not path.is_file() or path.stat().st_size > 10*1024*1024:
        raise ValueError('image missing or exceeds 10 MiB')
    if file_hash(path)!=frame['sha256']:
        raise ValueError('approved image bytes changed')
    with Image.open(path) as image:
        if image.width*image.height>1920*1080:
            raise ValueError('image exceeds 2073600 pixels')
        image.verify()


def supervise(command, deadline_seconds, log_path, env=None):
    """Kill and reap the entire worker group when the wall-clock budget expires."""
    started=time.monotonic()
    with Path(log_path).open('wb') as log:
        try:
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
        except OSError as exc:
            return dict(status='runtime_error',reason=str(exc),elapsed_seconds=time.monotonic()-started)
        try:
            code=process.wait(timeout=max(0,deadline_seconds))
            status='ok' if code==0 else 'runtime_error'
        except subprocess.TimeoutExpired:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            code=process.wait();status='timeout'
        except BaseException:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait();raise
    return dict(status=status,returncode=code,elapsed_seconds=time.monotonic()-started)


def verify(request, model_path, destination, *, python=None, variant='visibility', profile=None, recover_missing_close=True):
    """Run one bounded request; profiled calls allow traced wrapper recovery.

    Set recover_missing_close=False for strict experimental output validation.
    Recovery never modifies answer contents or relaxes evidence validation.
    """
    started=time.monotonic();check_packet(request)
    if profile is not None:
        # Snapshot caller-owned profile before worker launch.
        profile=json.loads(json.dumps(validate_profile(profile,request)))
    text=experiment_prompt(request,profile) if profile is not None else prompt(request,variant)
    model_path=Path(model_path).absolute()
    if not (model_path/'config.json').is_file():raise ValueError('local model config required')
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
    request_path=destination/'request.json';result_path=destination/'worker-result.json'
    request_path.write_text(json.dumps(request,indent=2)+'\n')
    python=python or str(Path('workbench/verify-env/.venv/bin/python').absolute())
    command=[python,'-m','video_workbench.verifiers.worker',str(model_path),str(request_path.absolute()),str(result_path.absolute()),variant]
    if profile is not None:
        profile_path=destination/'profile.json'
        profile_path.write_text(json.dumps(profile,indent=2)+'\n')
        command.extend(['--profile',str(profile_path.absolute())])
    env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    remaining=request['deadline_ms']/1000-(time.monotonic()-started)
    execution=supervise(command,remaining,destination/'worker.log',env)
    elapsed=time.monotonic()-started
    result=dict(execution,request_id=request['request_id'],entity_id=request['entity_id'],schema_version=SCHEMA_VERSION,mode='single_image',prompt=text,model_path=str(model_path),elapsed_seconds=elapsed,completed_us=request['as_of_us']+int(elapsed*1e6)+1)
    if profile is not None:
        result.update(profile=profile,profile_sha256=profile_hash(profile),schema_version=CONTRACT_VERSION,
                      validation_policy=RECOVERY_VERSION if recover_missing_close else 'strict-reasoning-envelope-v1')
    if execution['status']=='ok':
        try:
            if result_path.stat().st_size>(1024*1024 if profile is not None else 100000):raise ValueError('worker result too large')
            record=json.loads(result_path.read_text())
            if record['request_id']!=request['request_id']:raise ValueError('worker binding mismatch')
            # Recheck evidence after execution to detect unexpected source changes.
            check_packet(request)
            if profile is not None:
                if record.get('profile_sha256')!=profile_hash(profile) or record.get('profile')!=profile:
                    raise ValueError('worker profile binding mismatch')
                parser=parse_with_recovery if recover_missing_close else parse_experiment
                result.update(parser(request,record['raw'],profile,record.get('finish_reason')))
                result.update(profile=profile,profile_sha256=profile_hash(profile),schema_version=CONTRACT_VERSION)
            else:
                result.update(parse_visibility(request,record['raw']))
            result['runtime']=record
        except (OSError,ValueError,KeyError,TypeError) as exc:
            result.update(status='runtime_error',reason=str(exc))
    (destination/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
