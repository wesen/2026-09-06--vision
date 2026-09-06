"""Source-hashed RGB review records; graph state is never accepted as visual truth."""
from dataclasses import dataclass, asdict
from typing import Literal


@dataclass(frozen=True)
class StateLabel:
    sample_id: str
    episode_id: str
    entity_id: str
    entity_class: Literal['fridge','microwave']
    property: str
    sample_us: int
    video_sha256: str
    image_sha256: str
    split: Literal['train','development','test']
    split_group: str
    value: bool | None
    observability: Literal['visible','occluded','out_of_frame','ambiguous']
    label_source: str
    reviewer: str
    review_revision: str
    rationale: str

    def validate(self):
        if self.entity_class not in ('fridge','microwave') or self.property!='door_open':
            raise ValueError('unsupported entity/property')
        if self.sample_us<0:raise ValueError('invalid sample time')
        if self.observability not in ('visible','occluded','out_of_frame','ambiguous'):
            raise ValueError('invalid observability')
        if self.observability!='visible' and self.value is not None:
            raise ValueError('unusable visibility requires unknown state')
        if self.observability=='visible' and type(self.value) is not bool:
            raise ValueError('visible state requires a reviewed boolean')
        if self.label_source!='reviewed_rgb' or not all((self.reviewer,self.review_revision,self.rationale)):
            raise ValueError('review provenance required')
        if self.split not in ('train','development','test'):raise ValueError('invalid split')
        return asdict(self)
