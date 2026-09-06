"""Read-only review of frozen observations and source evidence."""
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from video_workbench.registry import file_hash
from .contracts import load_dataset, StateObservation


def create_app(run_path: Path, root=Path('.')):
    run_path,root=run_path.resolve(),root.resolve()
    samples, labels=load_dataset(run_path/'samples.json',run_path/'labels.json',root)
    results=json.loads((run_path/'results.json').read_text())
    observations=[json.loads(line) for line in (run_path/'observations.jsonl').read_text().splitlines()]
    by_id={s['sample_id']:s for s in samples}
    for row in observations:
        StateObservation(**{k:v for k,v in row.items() if k not in {'condition','split'}})
        if row['sample_id'] not in by_id:
            raise ValueError('unknown observation source')
        sample=by_id[row['sample_id']]
        if any(row[k]!=sample[k] for k in ('entity_id','episode_id','sample_us','property','split')):
            raise ValueError('observation/source mismatch')
        if row['producer_id']!=results['conditions'][row['condition']]['producer_id'] or row['feature_space_id']!=results['feature_space_id']:
            raise ValueError('observation/producer mismatch')
    app=FastAPI(title='Observable-state evidence review')

    @app.get('/',response_class=HTMLResponse)
    def page():
        return (Path(__file__).parent/'timeline.html').read_text()

    @app.get('/v1/state/run')
    def run():
        return {'run_id':results['run_id'],'conditions':results['conditions'],'limitations':results['limitations'],
                'samples':samples,'labels':[l.__dict__ for l in labels],'observations':observations}

    @app.get('/v1/state/evidence/{sample_id}/{kind}')
    def evidence(sample_id:str,kind:str):
        if sample_id not in by_id or kind not in {'image','video'}:
            raise HTTPException(404,'unknown evidence')
        s=by_id[sample_id]
        path=(root/s[kind]).resolve()
        if not path.is_relative_to(root) or not path.is_file() or file_hash(path)!=s[kind+'_sha256']:
            raise HTTPException(409,'source evidence changed')
        return FileResponse(path,media_type='image/png' if kind=='image' else 'video/mp4')
    return app
