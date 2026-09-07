"""Loopback replay API: registered sources, one active run, immutable history."""
from pathlib import Path
from threading import Event as CancelEvent, Lock, Thread
from contextlib import asynccontextmanager
import json
import os
import psutil
import re
import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from video_workbench.registry import file_hash
from .engine import Options, ReplayEngine, write_json
from .store import ReplayStore


class StartRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    episode_id: str=Field(min_length=1,max_length=100)
    mode: Literal['recorded','live_verifier']='recorded'
    family: Literal['qwen','cosmos']='qwen'
    speed: float=Field(default=1,gt=0,le=100)
    repetitions: int=Field(default=1,ge=1,le=100)
    max_jobs: int=Field(default=16,ge=1,le=128)
    max_bytes: int=Field(default=16*1024*1024,ge=1,le=64*1024*1024)
    perception_deadline_seconds: float=Field(default=2,gt=0,le=120)
    verifier_deadline_seconds: float=Field(default=120,gt=0,le=120)
    service_multiplier: float=Field(default=1,gt=0,le=100)


class Manager:
    def __init__(self,catalog,output):
        self.catalog=catalog;self.output=Path(output).resolve();self.output.mkdir(parents=True,exist_ok=True)
        self.lock=Lock();self.thread=None;self.active=None;self.cancel_event=CancelEvent()

    def start(self,request):
        options=Options(**request.model_dump()).validate()
        if options.episode_id not in self.catalog.sources:raise HTTPException(404,'unknown episode')
        with self.lock:
            if self.thread and self.thread.is_alive():raise HTTPException(409,'one replay is already active')
            self.active='replay-'+uuid.uuid4().hex[:16];self.cancel_event=CancelEvent();run_id=self.active
            def work():
                try:
                    engine=ReplayEngine(self.catalog,self.output,options,run_id=run_id)
                    engine.run(self.cancel_event.is_set)
                except Exception as exc:
                    root=self.output/run_id;root.mkdir(exist_ok=True)
                    write_json(root/'status.json',dict(run_id=run_id,status='failed',horizon_us=0,error=f'{type(exc).__name__}: {exc}',options=asdict_options(options)))
            self.thread=Thread(target=work,name=run_id,daemon=True);self.thread.start()
        return dict(run_id=run_id,status='starting')

    def shutdown(self):
        self.cancel_event.set()
        if self.thread:self.thread.join(timeout=5)


def asdict_options(options):
    from dataclasses import asdict
    return asdict(options)


def create_app(catalog,output):
    manager=Manager(catalog,output)
    @asynccontextmanager
    async def lifespan(app):
        yield
        manager.shutdown()
    app=FastAPI(title='Bounded video replay',lifespan=lifespan)
    app.state.manager=manager

    def root(run_id):
        if not re.fullmatch(r'replay-[a-f0-9]{16}',run_id):raise HTTPException(404,'unknown run')
        p=manager.output/run_id
        if not p.is_dir():
            if run_id==manager.active and manager.thread and manager.thread.is_alive():return p
            raise HTTPException(404,'unknown run')
        return p

    def status(run_id):
        p=root(run_id)
        if not (p/'status.json').exists():
            return dict(run_id=run_id,status='starting' if run_id==manager.active and manager.thread and manager.thread.is_alive() else 'interrupted',horizon_us=0)
        record=json.loads((p/'status.json').read_text())
        if record['status'] in ('ready','running','draining'):
            alive = bool(run_id==manager.active and manager.thread and manager.thread.is_alive())
            # A CLI replay can be inspected from another server process. Bind
            # PID plus creation time so PID reuse does not revive a stale run.
            if not alive and record.get('writer_pid') not in (None, os.getpid()):
                try:
                    writer = psutil.Process(record['writer_pid'])
                    alive = writer.is_running() and writer.create_time()==record.get('writer_created')
                except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                    pass
            if not alive: record['status']='interrupted'
        if (p/'summary.json').exists():record['summary']=json.loads((p/'summary.json').read_text())
        if (p/'config.json').exists():record['config']=json.loads((p/'config.json').read_text())
        return record

    @app.get('/',response_class=HTMLResponse)
    def home():return (Path(__file__).parent/'viewer.html').read_text()

    @app.get('/v1/replay/sources')
    def sources():
        return dict(sources=[{k:r[k] for k in ('episode_id','split','entity_label','duration_us','frames')} for r in catalog.sources.values()],modes=['recorded','live_verifier'])

    @app.post('/v1/replays',status_code=202)
    def start(request:StartRequest):return manager.start(request)

    @app.get('/v1/replays')
    def runs(limit:int=Query(default=30,ge=1,le=100)):
        paths=sorted(manager.output.glob('replay-*'),key=lambda p:p.stat().st_mtime,reverse=True)
        return dict(runs=[status(p.name) for p in paths[:limit] if re.fullmatch(r'replay-[a-f0-9]{16}',p.name)])

    @app.get('/v1/replays/{run_id}')
    def run_status(run_id:str):return status(run_id)

    @app.post('/v1/replays/{run_id}/cancel')
    def cancel(run_id:str):
        root(run_id)
        if run_id!=manager.active or not manager.thread or not manager.thread.is_alive():raise HTTPException(409,'run is not active')
        manager.cancel_event.set();return dict(run_id=run_id,status='cancelling')

    @app.get('/v1/replays/{run_id}/events')
    def events(run_id:str,after:int=Query(default=0,ge=0),limit:int=Query(default=200,ge=1,le=500),as_of_us:int|None=Query(default=None,ge=0)):
        p=root(run_id);current=status(run_id)['horizon_us'];horizon=current if as_of_us is None else as_of_us
        if horizon>current:raise HTTPException(422,'requested horizon is not available')
        if not (p/'replay.sqlite').exists():return dict(events=[],next_after=after,as_of_us=horizon)
        store=ReplayStore(p/'replay.sqlite',readonly=True)
        try:return store.events(as_of_us=horizon,after=after,limit=limit)
        finally:store.close()

    @app.get('/v1/replays/{run_id}/evidence/{evidence_id}')
    def evidence(run_id:str,evidence_id:str,as_of_us:int=Query(ge=0)):
        p=root(run_id)
        if as_of_us>status(run_id)['horizon_us']:raise HTTPException(422,'requested horizon is not available')
        if not (p/'replay.sqlite').exists():raise HTTPException(404,'unknown evidence')
        store=ReplayStore(p/'replay.sqlite',readonly=True)
        try:
            row=store.con.execute("SELECT payload FROM records WHERE kind='evidence' AND available_us<=? AND json_extract(payload,'$.frame.id')=? ORDER BY seq LIMIT 1",(as_of_us,evidence_id)).fetchone()
        finally:store.close()
        if row is None:raise HTTPException(404,'evidence not available at this horizon')
        record=json.loads(row[0]);image=(p/'evidence'/record['file']).resolve()
        if not image.is_relative_to((p/'evidence').resolve()) or not image.is_file() or file_hash(image)!=record['frame']['sha256']:
            raise HTTPException(409,'approved evidence changed')
        return FileResponse(image,media_type='image/png')

    @app.get('/v1/episodes/{episode_id}/video')
    def video(episode_id:str):
        source=catalog.sources.get(episode_id)
        if source is None:raise HTTPException(404,'unknown episode')
        path=Path(source['video'])
        if not path.is_file():raise HTTPException(410,'source video missing')
        if file_hash(path)!=source['video_sha256']:raise HTTPException(409,'registered video changed')
        return FileResponse(path,media_type='video/mp4')

    return app
