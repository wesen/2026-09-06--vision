"""Loopback API for reproducible video experiments."""
from pathlib import Path
import json
import re
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from .catalog import Catalog, ROOT
from .contracts import Selection, Experiment
from .manager import Manager,write
from contextlib import asynccontextmanager
from .evidence import prepare
from .resources import Resources

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

    # Reuse the existing replay endpoints at the same origin for Tailscale users.
    from video_workbench.replay.app import create_app as replay_app
    from video_workbench.replay.engine import Catalog as ReplayCatalog
    replay=replay_app(ReplayCatalog(),root/'output/replay-workbench')
    app.router.routes.extend(r for r in replay.router.routes if r.path.startswith('/v1/'))
    @app.get('/replay/',response_class=HTMLResponse)
    def replay_home():return (Path(__file__).parents[1]/'replay/viewer.html').read_text()
    @app.get('/favicon.ico',status_code=204)
    def favicon():return None
    return app
