"""Versioned, matched action families across apartments, props, and viewpoints."""
import math
from .core import canonical_hash,camera_rotation

FAMILIES={'door':{'CAN_OPEN'},'pickup':{'GRABBABLE'},'posture':{'SITTABLE'},'switch':{'HAS_SWITCH'}}


def bind(graph,scenario):
    nodes={n['id']:n for n in graph['nodes']}
    target=nodes[scenario['target_id']]
    if target['class_name']!=scenario['target_class'] or not FAMILIES[scenario['family']].issubset(target.get('properties',[])):
        raise ValueError('target binding or affordance mismatch')
    rooms=[nodes[e['to_id']] for e in graph['edges'] if e['from_id']==target['id'] and e['relation_type']=='INSIDE' and nodes[e['to_id']].get('category')=='Rooms']
    if len(rooms)!=1:raise ValueError('target room binding ambiguous')
    supports=[nodes[e['to_id']] for e in graph['edges'] if e['from_id']==target['id'] and e['relation_type']=='ON' and 'SURFACES' in nodes[e['to_id']].get('properties',[])]
    if scenario['family']=='pickup' and not supports:raise ValueError('pickup requires an explicit support surface')
    return target,rooms[0],min(supports,key=lambda n:n['id']) if supports else None


def camera_for(target,room,view):
    if view not in ('left','right'):raise ValueError('unknown view')
    t=target['bounding_box']['center'];center=room['bounding_box']['center'];size=room['bounding_box']['size']
    dx,dz=center[0]-t[0],center[2]-t[2]
    norm=math.hypot(dx,dz)
    if norm<.2:dx,dz,norm=1,0,1
    angle=math.radians(-28 if view=='left' else 28)
    x=(dx*math.cos(angle)-dz*math.sin(angle))/norm
    z=(dx*math.sin(angle)+dz*math.cos(angle))/norm
    position=[t[0]+2.8*x,1.65,t[2]+2.8*z]
    for axis in (0,2):position[axis]=max(center[axis]-size[axis]/2+.35,min(center[axis]+size[axis]/2-.35,position[axis]))
    look=[t[0],max(.85,min(1.1,t[1])),t[2]]
    return {'position':position,'look_at':look,'rotation':camera_rotation(position,look)}


def action(verb,*nodes):
    return '<char0> ['+verb+']'+''.join(f" <{n['class_name']}> ({n['id']})" for n in nodes)


def program_for(family,target,support,condition):
    approach=[action('Walk',target),action('LookAt',target)]
    if condition=='approach_only':return approach+[action('LookAt',target),action('LookAt',target)]
    if condition!='interaction':raise ValueError('unknown condition')
    if family=='door':
        if 'CLOSED' not in target.get('states',[]):raise ValueError('door must start closed')
        operations=[action('Open',target),action('LookAt',target),action('Close',target)]
    elif family=='pickup':operations=[action('Grab',target),action('PutObjBack',target)]
    elif family=='posture':return approach+[action('Sit',target)]
    elif family=='switch':
        on='ON' in target.get('states',[])
        operations=[action('SwitchOff' if on else 'SwitchOn',target),action('LookAt',target),action('SwitchOn' if on else 'SwitchOff',target)]
    else:raise ValueError('unknown family')
    return approach+operations+[action('LookAt',target)]


def plan(cfg):
    if cfg.get('schema_version')!=2:raise ValueError('unsupported diversity config')
    for key in ('fps','width','height'):
        if type(cfg.get(key)) is not int or cfg[key]<=0:raise ValueError('positive integer recording dimensions required')
    if cfg['width']%2 or cfg['height']%2:raise ValueError('even video dimensions required')
    if type(cfg.get('boundary_guard_frames')) is not int or cfg['boundary_guard_frames']<1:raise ValueError('positive boundary guard required')
    scenes=cfg['scenes']
    if len({s['scene_index'] for s in scenes})!=len(scenes):raise ValueError('scene appears in multiple split groups')
    if {s['split'] for s in scenes}!={'train','development','test'}:raise ValueError('three split roles required')
    rows=[]
    for scene in scenes:
        if {s['family'] for s in scene['scenarios']}!=set(FAMILIES):raise ValueError('each scene must contain every family')
        for scenario in scene['scenarios']:
            lineage=canonical_hash([cfg['name'],scene['scene_index'],scenario])
            for condition in ('interaction','approach_only'):
                for view in ('left','right'):
                    key=canonical_hash([lineage,condition,view])
                    rows.append({'episode_id':'dv-'+key[:16],'scene_index':scene['scene_index'],
                        'split':scene['split'],'split_group':f"apartment-{scene['scene_index']}",
                        'scenario':scenario,'condition':condition,'view':view,'lineage_id':lineage,
                        'seed':1000+scene['scene_index']*100})
    if len(rows)>48:raise ValueError('initial expansion limited to 48 episodes')
    return rows
