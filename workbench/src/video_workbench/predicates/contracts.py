"""Strict labels and observations: unknown is distinct from false and missing."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import re
from video_workbench.registry import file_hash


@dataclass(frozen=True)
class StateLabel:
    sample_id: str
    entity_id: str
    property: str
    value: bool | None
    observability: str
    reviewer: str
    revision: str
    provenance: str
    rationale: str

    def __post_init__(self):
        if self.property != 'door_open':
            raise ValueError('unsupported property')
        if self.observability not in {'visible', 'ambiguous', 'occluded', 'out_of_frame'}:
            raise ValueError('invalid observability')
        if self.value is not None and type(self.value) is not bool:
            raise ValueError('state value must be bool or null')
        if (self.value is not None) != (self.observability == 'visible'):
            raise ValueError('unknown and observability disagree')
        if self.provenance != 'reviewed_rgb' or not all((self.sample_id, self.entity_id, self.reviewer, self.revision, self.rationale)):
            raise ValueError('review provenance required')


@dataclass(frozen=True)
class StateObservation:
    sample_id: str
    episode_id: str
    entity_id: str
    property: str
    sample_us: int
    available_us: int
    availability_source: str
    value: bool | None
    raw_score: float | None
    calibrated_probability: float | None
    unknown_reason: str | None
    evidence_ids: tuple[str, ...]
    feature_space_id: str
    producer_id: str

    def __post_init__(self):
        import math
        if self.sample_us < 0 or self.available_us < self.sample_us:
            raise ValueError('invalid observation time')
        if type(self.value) not in (bool, type(None)):
            raise ValueError('invalid state value')
        if (self.value is None) != bool(self.unknown_reason):
            raise ValueError('unknown requires reason')
        if self.raw_score is None or self.calibrated_probability is None:
            if self.value is not None or self.raw_score is not None or self.calibrated_probability is not None:
                raise ValueError('missing evidence requires paired null scores and unknown value')
        elif not math.isfinite(self.raw_score) or not 0 <= self.calibrated_probability <= 1:
            raise ValueError('invalid score or probability')
        if not self.evidence_ids or not self.feature_space_id or not self.producer_id:
            raise ValueError('evidence and producer required')


def validate_samples(samples, root=Path('.'), verify_files=True):
    seen, groups, sources, episodes = set(), {}, {}, {}
    for s in samples:
        if s['sample_id'] in seen:
            raise ValueError('duplicate sample')
        seen.add(s['sample_id'])
        if s['sample_us'] < 0 or s['frame_index'] < 0:
            raise ValueError('invalid sample time')
        if s['split'] not in {'train', 'development', 'test'}:
            raise ValueError('invalid split')
        if s['entity_class'] not in {'fridge', 'microwave'} or s['property'] != 'door_open':
            raise ValueError('unsupported entity/property')
        if not s['entity_id'].startswith(s['episode_id'] + ':object-'):
            raise ValueError('entity mismatch')
        for table, key in ((groups, s['split_group']), (sources, s['video_sha256']), (episodes, s['episode_id'])):
            if table.setdefault(key, s['split']) != s['split']:
                raise ValueError('cross-split source/group leakage')
        for kind in ('image', 'video'):
            sha = s[kind + '_sha256']
            if not re.fullmatch('[0-9a-f]{64}', sha):
                raise ValueError('invalid source hash')
            path = (root / s[kind]).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError('source outside root')
            if verify_files and file_hash(path) != sha:
                raise ValueError(f'{kind} source hash mismatch')


def load_dataset(samples_path, labels_path, root=Path('.'), verify_files=True):
    samples = json.loads(Path(samples_path).read_text())
    validate_samples(samples, root, verify_files)
    labels = [StateLabel(**r) for r in json.loads(Path(labels_path).read_text())]
    by_id = {r.sample_id: r for r in labels}
    if len(by_id) != len(labels) or set(by_id) != {s['sample_id'] for s in samples}:
        raise ValueError('duplicate, missing, or extra labels; missing is not unknown')
    ordered = []
    for s in samples:
        label = by_id[s['sample_id']]
        if (label.entity_id, label.property) != (s['entity_id'], s['property']):
            raise ValueError('label entity/property mismatch')
        ordered.append(label)
    return samples, ordered
