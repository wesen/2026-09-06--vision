"""Freeze/deduplicate source targets without exposing state labels or detections."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from video_workbench.embedding import digest
from video_workbench.registry import file_hash
from video_workbench.index import write_json
from .annotations import CLASS_MAP


def prepare(state_path,pilot_path,destination):
    dest=Path(destination)
    if dest.exists():raise ValueError('new localization dataset directory required')
    state=json.loads(Path(state_path).read_text());pilot=json.loads(Path(pilot_path).read_text());merged={};input_count=0
    for kind,rows in [('state',state),('pilot',pilot)]:
        for r in rows:
            input_count+=1
            image=Path(r['image']);sha=file_hash(image)
            if sha!=r['image_sha256']:raise ValueError('source image changed')
            with Image.open(image) as im:width,height=im.size
            cls=r['entity_class'] if kind=='state' else r['target_class']
            if cls not in CLASS_MAP:raise ValueError('class not in frozen vocabulary')
            if kind=='state':video=Path(r['video'])
            else:
                release=Path('output/virtualhome-corpus/diversity-v2')
                episode_manifest=json.loads((release/'episodes'/r['episode_id']/'manifest.json').read_text())
                video=release/episode_manifest['attempt']/'video.mp4'
            if file_hash(video)!=r['video_sha256']:raise ValueError('source video changed')
            manifest_path=video.parents[1]/'manifest.json';manifest=json.loads(manifest_path.read_text())
            entity=f"{r['episode_id']}:object-{manifest['bindings']['target']}"
            if kind=='state' and r['entity_id']!=entity:raise ValueError('requested entity mismatch')
            key=(r['video_sha256'],r['frame_index'],entity)
            item={'episode_id':r['episode_id'],'video':str(video),'video_sha256':r['video_sha256'],'image':str(image),'image_sha256':sha,'frame_index':r['frame_index'],'pts_us':r['sample_us'] if kind=='state' else r['pts_us'],'width':width,'height':height,'requested_entity':entity,'requested_class':cls,'mapped_class':CLASS_MAP[cls],'split':r['split'],'apartment':r.get('split_group',f"apartment-{manifest.get('scene',manifest.get('scene_index','unknown'))}"),'view':manifest.get('view',str(manifest.get('group',{}).get('camera_dx','fixed'))),'manifest_sha256':file_hash(manifest_path)}
            alias={'kind':kind,'id':r['sample_id'] if kind=='state' else str(r['ordinal'])}
            if key in merged:
                previous=merged[key]
                for field in ('image_sha256','pts_us','requested_class','split'):
                    if item[field]!=previous[field]:raise ValueError('duplicate source has conflicting metadata')
                previous['aliases'].append(alias)
            else:
                item['sample_id']=digest(key)[:24];item['aliases']=[alias];merged[key]=item
    samples=list(merged.values());reviews=[]
    for s in samples:reviews.append({'sample_id':s['sample_id'],'image_sha256':s['image_sha256'],'visibility':'pending','visible_xyxy':None,'detector_class_supported':s['mapped_class'] is not None,'occluded':False,'truncated':False,'temporal_context_used':False,'reviewer':None,'rationale':'','convention':'visible-extent-half-open-v1'})
    dest.mkdir(parents=True);write_json(dest/'samples.json',samples);write_json(dest/'reviews-pending.json',reviews)
    summary={'input_references':input_count,'unique_targets':len(samples),'duplicates':input_count-len(samples),'state_references':len(state),'pilot_references':len(pilot),'sample_sha256':file_hash(dest/'samples.json'),'input_sha256':{str(p):file_hash(p) for p in (state_path,pilot_path)},'class_map':CLASS_MAP,'status':'source frozen; annotation pending'}
    write_json(dest/'manifest.json',summary);return summary


def review_sheets(dataset,destination):
    samples=json.loads((Path(dataset)/'samples.json').read_text());dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
    groups={}
    for s in samples:groups.setdefault(s['episode_id'],[]).append(s)
    index=[]
    for ordinal,(episode,rows) in enumerate(groups.items()):
        rows=sorted(rows,key=lambda s:s['frame_index']);canvas=Image.new('RGB',(1280,510*((len(rows)+1)//2)),'white');draw=ImageDraw.Draw(canvas)
        for i,s in enumerate(rows):
            if file_hash(s['image'])!=s['image_sha256']:raise ValueError('source image changed')
            x=i%2*640;y=i//2*510
            with Image.open(s['image']) as im:canvas.paste(im,(x,y))
            draw.text((x+4,y+483),f"{s['sample_id']} / frame {s['frame_index']} / {s['requested_class']}",fill='black')
        path=dest/f'source-{ordinal:02d}.jpg';canvas.save(path,quality=96);index.append({'episode_id':episode,'sheet':str(path),'sample_ids':[s['sample_id'] for s in rows]})
    write_json(dest/'index.json',index);return {'sheets':len(index),'targets':len(samples)}
