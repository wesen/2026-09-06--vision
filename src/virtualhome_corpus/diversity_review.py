"""Build audit evidence and native-pixel transition review pages, without changing labels."""
import argparse
from collections import defaultdict
import html
import itertools
import json
from pathlib import Path
import statistics
from PIL import Image, ImageDraw
from .core import save_json, file_hash, frame_files
from .diversity import plan
from .diversity_runner import validate


def dhash(image):
    pixels=list(image.convert('L').resize((9,8)).getdata())
    value=0
    for y in range(8):
        for x in range(8):value=(value<<1)|int(pixels[y*9+x]>pixels[y*9+x+1])
    return value


def audit(root, cfg):
    manifests=[json.loads((root/'episodes'/r['episode_id']/'manifest.json').read_text()) for r in plan(cfg)]
    groups={};lineages={};hashes={};fingerprints={};durations=defaultdict(list);rows=[];calibration=[]
    review=root/'review';review.mkdir(exist_ok=True)
    for m in manifests:
        validate(root,m,cfg,deep=True)
        for table,key in ((groups,m['split_group']),(lineages,m['lineage_id']),(hashes,m['video_sha256'])):
            if table.setdefault(key,m['split'])!=m['split']:raise ValueError('Cross-split group or exact video duplication')
        attempt=root/m['attempt'];images,graphs,camera=frame_files(attempt/'episode/0')
        annotations=json.loads((root/m['annotations']).read_text())
        sample_indices=[round((len(images)-1)*f) for f in (0,.25,.5,.75,1)]
        fingerprints[m['episode_id']]=[dhash(Image.open(images[i])) for i in sample_indices]
        duration=m['frame_count']/cfg['fps'];durations[m['condition']].append(duration)
        # State labels include holding/sitting evidence omitted by target-only state arrays.
        bindings=m['bindings'];target=bindings['target'];actor=bindings['char0']
        signatures=[]
        for i in images:
            g=json.loads(graphs[i].read_text(encoding='utf-8-sig'));nodes={n['id']:n for n in g['nodes']}
            holding=[e['relation_type'] for e in g['edges'] if e['from_id']==actor and e['to_id']==target and e['relation_type'].startswith('HOLDS')]
            signature={'target_states':sorted(nodes[target].get('states',[])), 'actor_states':sorted(nodes[actor].get('states',[])), 'holding':sorted(holding)}
            if not signatures or signatures[-1]['state']!=signature:signatures.append({'start_frame':i,'end_frame_exclusive':i+1,'state':signature})
            else:signatures[-1]['end_frame_exclusive']=i+1
        save_json(attempt/'observable-world-runs.json',{'quality':'simulator_world_state_not_visual_truth','runs':signatures})
        picks=set(sample_indices)
        for a in annotations['actions']:
            if a['interior']:picks.add((a['interior']['start_frame']+a['interior']['end_frame_exclusive'])//2)
        picks=sorted(picks)
        sheet=Image.new('RGB',(1280,((len(picks)+3)//4)*264),'white');draw=ImageDraw.Draw(sheet)
        for j,i in enumerate(picks):
            with Image.open(images[i]) as im:sheet.paste(im.resize((320,240)),((j%4)*320,(j//4)*264+24))
            draw.text(((j%4)*320+5,(j//4)*264+4),f'{i} / {i/cfg["fps"]:.1f}s',fill='black')
        name=m['episode_id']+'.jpg';sheet.save(review/name,quality=92)
        rows.append({'episode_id':m['episode_id'],'split':m['split'],'family':m['scenario']['family'],'target':m['scenario']['target_class'],'condition':m['condition'],'view':m['view'],'duration_s':duration,'world_runs':len(signatures),'sheet':'review/'+name,'video':m['video']})
        if m['scenario']['family']=='door' and m['condition']=='interaction':
            indices=set()
            for a in annotations['actions']:
                if a['action'] in ('OPEN','CLOSE'):
                    for endpoint in (a['raw_start'],a['raw_end']):indices.update(range(max(0,endpoint-3),min(len(images),endpoint+4)))
            for run in signatures[1:]:indices.update(range(max(0,run['start_frame']-3),min(len(images),run['start_frame']+4)))
            frames=[{'frame':i,'seconds':i/cfg['fps'],'image':str(images[i].relative_to(root)),'graph':str(graphs[i].relative_to(root))} for i in sorted(indices)]
            calibration.append({'episode_id':m['episode_id'],'target':m['scenario']['target_class'],'view':m['view'],'actions':annotations['actions'],'world_runs':signatures,'frames':frames,'reviewer':None,'visibility':'pending','visual_uncertainty_bounds':None,'precise_boundary_supervision_allowed':False,'dense_visual_state_supervision_allowed':False})
    nearest=[]
    splits={m['episode_id']:m['split'] for m in manifests}
    for a,b in itertools.combinations(fingerprints,2):
        if splits[a]==splits[b]:continue
        distances=[(x^y).bit_count() for x,y in zip(fingerprints[a],fingerprints[b])]
        nearest.append({'a':a,'b':b,'mean_hamming_64bit':statistics.mean(distances),'min_hamming_64bit':min(distances)})
    result={'episodes':len(manifests),'cross_split_lineage_violations':0,'cross_split_exact_video_duplicates':0,
            'perceptual_method':'64-bit dHash at five trajectory fractions; diagnostic only, not a robust duplicate detector',
            'nearest_cross_split_pairs':sorted(nearest,key=lambda r:r['mean_hamming_64bit'])[:20],
            'duration_by_condition':{k:{'min':min(v),'mean':statistics.mean(v),'max':max(v)} for k,v in durations.items()},
            'duration_matched':False,'actor_generalization_tested':False,'scene_generalization_design':'one apartment per split; scene and partition are confounded',
            'visual_review':'pending','rows':rows}
    save_json(root/'audit.json',result);save_json(root/'calibration-review.json',calibration)
    style='<style>body{font:18px system-ui;max-width:1350px;margin:32px auto;background:#ececec}article{background:white;padding:20px;margin:24px 0}img{max-width:100%}video{width:640px}code{font-size:14px}a{color:#135b9b}</style>'
    page=['<html><meta charset="utf-8"><title>Household diversity corpus review</title>'+style+'<h1>Household diversity corpus</h1><p>48 matched episodes · 3 apartments · 4 action families · 2 conditions · 2 views</p><p>Weak program labels; RGB boundaries uncalibrated. Review images have labels; model videos do not.</p><a href="calibration.html">Native-resolution transition neighborhoods</a>']
    for r in rows:
        page.append('<article id="'+r['episode_id']+'"><h2>'+html.escape(f"{r['split']} · {r['family']} / {r['target']} · {r['condition']} · {r['view']}")+'</h2><p><code>'+r['episode_id']+f"</code> · {r['duration_s']:.1f}s</p><img src=\"{r['sheet']}\"><details><summary>Play full video</summary><video controls preload=\"none\" src=\"{r['video']}\"></video></details></article>")
    (root/'gallery.html').write_text('\n'.join(page))
    page=['<html><meta charset="utf-8"><title>Transition calibration evidence</title>'+style+'<h1>Native-resolution transition neighborhoods</h1><p>Raw action boundaries and graph changes are candidate locations, not precise visual labels.</p>']
    for c in calibration:
        page.append(f'<article><h2>{c["episode_id"]} · {c["target"]} · {c["view"]}</h2><pre>'+html.escape(json.dumps(c['world_runs'],indent=2))+'</pre>')
        for f in c['frames']:page.append(f'<figure><figcaption>frame {f["frame"]} · {f["seconds"]:.1f}s</figcaption><img width="640" height="480" src="{f["image"]}"></figure>')
        page.append('</article>')
    (root/'calibration.html').write_text('\n'.join(page))
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','nearest_cross_split_pairs')},indent=2))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('output/virtualhome-corpus/diversity-v2'));a=p.parse_args()
    audit(a.output,json.loads((a.output/'config.json').read_text()))

if __name__=='__main__':main()
