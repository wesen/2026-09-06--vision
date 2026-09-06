"""Allowlisted perception replay, source-coordinate overlays, and crop evidence."""
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
from io import BytesIO
import json
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse,FileResponse,Response
from video_workbench.registry import file_hash
from video_workbench.media import decode_selected
from .store import rows,verify_episode


def create_app(run_path,derived_path):
    source,derived=Path(run_path).resolve(),Path(derived_path).resolve()
    run=json.loads((source/'run.json').read_text());other=json.loads((derived/'run.json').read_text())
    if run['status']!='complete' or other['status']!='complete' or other['spec']['source_run']!=run['run_id']:
        raise ValueError('incomplete or mismatched perception runs')
    if other['spec']['source_manifest_sha256']!=file_hash(source/'run.json'):raise ValueError('source run changed')
    allowed={e['episode_id']:e for e in run['episodes']};der_entries={e['episode_id']:e for e in other['episodes']}
    app=FastAPI(title='Perception evidence replay')
    @lru_cache(maxsize=64)
    def load(eid):
        if eid not in allowed or eid not in der_entries:raise HTTPException(404,'unknown episode')
        a,b=source/'episodes'/eid,derived/'episodes'/eid
        if file_hash(a/'manifest.json')!=allowed[eid]['manifest_sha256'] or file_hash(b/'manifest.json')!=der_entries[eid]['manifest_sha256']:
            raise HTTPException(409,'manifest changed')
        m=verify_episode(a);d=verify_episode(b)
        return {'manifest':m,'derived':d,'frames':rows(a/'frames.jsonl'),'detections':rows(a/'detections.jsonl'),'tracks':rows(b/'tracks.jsonl'),'crops':rows(b/'crops.jsonl'),'proposals':rows(b/'proposals.jsonl')}
    @app.get('/',response_class=HTMLResponse)
    def page():return (Path(__file__).parent/'viewer.html').read_text()
    @app.get('/v1/perception/run')
    def overview():
        episodes=[]
        for eid in allowed:
            a=json.loads((source/'episodes'/eid/'manifest.json').read_text())
            episodes.append({k:a['episode'][k] for k in ('episode_id','split','split_group')}|{'frames':a['frames']})
        return {'run_id':run['run_id'],'derived_id':other['run_id'],'episodes':episodes,'detector':run['spec']['detector']}
    @app.get('/v1/perception/episodes/{eid}')
    def episode(eid:str):return load(eid)
    def video_source(eid):
        e=load(eid)['manifest']['episode'];p=Path(e['video'])
        if not p.is_file() or file_hash(p)!=e['video_sha256']:raise HTTPException(409,'video source changed')
        return p
    @app.get('/v1/perception/episodes/{eid}/video')
    def video(eid:str):return FileResponse(video_source(eid),media_type='video/mp4')
    @app.get('/v1/perception/episodes/{eid}/frame/{index}')
    def frame(eid:str,index:int):
        if not 0<=index<len(load(eid)['frames']):raise HTTPException(404,'unknown frame')
        im=decode_selected(video_source(eid),[index])[index];buf=BytesIO();im.save(buf,format='PNG')
        return Response(buf.getvalue(),media_type='image/png')
    @app.get('/v1/perception/episodes/{eid}/crop/{crop_id}')
    def crop(eid:str,crop_id:str):
        record=next((c for c in load(eid)['crops'] if c['evidence_id']==crop_id),None)
        if record is None:raise HTTPException(404,'unknown crop')
        p=Path(record['image']).resolve()
        if not p.is_relative_to(derived) or not p.is_file() or file_hash(p)!=record['image_sha256']:raise HTTPException(409,'crop changed')
        return FileResponse(p,media_type='image/png')
    @app.get('/v1/perception/masks')
    def masks():
        path=source.parent/'masks-v1/masks.json'
        return json.loads(path.read_text()) if path.exists() else {'records':[]}
    return app
