"""Validated finite local experiment configuration."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Selection(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    episode_id: str=Field(min_length=1,max_length=100)
    start_us: int=Field(default=0,ge=0)
    end_us: int=Field(default=2000000,gt=0)
    fps: float=Field(default=1,gt=0,le=30)
    crop: tuple[float,float,float,float]|None=None

    @model_validator(mode='after')
    def valid(self):
        if self.end_us<=self.start_us: raise ValueError('end must follow start')
        if self.crop:
            x0,y0,x1,y1=self.crop
            if not (0<=x0<x1<=1 and 0<=y0<y1<=1): raise ValueError('crop must be normalized ordered coordinates')
        return self

class Handoff(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    run_id: str=Field(pattern=r'^run-[a-f0-9]{16}$')
    frame_id: str=Field(pattern=r'^frame-[0-9]+$')
    detection_id: str=Field(min_length=1,max_length=100)
    padding: float=Field(default=.15,ge=0,le=1)

class Experiment(Selection):
    handoff: Handoff|None=None
    component: Literal['detection','segmentation','tracking','reasoning','states','embeddings','actions']='detection'
    model: Literal['yolo11n','yolo11n-seg','qwen','cosmos','pooled_images','native_video','native_ridge','pooled_ridge']='yolo11n'
    device: Literal['cpu','mps']='mps'
    confidence: float=Field(default=.25,ge=.01,le=1)
    iou: float=Field(default=.7,gt=0,le=1)
    image_size: Literal[320,640,960]=640
    classes: list[int]=Field(default_factory=list,max_length=80)
    target: str=Field(default='refrigerator',min_length=1,max_length=100)
    reasoning: bool=False
    max_tokens: int=Field(default=512,ge=64,le=4096)
    deadline_seconds: int=Field(default=120,ge=1,le=600)
    window_seconds: float=Field(default=2,ge=.1,le=30)
    stride_seconds: float=Field(default=1,ge=.1,le=30)
    query: str=Field(default='A person opens a refrigerator',min_length=1,max_length=500)
    max_gap_seconds: float=Field(default=2,gt=0,le=30)

    @model_validator(mode='after')
    def supported(self):
        models={'actions':{'native_ridge','pooled_ridge'},'detection':{'yolo11n'},'segmentation':{'yolo11n-seg'},'tracking':{'yolo11n'},
                'reasoning':{'qwen','cosmos'},'states':{'qwen','cosmos'},'embeddings':{'pooled_images','native_video'}}
        if self.model not in models[self.component]: raise ValueError('unsupported component/model combination')
        if any(c<0 or c>79 for c in self.classes): raise ValueError('class IDs must be in 0..79')
        if self.component=='embeddings' and (self.end_us-self.start_us)/(self.stride_seconds*1e6)>128: raise ValueError('selection exceeds 128 window budget')
        if self.component=='embeddings' and not self.query.strip(): raise ValueError('query must not be blank')
        if self.component=='actions' and (self.fps!=2 or self.crop is not None or self.start_us%500000 or self.end_us%500000): raise ValueError('frozen action heads require full frame, 2 FPS and range endpoints on 0.5-second grid')
        return self
