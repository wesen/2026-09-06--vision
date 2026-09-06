"""Read-only comparison of frozen region predictions and source/crop evidence."""
from pathlib import Path
import json
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse,FileResponse
from video_workbench.registry import file_hash
from .contracts import load_dataset


def create_app(run_path,samples_path,labels_path,regions_path):
    root=Path('.').resolve();samples,labels=load_dataset(samples_path,labels_path)
    run_path=Path(run_path);results=json.loads((run_path/'results.json').read_text());regions=json.loads(Path(regions_path).read_text())
    if file_hash(regions_path)!=results['feature_metadata']['manifest_sha256']:raise ValueError('region manifest changed')
    if file_hash(samples_path)!=results['sample_sha256'] or file_hash(labels_path)!=results['label_sha256']:raise ValueError('sample/label revision mismatch')
    observations=[json.loads(l) for l in (run_path/'observations.jsonl').read_text().splitlines()]
    by_id={s['sample_id']:s for s in samples};by_region={r['sample_id']:r for r in regions['samples']}
    app=FastAPI(title='State region evidence comparison')
    @app.get('/',response_class=HTMLResponse)
    def page():return (Path(__file__).parent/'region_viewer.html').read_text()
    @app.get('/v1/regions/run')
    def data():return {'results':results,'samples':samples,'labels':[l.__dict__ for l in labels],'regions':regions,'observations':observations}
    @app.get('/v1/regions/evidence/{sid}/{kind}')
    def evidence(sid:str,kind:str):
        if sid not in by_id or kind not in {'image','crop','video'}:raise HTTPException(404,'unknown evidence')
        if kind=='crop':
            c=by_region[sid]['crop']
            if c is None:raise HTTPException(404,'no accepted detector crop')
            value,sha=c['image'],c['image_sha256']
        else:value,sha=by_id[sid][kind],by_id[sid][kind+'_sha256']
        path=(root/value).resolve()
        if not path.is_relative_to(root) or not path.is_file() or file_hash(path)!=sha:raise HTTPException(409,'source changed')
        return FileResponse(path,media_type='video/mp4' if kind=='video' else 'image/png')
    return app
