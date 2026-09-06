"""Content-addressed frame cache and immutable, atomically published clip indices."""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import fcntl
import json
import os
import sqlite3
import tempfile
import time
import numpy as np
from .embedding import digest, normalize
from .registry import file_hash
from .media import selected_indices, decode_selected


def atomic_write(path, writer):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            writer(f);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)


def write_json(path,value):
    atomic_write(path,lambda f:f.write((json.dumps(value,sort_keys=True,indent=2)+'\n').encode()))


@contextmanager
def writer_lock(root):
    Path(root).mkdir(parents=True,exist_ok=True)
    with (Path(root)/'.writer.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('another index writer is active')
        try:yield
        finally:fcntl.flock(lock,fcntl.LOCK_UN)


class FrameCache:
    """One writer; SQLite row is authoritative only after array publication."""
    def __init__(self,root,space):
        self.root=Path(root)/'frames'/space.id;self.root.mkdir(parents=True,exist_ok=True)
        self.space=space
        self.db=sqlite3.connect(self.root/'metadata.sqlite')
        self.db.execute('CREATE TABLE IF NOT EXISTS features (key TEXT PRIMARY KEY, sha256 TEXT NOT NULL)')
        self.db.commit()

    def close(self):self.db.close()

    def get(self,key):
        row=self.db.execute('SELECT sha256 FROM features WHERE key=?',(key,)).fetchone()
        if row is None:return None # orphan arrays after a crash are not committed
        path=self.root/(key+'.npy')
        if file_hash(path)!=row[0]:raise ValueError('corrupt cached feature')
        a=np.load(path,allow_pickle=False)
        if a.shape!=(1,self.space.dimension) or a.dtype!=np.float32 or not np.isfinite(a).all() or not np.allclose(np.linalg.norm(a,axis=1),1,atol=1e-5):
            raise ValueError('invalid cached vector')
        return a[0]

    def put(self,key,vector,after_publish=None):
        a=normalize(np.asarray(vector)[None])
        if a.shape!=(1,self.space.dimension):raise ValueError('feature dimension mismatch')
        path=self.root/(key+'.npy')
        atomic_write(path,lambda f:np.save(f,a,allow_pickle=False))
        if after_publish:after_publish()
        with self.db:self.db.execute('INSERT OR REPLACE INTO features VALUES (?,?)',(key,file_hash(path)))
        return a[0]


def windows(duration_us,seconds):
    size=round(seconds*1e6)
    if size<=0:raise ValueError('window must be positive')
    return [(start,min(start+size,duration_us)) for start in range(0,duration_us,size)]


def frame_key(episode,index,space):
    m=episode['media']
    return digest({'space':space.id,'video':episode['video_sha256'],
        'raw_pts':m['raw_pts'][index],'time_base':m['time_base'],
        'origin_us':m['origin_us'],'pts_us':m['pts_us'][index]})


def build(registry,embedder,root,seconds=5,fps=1,splits=('train','development','test'),progress=print):
    if fps<=0 or fps>30:raise ValueError('FPS must be in (0,30]')
    root=Path(root)
    with writer_lock(root):
        cache=FrameCache(root,embedder.space)
        try:
            started=time.perf_counter();chunks=[];vectors=[];fresh=0;reused=0
            episodes=[r for r in registry.episodes() if r['split'] in splits]
            if not episodes:raise ValueError('no episodes in requested splits')
            for ep in episodes:
                if file_hash(ep['video'])!=ep['video_sha256']:raise ValueError('source video changed')
                pts=ep['media']['pts_us']
                plans=[(a,b,selected_indices(pts,a,b,fps)) for a,b in windows(ep['media']['duration_us'],seconds)]
                required=sorted({i for _,_,ids in plans for i in ids})
                features={i:cache.get(frame_key(ep,i,embedder.space)) for i in required}
                missing=[i for i in required if features[i] is None]
                images=decode_selected(ep['video'],missing)
                for i in missing:
                    features[i]=cache.put(frame_key(ep,i,embedder.space),embedder.image(images[i]))
                    del images[i]
                fresh+=len(missing);reused+=len(required)-len(missing)
                for start,end,ids in plans:
                    if not ids:continue # empty VFR spans contain no visual evidence
                    chunk={'episode_id':ep['episode_id'],'split':ep['split'],'split_group':ep['split_group'],
                        'video_sha256':ep['video_sha256'],'start_us':start,'end_us':end,
                        'selected_pts_us':[pts[i] for i in ids],
                        'selected_raw_pts':[ep['media']['raw_pts'][i] for i in ids],
                        'time_base':ep['media']['time_base'],'origin_us':ep['media']['origin_us']}
                    chunk['chunk_id']=digest({'space':embedder.space.id,**chunk})
                    chunks.append(chunk)
                    vectors.append(normalize(np.mean([features[i] for i in ids],axis=0)[None])[0])
                progress(f"{ep['episode_id']}: {len(plans)} windows, {len(missing)} new frames",flush=True)
            spec={'schema':1,'space':asdict(embedder.space),'space_id':embedder.space.id,
                'window_seconds':seconds,'fps':fps,'splits':sorted(splits),
                'producer_files':{name:file_hash(Path(__file__).parent/name) for name in ('embedding.py','media.py','index.py')},
                'corpus':[{k:e[k] for k in ('episode_id','split','split_group','video_sha256')} for e in episodes],
                'chunks':chunks}
            identity=digest(spec)
            directory=root/'indices'/identity;directory.mkdir(parents=True,exist_ok=True)
            array=np.stack(vectors).astype(np.float32)
            path=directory/'features.npy'
            atomic_write(path,lambda f:np.save(f,array,allow_pickle=False))
            manifest=spec|{'index_id':identity,'array_sha256':file_hash(path),'shape':list(array.shape)}
            write_json(directory/'manifest.json',manifest)
            report={'index_id':identity,'manifest':str(directory/'manifest.json'),
                'chunks':len(chunks),'fresh_frames':fresh,'reused_frames':reused,
                'elapsed_seconds':time.perf_counter()-started,'feature_bytes':path.stat().st_size}
            write_json(root/'last-build.json',report)
            return report
        finally:cache.close()


class Index:
    def __init__(self,manifest,expected_space=None):
        self.path=Path(manifest)
        self.manifest=json.loads(self.path.read_text())
        m=self.manifest
        if m['schema']!=1:raise ValueError('unsupported index schema')
        if digest(m['space'])!=m['space_id']:raise ValueError('invalid space identity')
        if expected_space is not None and m['space_id']!=expected_space:raise ValueError('incompatible feature space')
        spec={k:v for k,v in m.items() if k not in ('index_id','array_sha256','shape')}
        if digest(spec)!=m['index_id']:raise ValueError('manifest identity mismatch')
        array=self.path.parent/'features.npy'
        if file_hash(array)!=m['array_sha256']:raise ValueError('index array hash mismatch')
        self.vectors=np.load(array,mmap_mode='r',allow_pickle=False)
        if list(self.vectors.shape)!=m['shape'] or self.vectors.shape!=(len(m['chunks']),m['space']['dimension']) or self.vectors.dtype!=np.float32:
            raise ValueError('invalid index shape or dtype')
        if not np.isfinite(self.vectors).all() or not np.allclose(np.linalg.norm(self.vectors,axis=1),1,atol=1e-5):raise ValueError('invalid index normalization')

    def search(self,query,space_id,k=10,split=None):
        if space_id!=self.manifest['space_id']:raise ValueError('incompatible query feature space')
        if k<1 or k>100:raise ValueError('k must be 1..100')
        q=normalize(np.asarray(query)[None])[0]
        if q.shape!=(self.vectors.shape[1],):raise ValueError('query dimension mismatch')
        scores=self.vectors@q
        eligible=[i for i,c in enumerate(self.manifest['chunks']) if split is None or c['split']==split]
        ordered=sorted(eligible,key=lambda i:(-float(scores[i]),self.manifest['chunks'][i]['chunk_id']))[:k]
        return [dict(self.manifest['chunks'][i],score=float(scores[i]),rank=rank+1) for rank,i in enumerate(ordered)]
