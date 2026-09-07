"""Fixed component worker; receives only a server-owned immutable run directory."""
from pathlib import Path
from dataclasses import asdict
import json,sys,time
import numpy as np
from PIL import Image,ImageDraw
from video_workbench.registry import file_hash
from video_workbench.embedding import digest
from .manager import write
from .catalog import ROOT,MODELS

def checked_image(root,frame):
    p=root/frame['file']
    if file_hash(p)!=frame['sha256']:raise ValueError('approved input image changed')
    return Image.open(p).convert('RGB')

def perception(root,request):
    import torch,ultralytics
    from ultralytics import YOLO
    from video_workbench.perception.contracts import FrameRef
    from video_workbench.perception.tracking import TrackerSession
    o=request['options'];checkpoint=ROOT/MODELS[o['model']][2]
    if o['device']=='mps' and not torch.backends.mps.is_available():raise ValueError('MPS unavailable; no fallback')
    model=YOLO(str(checkpoint));records=[]
    spec=dict(checkpoint_sha256=file_hash(checkpoint),torch=torch.__version__,ultralytics=ultralytics.__version__,
              parameters={k:o[k] for k in ('confidence','iou','image_size','device','classes')})
    tracker=TrackerSession(request['run_id'],o['episode_id'],cadence_us=round(1e6/o['fps'])) if o['component']=='tracking' else None
    for frame in request['evidence']['frames']:
        image=checked_image(root,frame);start=time.monotonic()
        result=model.predict(image,device=o['device'],conf=o['confidence'],iou=o['iou'],imgsz=o['image_size'],
                             classes=o['classes'] or None,max_det=100,rect=False,augment=False,verbose=False)[0]
        detections=[];polygons=[]
        for i,b in enumerate(result.boxes):
            xy=b.xyxy[0].tolist();cls=int(b.cls[0]);score=float(b.conf[0])
            detections.append(dict(detection_id=digest([request['run_id'],frame['id'],i]),class_id=cls,class_name=model.names[cls],score=score,xyxy=xy))
        if result.masks is not None:
            polygons=[np.asarray(p,dtype=float).tolist() for p in result.masks.xy]
        paint=image.convert('RGBA');layer=Image.new('RGBA',image.size);draw=ImageDraw.Draw(layer)
        for polygon in polygons:
            if len(polygon)>=3:draw.polygon([tuple(p) for p in polygon],fill=(75,235,170,90),outline=(165,255,218,230))
        paint=Image.alpha_composite(paint,layer).convert('RGB');draw=ImageDraw.Draw(paint)
        for d in detections:
            draw.rectangle(d['xyxy'],outline='#a5ebc8',width=2);draw.text((d['xyxy'][0]+3,d['xyxy'][1]+3),f"{d['class_name']} {d['score']:.2f}",fill='white',stroke_width=1,stroke_fill='black')
        tracks=[]
        if tracker:
            ref=FrameRef(o['episode_id'],request['evidence']['source']['video_sha256'],frame['frame_index'],frame['raw_pts'],frame['time_base'],frame['pts_us'],image.width,image.height)
            tracks=tracker.update(ref,detections)
            for t in tracks:
                draw.rectangle(t['xyxy'],outline='orange' if t['status']=='predicted' else 'cyan',width=2)
                draw.text((t['xyxy'][0],t['xyxy'][3]-14),t['track_id'].split(':')[-1]+' '+t['status'],fill='white',stroke_width=1,stroke_fill='black')
        name='overlay-'+frame['id']+'.png';paint.save(root/name)
        records.append(dict(frame=frame,detections=detections,polygons=polygons,tracks=tracks,overlay=name,seconds=time.monotonic()-start))
        write(root/'progress.json',dict(done=len(records),total=len(request['evidence']['frames'])))
    return dict(kind=o['component'],spec=spec,records=records,resets=tracker.resets if tracker else [],coordinates='input-image pixels; add crop origin for source coordinates')

def transitions(samples,max_gap_us):
    events=[];previous=None
    for s in samples:
        if s['state']=='unknown':previous=None;continue
        if previous and s['pts_us']-previous['pts_us']<=max_gap_us and s['state']!=previous['state']:
            events.append(dict(kind='OPEN' if s['state']=='open' else 'CLOSE',start_us=previous['pts_us'],end_us=s['pts_us'],
                               interval='(start, end]',evidence_ids=[previous['frame']['id'],s['frame']['id']]))
        previous=s
    return events

def reasoning(root,request):
    from video_workbench.verifiers.worker import run
    from video_workbench.verifiers.profiles import make_profile,profile_hash
    from video_workbench.verifiers.recovery import parse_with_recovery
    from video_workbench.verifiers.adapter import check_packet
    o=request['options']
    from video_workbench.embedding import artifact_identity
    checkpoint_identity,_=artifact_identity(ROOT/MODELS[o['model']][2])
    profile=make_profile(o['model'],reasoning=o['reasoning'])
    profile.update(max_output_tokens=o['max_tokens'],deadline_ms=min(120000,o['deadline_seconds']*1000));profile['id']+='-lab'
    pp=root/'profile.json';write(pp,profile);records=[]
    for f in request['evidence']['frames']:
        checked_image(root,f);t=f['pts_us'];entity=o['target']
        approved=dict(id=f['id'],episode_id=o['episode_id'],entity_id=entity,pts_us=t,available_us=t,path=str(root/f['file']),sha256=f['sha256'])
        packet=dict(episode_id=o['episode_id'],entity_id=entity,entity_label=entity,property='door_open',
                    question=f'Is the {entity} door visibly open in the approved frame? Answer unknown if obscured or not identifiable.',
                    event_us=t,allowed_start_us=t,allowed_end_us=t+1,as_of_us=t,frames=[approved],max_output_tokens=o['max_tokens'],deadline_ms=profile['deadline_ms'])
        packet['request_id']=digest(packet);check_packet(packet)
        rp=root/('request-'+f['id']+'.json');out=root/('answer-'+f['id']+'.json');write(rp,packet)
        import signal
        def expired(*_):raise TimeoutError('single-image verifier exceeded its approved deadline')
        previous_handler=signal.signal(signal.SIGALRM,expired)
        signal.setitimer(signal.ITIMER_REAL,profile['deadline_ms']/1000)
        try:run(str(ROOT/MODELS[o['model']][2]),rp,out,'visibility',pp)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            signal.signal(signal.SIGALRM,previous_handler)
        raw=json.loads(out.read_text());check_packet(packet)
        parsed=parse_with_recovery(packet,raw['raw'],profile,raw.get('finish_reason'))
        answer=parsed.get('answer',{}).get('answer','unknown') if parsed['status']=='ok' else 'unknown'
        records.append(dict(frame=f,pts_us=t,state={'true':'open','false':'closed','unknown':'unknown'}[answer],parsed=parsed,runtime=raw))
        write(root/'progress.json',dict(done=len(records),total=len(request['evidence']['frames'])))
    return dict(kind=o['component'],mode='independent-single-image',profile=profile,profile_sha256=profile_hash(profile),
                checkpoint=str(ROOT/MODELS[o['model']][2]),checkpoint_identity=checkpoint_identity,records=records,events=transitions(records,int(o['max_gap_seconds']*1e6)))

def embeddings(root,request):
    from video_workbench.media import selected_indices
    o=request['options']
    if o['model']=='native_video':
        from video_workbench.native_video import NativeVideoEmbedder
        encoder=NativeVideoEmbedder(str(ROOT/MODELS[o['model']][2]))
    else:
        from video_workbench.embedding import QwenEmbedder
        encoder=QwenEmbedder(str(ROOT/MODELS[o['model']][2]))
    frames=request['evidence']['frames'];images=[checked_image(root,f) for f in frames];query=encoder.text(o['query']);windows=[];vectors=[]
    start=o['start_us'];width=round(o['window_seconds']*1e6);stride=round(o['stride_seconds']*1e6)
    while start<o['end_us']:
        end=min(start+width,o['end_us']);ids=[i for i,f in enumerate(frames) if start<=f['pts_us']<end]
        if ids:
            if o['model']=='native_video':vector=encoder.video([images[i] for i in ids],[frames[i]['pts_us'] for i in ids],start)
            else:vector=encoder.pool([images[i] for i in ids])
            vector=np.asarray(vector,dtype=np.float32).reshape(-1);vectors.append(vector)
            windows.append(dict(start_us=start,end_us=end,frame_ids=[frames[i]['id'] for i in ids],pts_us=[frames[i]['pts_us'] for i in ids],score=float(vector@np.asarray(query).reshape(-1))))
        start+=stride
        if len(windows)>128:raise ValueError('window budget exceeded')
        write(root/'progress.json',dict(done=len(windows),total=None))
    if not windows:raise ValueError('no nonempty embedding windows')
    np.savez(root/'vectors.npz',vectors=np.stack(vectors),query=np.asarray(query))
    return dict(kind='embeddings',space=asdict(encoder.space),feature_space_id=encoder.space.id,query=o['query'],windows=windows,
                ranking=sorted(range(len(windows)),key=lambda i:windows[i]['score'],reverse=True),sampling='one shared selection grid, windows filter its actual frames')

def actions(root,request):
    """Fresh encoding and frozen ridge inference under the training policy."""
    o=request['options'];native=o['model']=='native_ridge'
    feature_root=ROOT/('output/temporal-native-fp32-v1/features' if native else 'output/temporal-v1/pooled-features')
    model_path=ROOT/('output/temporal-native-fp32-v1/ridge/results.json' if native else 'output/temporal-v1/linear-v1/results.json')
    benchmark=json.loads(model_path.read_text());fm=json.loads((feature_root/'manifest.json').read_text())
    if file_hash(feature_root/'manifest.json')!=benchmark['features_manifest_sha256'] or benchmark['model']['space']!=fm['space_id']:
        raise ValueError('action checkpoint/feature manifest mismatch')
    if native:
        from video_workbench.native_video import NativeVideoEmbedder
        encoder=NativeVideoEmbedder(str(ROOT/MODELS[o['model']][2]))
    else:
        from video_workbench.embedding import QwenEmbedder
        encoder=QwenEmbedder(str(ROOT/MODELS[o['model']][2]))
    if digest(fm['spec']['encoder'])!=encoder.space.id:raise ValueError('action encoder differs from frozen training feature space')
    if fm['spec']['policy']['fps']!=2 or fm['spec']['policy']['window_us']!=2000000 or fm['spec']['policy']['stride_us']!=500000:
        raise ValueError('unsupported frozen action sampling policy')
    frames=request['evidence']['frames'];images=[checked_image(root,f) for f in frames];head=benchmark['model'];windows=[]
    for end in range(o['start_us']+500000,o['end_us']+1,500000):
        start=max(o['start_us'],end-2000000);ids=[i for i,f in enumerate(frames) if start<=f['pts_us']<end]
        if not ids:continue
        vector=encoder.video([images[i] for i in ids],[frames[i]['pts_us'] for i in ids],start) if native else encoder.pool([images[i] for i in ids])
        scores=(np.asarray(vector)-np.asarray(head['mean']))@np.asarray(head['weights'])+np.asarray(head['bias'])
        windows.append(dict(start_us=start,end_us=end,pts_us=[frames[i]['pts_us'] for i in ids],prediction=benchmark['classes'][int(scores.argmax())],scores=scores.tolist(),frame_ids=[frames[i]['id'] for i in ids]))
        write(root/'progress.json',dict(done=len(windows),total=(o['end_us']-o['start_us'])//500000))
    return dict(kind='actions',mode='fresh-encoding-frozen-ridge',action_windows=windows,classes=benchmark['classes'],feature_space_id=fm['space_id'],encoder_space_id=encoder.space.id,checkpoint_sha256=file_hash(model_path),policy=fm['spec']['policy'],
                scope='Fresh full-frame encoding and frozen ridge scores. Selection start resets trailing context. Scores are not probabilities; weak-label action predictions are not reviewed event boundaries.')

def main():
    root=Path(sys.argv[1]).absolute();request=json.loads((root/'request.json').read_text());c=request['options']['component'];start=time.monotonic()
    result=perception(root,request) if c in ('detection','segmentation','tracking') else reasoning(root,request) if c in ('reasoning','states') else actions(root,request) if c=='actions' else embeddings(root,request)
    result.update(run_id=request['run_id'],seconds=time.monotonic()-start)
    write(root/'result.json',result)

if __name__=='__main__':main()
