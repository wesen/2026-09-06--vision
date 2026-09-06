"""Single-user loopback API; serving a single immutable index per process."""
from pathlib import Path
from threading import Lock
from typing import Literal
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse,HTMLResponse
from pydantic import BaseModel,Field,ConfigDict
from .registry import Registry,file_hash
from .index import Index


class SearchRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    query:str=Field(min_length=1,max_length=500)
    index_id:str|None=None
    split:Literal['train','development','test']|None=None
    top_k:int=Field(default=5,ge=1,le=100)


class SearchHit(BaseModel):
    episode_id:str
    chunk_id:str
    rank:int
    split:str
    split_group:str
    start_us:int
    end_us:int
    selected_pts_us:list[int]
    score:float
    feature_space_id:str
    video_url:str


class SearchResponse(BaseModel):
    index_id:str
    feature_space_id:str
    mode:str
    elapsed_seconds:float
    hits:list[SearchHit]


def create_app(db_path,manifest,embedder):
    index=Index(manifest,embedder.space.id)
    r=Registry(db_path)
    try:episodes={e['episode_id']:e for e in r.episodes()}
    finally:r.close()
    for source in index.manifest['corpus']:
        ep=episodes.get(source['episode_id'])
        if ep is None or any(ep[k]!=v for k,v in source.items()):
            raise ValueError('index and registry source/split mismatch')
    app=FastAPI(title='Timestamped video search',version='0.1.0')
    lock=Lock()

    @app.get('/',response_class=HTMLResponse)
    def home():return (Path(__file__).parent/'viewer.html').read_text()

    @app.get('/v1/index')
    def metadata():
        m=index.manifest
        return {k:m[k] for k in ('index_id','space_id','space','window_seconds','fps','shape','splits')}

    @app.post('/v1/search',response_model=SearchResponse)
    def search(request:SearchRequest):
        if not request.query.strip():raise HTTPException(422,'query is empty')
        if request.index_id is not None and request.index_id!=index.manifest['index_id']:
            raise HTTPException(409,'requested index is not loaded')
        started=time.perf_counter()
        with lock:
            query=embedder.text(request.query)
            hits=index.search(query,embedder.space.id,request.top_k,request.split)
        return SearchResponse(index_id=index.manifest['index_id'],feature_space_id=embedder.space.id,
            mode=embedder.space.mode,elapsed_seconds=time.perf_counter()-started,
            hits=[SearchHit(**{k:v for k,v in h.items() if k in SearchHit.model_fields},
                feature_space_id=embedder.space.id,video_url=f"/v1/episodes/{h['episode_id']}/video") for h in hits])

    @app.get('/v1/episodes/{episode_id}/video')
    def video(episode_id:str):
        ep=episodes.get(episode_id)
        if ep is None:raise HTTPException(404,'unknown episode')
        try:valid=file_hash(ep['video'])==ep['video_sha256']
        except FileNotFoundError:raise HTTPException(410,'source video missing')
        if not valid:raise HTTPException(409,'source video changed since ingest')
        return FileResponse(ep['video'],media_type='video/mp4')

    return app
