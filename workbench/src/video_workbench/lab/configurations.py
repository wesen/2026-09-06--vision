"""Named, immutable experiment drafts stored independently of inference runs."""
import json
import re
import time
import uuid
from pydantic import BaseModel,ConfigDict,Field,field_validator
from .contracts import Experiment
from .handoff import validate
from .presentation import reasoning_prompt
from .manager import write

class SaveConfiguration(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name: str=Field(min_length=1,max_length=100)
    notes: str=Field(default='',max_length=4000)
    options: Experiment

    @field_validator('name')
    @classmethod
    def name_not_blank(cls,value):
        if not value.strip():raise ValueError('configuration name must not be blank')
        return value.strip()

class Configurations:
    def __init__(self,catalog,output):
        self.catalog=catalog;self.output=output;self.directory=output/'configurations'
        self.directory.mkdir(parents=True,exist_ok=True)

    def save(self,request):
        source=self.catalog.get(request.options.episode_id)
        if request.options.end_us>source['media']['duration_us']:
            raise ValueError('range exceeds recording duration')
        validate(self.output,request.options)
        options=request.options.model_dump()
        snapshot=None
        if request.options.component in ('reasoning','states'):
            snapshot=reasoning_prompt(request.options)
            # Freeze even a default template so loading after a code update keeps its text.
            options['prompt']=snapshot['prompt']
        value=dict(schema_version=1,configuration_id='config-'+uuid.uuid4().hex[:16],
                   name=request.name,notes=request.notes,created_unix=time.time(),options=options,
                   source_sha256=source['video_sha256'],source_split=source['split'],prompt_snapshot=snapshot)
        write(self.directory/(value['configuration_id']+'.json'),value)
        return value

    def list(self):
        return sorted((json.loads(p.read_text()) for p in self.directory.glob('config-*.json')),
                      key=lambda v:v['created_unix'],reverse=True)

    def get(self,identifier):
        if not re.fullmatch(r'config-[a-f0-9]{16}',identifier):raise ValueError('unknown configuration')
        path=self.directory/(identifier+'.json')
        if not path.is_file():raise ValueError('unknown configuration')
        value=json.loads(path.read_text())
        source=self.catalog.get(value['options']['episode_id'])
        if (source['video_sha256'],source['split'])!=(value['source_sha256'],value['source_split']):
            raise ValueError('saved configuration source identity changed')
        validate(self.output,Experiment.model_validate(value['options']))
        return value
