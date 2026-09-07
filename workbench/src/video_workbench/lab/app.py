"""Loopback API for reproducible video experiments."""
from pathlib import Path
import json
import re
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from .catalog import Catalog, ROOT
from .contracts import Selection
from .evidence import prepare

def create_app(root=ROOT):
    root=Path(root); catalog=Catalog(root); output=root/'output/video-lab'; output.mkdir(exist_ok=True,parents=True)
    app=FastAPI(title='Video Laboratory',version='0.1')
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
    return app
