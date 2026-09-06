"""Flat household rule templates. No model calls, I/O, or revision machinery."""
from dataclasses import dataclass
import hashlib
import json


def integer(value):return type(value) is int and value>=0


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Event:
    id: str
    episode_id: str
    entity_id: str
    stream_id: str
    name: str
    lo_us: int
    hi_us: int
    available_us: int
    committed_us: int

    def validate(self):
        if not all(isinstance(v,str) and v for v in (self.id,self.episode_id,self.entity_id,self.stream_id,self.name)):raise ValueError('event identity required')
        if not all(integer(v) for v in (self.lo_us,self.hi_us,self.available_us,self.committed_us)) or not self.lo_us<=self.hi_us<=self.available_us<=self.committed_us:raise ValueError('invalid event clocks')
        return self


@dataclass(frozen=True)
class Coverage:
    id: str
    episode_id: str
    entity_id: str
    stream_id: str
    event_name: str
    start_us: int
    end_us: int
    available_us: int
    committed_us: int
    origin: str

    def validate(self):
        if not all(isinstance(v,str) and v for v in (self.id,self.episode_id,self.entity_id,self.stream_id,self.event_name)):raise ValueError('coverage identity required')
        if not all(integer(v) for v in (self.start_us,self.end_us,self.available_us,self.committed_us)) or not self.start_us<self.end_us<=self.available_us<=self.committed_us:raise ValueError('invalid coverage clocks')
        if self.origin not in ('oracle','reviewed'):raise ValueError('coverage must be explicitly oracle or reviewed')
        return self


def validate_rule(rule):
    base={'schema_version','rule_id','op','event_stream'}
    fields={'state_at_event':{'event_id','state_stream','property','expected'},
            'before':{'first_event_id','second_event_id'},
            'no_event_in':{'event_name','start_us','end_us'}}
    if not isinstance(rule,dict) or rule.get('op') not in fields:raise ValueError('unknown rule template')
    if set(rule)!=base|fields[rule['op']] or type(rule['schema_version']) is not int or rule['schema_version']!=1:raise ValueError('rule schema fields/version invalid')
    for k,v in rule.items():
        if k not in ('schema_version','expected','start_us','end_us') and (not isinstance(v,str) or not v):raise ValueError('rule string fields required')
    if rule['op']=='state_at_event' and type(rule['expected']) is not bool:raise ValueError('expected must be boolean')
    if rule['op']=='no_event_in' and (not integer(rule['start_us']) or not integer(rule['end_us']) or not rule['start_us']<rule['end_us']):raise ValueError('positive bounded interval required')
    return rule


def evaluate(rule,episode_id,entity_id,events=(),observations=(),coverage=(),as_of_us=0):
    validate_rule(rule)
    if not integer(as_of_us) or not episode_id or not entity_id:raise ValueError('query identity and integer horizon required')
    for records in (events,coverage):
        ids=[]
        for r in records:r.validate();ids.append(r.id)
        if len(ids)!=len(set(ids)):raise ValueError('duplicate evidence identity')
    for o in observations:o.validate()
    if len({o.run_id for o in observations})>1:raise ValueError('one run per observation snapshot required')
    selected=[o for o in observations if o.stream_id==rule.get('state_stream')]
    if len({(o.producer,o.feature_space_id,o.mode) for o in selected})>1:raise ValueError('mixed producers in selected state stream')
    visible=lambda r:r.available_us<=as_of_us and r.committed_us<=as_of_us
    es=[e for e in events if visible(e) and e.episode_id==episode_id and e.entity_id==entity_id and e.stream_id==rule['event_stream']]
    used=[]
    def decision(status,reason,applicability='observed'):
        result={'rule_id':rule['rule_id'],'rule_sha256':digest(rule),'episode_id':episode_id,'entity_id':entity_id,
                'as_of_us':as_of_us,'status':status,'reason':reason,'applicability':applicability,
                'evidence_ids':sorted(set(used)),'evaluator_version':'flat-rules-v1'}
        return dict(result,evaluation_id=digest(result))
    def event(id):return next((e for e in es if e.id==id),None)
    if rule['op']=='state_at_event':
        e=event(rule['event_id'])
        if e is None:return decision('UNKNOWN','trigger_not_observed','not_observed')
        used.append(e.id)
        if e.lo_us!=e.hi_us:return decision('UNKNOWN','uncertain_trigger_requires_interval_evidence')
        rows=[o for o in observations if visible(o) and o.episode_id==episode_id and o.entity==entity_id and o.property==rule['property'] and o.stream_id==rule['state_stream'] and o.event_us==e.lo_us]
        used.extend(o.observation_id for o in rows)
        if not rows:return decision('UNKNOWN','no_exact_state_sample')
        if any(o.value is None for o in rows):return decision('UNKNOWN','source_unknown')
        if any(type(o.value) is not bool for o in rows):return decision('UNKNOWN','non_boolean_state')
        if len({o.value for o in rows})>1:return decision('UNKNOWN','disagreeing_samples')
        return decision('PASS' if rows[0].value==rule['expected'] else 'VIOLATION','observed_state_match' if rows[0].value==rule['expected'] else 'observed_state_mismatch')
    if rule['op']=='before':
        a=event(rule['first_event_id']);b=event(rule['second_event_id'])
        used.extend(e.id for e in (a,b) if e)
        if a is None or b is None:return decision('UNKNOWN','required_event_not_observed','not_observed')
        if a.hi_us<b.lo_us:return decision('PASS','strictly_before')
        if a.lo_us>=b.hi_us:return decision('VIOLATION','not_strictly_before')
        return decision('UNKNOWN','overlapping_event_uncertainty')
    start,end=rule['start_us'],rule['end_us']
    relevant=[e for e in es if e.name==rule['event_name'] and e.hi_us>=start and e.lo_us<end]
    certain=[e for e in relevant if start<=e.lo_us and e.hi_us<end]
    if certain:
        used.extend(e.id for e in certain);return decision('VIOLATION','prohibited_event_observed')
    if relevant:
        used.extend(e.id for e in relevant);return decision('UNKNOWN','event_overlaps_interval_boundary')
    if as_of_us<end:return decision('UNKNOWN','interval_not_finished')
    spans=sorted((c for c in coverage if visible(c) and c.episode_id==episode_id and c.entity_id==entity_id and c.stream_id==rule['event_stream'] and c.event_name==rule['event_name'] and c.end_us>start and c.start_us<end),key=lambda c:(c.start_us,c.end_us,c.id))
    cursor=start
    for c in spans:
        used.append(c.id)
        if c.start_us>cursor:return decision('UNKNOWN','event_coverage_gap')
        cursor=max(cursor,c.end_us)
        if cursor>=end:return decision('PASS','covered_event_absence')
    return decision('UNKNOWN','event_coverage_gap')
