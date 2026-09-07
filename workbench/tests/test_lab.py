"""Feature-boundary checks for the laboratory's evidence and option contracts."""
from pathlib import Path
import pytest
from video_workbench.lab.contracts import Selection,Experiment
from video_workbench.lab.catalog import Catalog,ROOT
from video_workbench.lab.evidence import prepare

def test_ranges_and_model_combinations():
    for kwargs in ({'end_us':0},{'start_us':2,'end_us':1},{'fps':float('nan')},{'crop':[.8,0,.2,1]}):
        with pytest.raises(ValueError): Selection(episode_id='x',**kwargs)
    with pytest.raises(ValueError): Experiment(episode_id='x',component='embeddings',model='qwen')

def test_corpus_identity_and_exact_preview(tmp_path):
    catalog=Catalog(); eid='home-v1--ep-7d3106fb1cac9776'
    if eid not in catalog.sources: pytest.skip('local corpus absent')
    source=catalog.get(eid)
    assert source['original_episode_id']=='ep-7d3106fb1cac9776'
    result=prepare(catalog,Selection(episode_id=eid,start_us=9500000,end_us=10500000,fps=2,crop=(.25,0,.75,1)),tmp_path)
    assert [f['pts_us'] for f in result['frames']]==[9500000,10000000]
    assert result['frames'][0]['width']==source['media']['width']//2
    with pytest.raises(ValueError,match='64 sample'):
        prepare(catalog,Selection(episode_id=eid,end_us=14000000,fps=10),tmp_path/'too-many')
