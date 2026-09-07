"""Loopback API for reproducible video experiments."""
from pathlib import Path
import json
import re
import uuid
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse
from .catalog import Catalog, ROOT
from .contracts import Selection, Experiment, Handoff
from .manager import Manager,write
from contextlib import asynccontextmanager
from .evidence import prepare
from .resources import Resources
from .analysis import Review,RuleRequest,compare,point_rule,action_artifacts
import time

def create_app(root=ROOT):
    root=Path(root); catalog=Catalog(root); output=root/'output/video-lab'; output.mkdir(exist_ok=True,parents=True)
    manager=Manager(catalog,output)
    @asynccontextmanager
    async def lifespan(app):
        yield
        manager.shutdown()
        replay.state.manager.shutdown()
    app=FastAPI(title='Video Laboratory',version='0.2',lifespan=lifespan)
    Resources(root).attach(app)
    app.state.catalog=catalog; app.state.output=output
    @app.get('/',response_class=HTMLResponse)
    def home(): return (Path(__file__).parent/'viewer.html').read_text()
    @app.get('/v1/lab/catalog')
    def capabilities(): return dict(sources=catalog.public(),models=catalog.capabilities(),max_samples=64)
    @app.get('/v1/lab/sources/{eid}')
    def source(eid:str):
        try: s=catalog.get(eid)
        except ValueError as e: raise HTTPException(409,str(e))
        return {k:v for k,v in s.items() if k!='video'}
    @app.get('/v1/lab/sources/{eid}/video')
    def video(eid:str):
        try: s=catalog.get(eid)
        except ValueError as e: raise HTTPException(409,str(e))
        return FileResponse(s['video'],media_type='video/mp4')
    @app.post('/v1/lab/render-yaml')
    def render_yaml(value:object=Body(default=None)):
        from .presentation import highlighted_yaml
        return highlighted_yaml(value)

    @app.post('/v1/lab/prompt')
    def prompt_preview(request:Experiment):
        from .presentation import reasoning_prompt
        if request.component not in ('reasoning','states'):raise HTTPException(422,'select reasoning or states')
        return reasoning_prompt(request)

    @app.post('/v1/lab/preview')
    def preview(request:Selection):
        name='preview-'+uuid.uuid4().hex[:16]; dest=output/name
        try: result=prepare(catalog,request,dest)
        except ValueError as e: raise HTTPException(422,str(e))
        result['preview_id']=name
        for f in result['frames']: f['url']=f'/v1/lab/runs/{name}/artifacts/{f["file"]}'
        (dest/'preview.json').write_text(json.dumps(result,indent=2))
        return result
    @app.get('/v1/lab/runs/{run_id}/artifacts/{name}')
    def artifact(run_id:str,name:str):
        if not re.fullmatch(r'(preview|run)-[a-f0-9]{16}',run_id) or not re.fullmatch(r'[a-zA-Z0-9_-]+\.png',name): raise HTTPException(404)
        p=output/run_id/name
        if not p.is_file(): raise HTTPException(404)
        return FileResponse(p)
    def run_root(run_id):
        if not re.fullmatch(r'run-[a-f0-9]{16}',run_id):raise HTTPException(404,'unknown run')
        p=output/run_id
        if not (p/'request.json').is_file():raise HTTPException(404,'unknown run')
        return p

    def read_run(run_id):
        p=run_root(run_id);record=json.loads((p/'status.json').read_text())
        record['request']=json.loads((p/'request.json').read_text())
        for name in ('result','progress'):
            if (p/(name+'.json')).is_file():record[name]=json.loads((p/(name+'.json')).read_text())
        return record

    @app.post('/v1/lab/handoff')
    def handoff(request:Handoff):
        from .handoff import resolve
        try:
            options, provenance=resolve(output,request)
            return dict(options=options.model_dump(),provenance=provenance)
        except ValueError as e:raise HTTPException(422,str(e))

    @app.post('/v1/lab/runs',status_code=202)
    def start(request:Experiment):
        try:return manager.start(request)
        except RuntimeError as e:raise HTTPException(409,str(e))
        except ValueError as e:raise HTTPException(422,str(e))

    @app.get('/v1/lab/runs')
    def runs():
        paths=sorted(output.glob('run-*/request.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:100]
        return dict(runs=[{k:v for k,v in read_run(p.parent.name).items() if k!='result'} for p in paths])

    @app.get('/v1/lab/runs/{run_id}')
    def run(run_id:str):return read_run(run_id)

    @app.post('/v1/lab/runs/{run_id}/cancel')
    def cancel(run_id:str):
        run_root(run_id)
        if manager.active!=run_id or not manager.thread or not manager.thread.is_alive():raise HTTPException(409,'run is not active')
        manager.cancel.set();return dict(run_id=run_id,status='cancelling')

    @app.get('/v1/lab/compare')
    def comparison(a:str,b:str):return compare(read_run(a),read_run(b))

    @app.post('/v1/lab/runs/{run_id}/reviews',status_code=201)
    def review(run_id:str,request:Review):
        p=run_root(run_id);record=read_run(run_id)
        if record['status']!='completed':raise HTTPException(409,'review a completed run')
        value=dict(review_id='review-'+uuid.uuid4().hex[:16],run_id=run_id,created_unix=time.time(),
                   source=record['request']['evidence']['source'],**request.model_dump())
        write(p/(value['review_id']+'.json'),value);return value

    @app.get('/v1/lab/runs/{run_id}/export')
    def export(run_id:str):
        p=run_root(run_id)
        return dict(schema_version=1,experiment=read_run(run_id),reviews=[json.loads(f.read_text()) for f in sorted(p.glob('review-*.json'))],
                    partition_policy='Reviews retain the source split. Export does not promote test cases into training.')

    @app.post('/v1/lab/runs/{run_id}/rule')
    def rule(run_id:str,request:RuleRequest):
        record=read_run(run_id)
        if record['status']!='completed':raise HTTPException(409,'select a completed run')
        try:result=point_rule(record,request)
        except ValueError as e:raise HTTPException(422,str(e))
        result['evaluation_record_id']='rule-'+uuid.uuid4().hex[:16]
        write(run_root(run_id)/(result['evaluation_record_id']+'.json'),result)
        return result

    @app.post('/v1/lab/actions/inspect')
    def actions(request:Selection):
        try:
            source=catalog.get(request.episode_id)
            if request.end_us>source['media']['duration_us']:raise ValueError('range exceeds source duration')
            return action_artifacts(root,source,request.start_us,request.end_us)
        except ValueError as e:raise HTTPException(422,str(e))

    # Reuse the existing replay endpoints at the same origin for Tailscale users.
    from video_workbench.replay.app import create_app as replay_app
    from video_workbench.replay.engine import Catalog as ReplayCatalog
    replay=replay_app(ReplayCatalog(),root/'output/replay-workbench')
    app.router.routes.extend(r for r in replay.router.routes if r.path.startswith('/v1/'))
    @app.get('/replay/',response_class=HTMLResponse)
    def replay_home():return (Path(__file__).parents[1]/'replay/viewer.html').read_text()
    @app.get('/lab/analysis.js')
    def analysis_script():return FileResponse(Path(__file__).parent/'analysis.js',media_type='text/javascript')
    @app.get('/favicon.ico',status_code=204)
    def favicon():return None
    return app
