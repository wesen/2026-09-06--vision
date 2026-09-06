"""Fixed development system comparison; run each encoder in its own environment."""
import argparse
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from video_workbench.evaluation import evaluate
from video_workbench.index import Index, write_json
from video_workbench.registry import file_hash

TICKET = Path(__file__).resolve().parents[1]
OUT = TICKET / 'various/native-pooled-v1'
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('mode', choices=['native_video', 'pooled_images', 'compare'])
a = p.parse_args()
protocol = json.loads((OUT / 'protocol.json').read_text())
queries_path = Path('configs/retrieval/home-v1-queries.json')
assert file_hash(queries_path) == protocol['queries_sha256'], 'query freeze changed'
queries = json.loads(queries_path.read_text())
pooled = Index(protocol['pooled_manifest'])
build_path = Path(protocol['native_root']) / 'last-build.json'
build = json.loads(build_path.read_text())
native = Index(build['manifest'])
# Chunk IDs intentionally differ by feature space. All source evidence must match.
def evidence(index):
    return [{k:v for k,v in c.items() if k != 'chunk_id'} for c in index.manifest['chunks']]
assert evidence(native) == evidence(pooled), 'source clips/timestamps differ'
for index in (native, pooled):
    assert index.manifest['splits'] == ['development']
    assert index.manifest['window_seconds'] == 2 and index.manifest['fps'] == 2
assert native.manifest['space_id'] != pooled.manifest['space_id']
if a.mode == 'compare':
    reports = {m:json.loads((OUT / (m + '.json')).read_text()) for m in ('native_video','pooled_images')}
    for m,r in reports.items():
        assert r['protocol_sha256'] == file_hash(OUT / 'protocol.json')
        assert [q['query'] for q in r['evaluation']['queries']] == [q['query'] for q in queries]
    result = {'protocol':protocol,'source_evidence_match':True,'clips':len(evidence(native)),
              'episodes':len({c['episode_id'] for c in evidence(native)}),
              'metrics':{m:r['evaluation']['metrics'] for m,r in reports.items()},
              'reports_sha256':{m:file_hash(OUT/(m+'.json')) for m in reports},
              'native_build':build}
    write_json(OUT/'comparison.json',result)
    for m,index in [('native_video',native),('pooled_images',pooled)]:write_json(OUT/(m+'-manifest.json'),index.manifest)
    print(json.dumps(result,indent=2))
else:
    dest = OUT/(a.mode+'.json')
    if dest.exists():raise ValueError('completed mode report already exists; version experiment')
    if a.mode == 'native_video':
        from video_workbench.native_video import NativeVideoEmbedder
        encoder=NativeVideoEmbedder();index=native
    else:
        from video_workbench.embedding import QwenEmbedder
        encoder=QwenEmbedder('output/models/qwen3-vl-embedding-2b-4bit');index=pooled
    assert encoder.space.id == index.manifest['space_id'], 'query/index space mismatch'
    vectors=np.stack([encoder.text(q['query']) for q in queries])
    np.save(OUT/(a.mode+'-query-vectors.npy'),vectors,allow_pickle=False)
    result={'mode':a.mode,'protocol_sha256':file_hash(OUT/'protocol.json'),
            'script_sha256':file_hash(__file__),'query_vectors_sha256':file_hash(OUT/(a.mode+'-query-vectors.npy')),
            'space':asdict(encoder.space),'space_id':encoder.space.id,
            'evaluation':evaluate(index,queries,vectors,'development',protocol)}
    write_json(dest,result)
    print(json.dumps(result['evaluation']['metrics'],indent=2))
