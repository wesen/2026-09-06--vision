"""Publish separate production and oracle streams with verified source identities."""
from dataclasses import fields
import json
from pathlib import Path
from video_workbench.predicates.contracts import StateObservation
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json


def export(comparison, crop_manifest, feature_metadata, destination):
    source=Path(comparison);dest=Path(destination)
    if dest.exists():raise ValueError('new handoff destination required')
    manifest=json.loads((source/'manifest.json').read_text())
    if manifest['status']!='complete':raise ValueError('incomplete comparison')
    for name in ('results.json','observations.jsonl'):
        if file_hash(source/name)!=manifest['artifacts'][name]:raise ValueError('comparison artifact changed')
    results=json.loads((source/'results.json').read_text())
    crops=json.loads(Path(crop_manifest).read_text())
    if file_hash(feature_metadata)!=results['feature_metadata_sha256']:
        raise ValueError('feature metadata mismatch')
    if file_hash(crop_manifest)!=json.loads(Path(feature_metadata).read_text())['producer']['manifest_sha256']:
        raise ValueError('crop manifest mismatch')
    by_state={a['id']:s for s in crops['samples'] for a in s['aliases'] if a['kind']=='state'}
    streams={'production':[],'oracle_diagnostic':[]};seen=set()
    for line in (source/'observations.jsonl').read_text().splitlines():
        row=json.loads(line);StateObservation(**{f.name:row[f.name] for f in fields(StateObservation)})
        condition=row['condition'];base=condition.split('__')[0];sample=by_state[row['sample_id']]
        key=(condition,row['sample_id'])
        if key in seen:raise ValueError('duplicate observation')
        seen.add(key)
        if row['producer_id']!=results['conditions'][condition]['producer_id']:raise ValueError('observation producer mismatch')
        if row['oracle_assisted']!=(base in ('O','FO')):raise ValueError('oracle provenance mismatch')
        for key in ('episode_id','entity_id','split'):
            if row[key]!=sample[key]:raise ValueError('handoff source mismatch')
        if row['sample_us']!=sample['pts_us']:raise ValueError('handoff timestamp mismatch')
        used=['F'] if base=='F' else [base] if base in ('D','O') else ['F',base[1]]
        expected_ids=[sample[c]['evidence_id'] for c in used if sample[c] is not None]
        if not expected_ids:expected_ids=[sample['sample_id']]
        if row['evidence_ids']!=expected_ids:raise ValueError('condition evidence citation mismatch')
        expected_available=base not in ('D','O') or sample[base] is not None
        if row['evidence_available']!=expected_available:raise ValueError('evidence availability mismatch')
        if row['feature_space_id']!=results['conditions'][condition]['spec']['space']:raise ValueError('handoff feature space mismatch')
        if not row['evidence_available'] and (row['raw_score'] is not None or row['calibrated_probability'] is not None or row['value'] is not None):raise ValueError('missing evidence has numerical inference')
        row.update(video_sha256=sample['video_sha256'],frame_index=sample['frame_index'],source_image_sha256=sample['image_sha256'])
        streams['oracle_diagnostic' if row['oracle_assisted'] else 'production'].append(row)
    expected=len(by_state)*len(results['conditions'])
    if len(seen)!=expected:raise ValueError('incomplete observation population')
    dest.mkdir(parents=True)
    for name,rows in streams.items():
        rows.sort(key=lambda r:(r['condition'],r['episode_id'],r['sample_us']))
        (dest/(name+'.jsonl')).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in rows))
    output={'status':'complete','source_manifest_sha256':file_hash(source/'manifest.json'),'crop_manifest_sha256':file_hash(crop_manifest),
            'streams':{name:{'rows':len(rows),'sha256':file_hash(dest/(name+'.jsonl'))} for name,rows in streams.items()},
            'availability':'offline source horizon only; live processing/commit latency not modeled',
            'sampling':'six sparse state frames per episode; not dense temporal ground truth',
            'consumption':'Choose one producer/condition; never concatenate alternative predictions as independent evidence. Oracle stream is diagnostic only.'}
    write_json(dest/'manifest.json',output);return output
