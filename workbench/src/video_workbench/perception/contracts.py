"""Pure geometry and provenance contracts; no vendor runtime imports."""
from dataclasses import dataclass, asdict
import math
from video_workbench.embedding import digest


def box(values, width, height):
    if len(values) != 4 or not all(math.isfinite(v) for v in values):
        raise ValueError('box must contain four finite coordinates')
    x1,y1,x2,y2=map(float,values)
    if not (0<=x1<x2<=width and 0<=y1<y2<=height):
        raise ValueError('invalid source-coordinate box')
    return (x1,y1,x2,y2)


def iou(a,b):
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    area=lambda r:(r[2]-r[0])*(r[3]-r[1])
    return intersection/(area(a)+area(b)-intersection)


def expand(rect,width,height,margin=.25):
    x1,y1,x2,y2=box(rect,width,height)
    dx,dy=(x2-x1)*margin,(y2-y1)*margin
    return box((max(0,math.floor(x1-dx)),max(0,math.floor(y1-dy)),min(width,math.ceil(x2+dx)),min(height,math.ceil(y2+dy))),width,height)


def union(a,b):
    return (min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3]))


def source_to_crop(point,rect,size):
    return ((point[0]-rect[0])*size[0]/(rect[2]-rect[0]),(point[1]-rect[1])*size[1]/(rect[3]-rect[1]))


def crop_to_source(point,rect,size):
    return (point[0]*(rect[2]-rect[0])/size[0]+rect[0],point[1]*(rect[3]-rect[1])/size[1]+rect[1])


@dataclass(frozen=True)
class FrameRef:
    episode_id:str
    video_sha256:str
    frame_index:int
    raw_pts:int
    time_base:str
    pts_us:int
    width:int
    height:int

    @property
    def id(self):
        return digest(asdict(self))[:24]

    def __post_init__(self):
        if self.frame_index<0 or self.pts_us<0 or min(self.width,self.height)<=0:
            raise ValueError('invalid frame')


@dataclass(frozen=True)
class Detection:
    detection_id:str
    frame_id:str
    producer_id:str
    class_id:int
    class_name:str
    score:float
    xyxy:tuple

    def validate(self,frame):
        box(self.xyxy,frame.width,frame.height)
        if self.frame_id!=frame.id or not 0<=self.score<=1:
            raise ValueError('detection/source mismatch')


def crop_record(frame,rect,producer_id,kind,detection_ids,size=(320,240)):
    rect=box(rect,frame.width,frame.height)
    semantic={'frame_id':frame.id,'video_sha256':frame.video_sha256,'rect':rect,'output_size':size,'interpolation':'PIL-bicubic','producer_id':producer_id,'kind':kind,'detection_ids':detection_ids}
    return dict(semantic,evidence_id=digest(semantic)[:24],source_min_extent=min(rect[2]-rect[0],rect[3]-rect[1]))


def validate_packet(packet,known_evidence,as_of_us):
    start,end=packet['interval_us']
    if not 0<=start<end or packet['available_at_us']>as_of_us:
        raise ValueError('future or invalid packet')
    if len(packet['evidence_ids'])>packet['budget']['max_images']:
        raise ValueError('image budget exceeded')
    pixels=0
    for eid in packet['evidence_ids']:
        if eid not in known_evidence:
            raise ValueError('unknown citation')
        e=known_evidence[eid]
        if e['episode_id']!=packet['episode_id'] or e['video_sha256']!=packet['video_sha256']:
            raise ValueError('packet source mismatch')
        if not start<=e['pts_us']<end or e['pts_us']>as_of_us or e.get('available_at_us',e['pts_us'])>as_of_us:
            raise ValueError('future or out-of-interval evidence')
        pixels+=e['width']*e['height']
    if pixels>packet['budget']['max_pixels']:
        raise ValueError('pixel budget exceeded')


def validate_response(response,packet):
    if type(response.get('value')) not in (bool,type(None)) or 'value' not in response:
        raise ValueError('invalid verifier value')
    if not response.get('evidence_ids') or not set(response['evidence_ids'])<=set(packet['evidence_ids']):
        raise ValueError('unsupported verifier citation')
    if not isinstance(response.get('explanation'),str) or len(response['explanation'])>2000:
        raise ValueError('unbounded verifier explanation')
