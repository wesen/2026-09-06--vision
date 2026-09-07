"""Readable data presentation and inference-free prompt preview."""
import hashlib
import yaml
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter
from video_workbench.verifiers.profiles import make_profile
from video_workbench.verifiers.visibility import experiment_prompt_text

class ReadableDumper(yaml.SafeDumper):
    pass

def string(dumper, value):
    return dumper.represent_scalar('tag:yaml.org,2002:str',value,style='|' if '\n' in value else None)

ReadableDumper.add_representer(str,string)

def highlighted_yaml(value):
    text=yaml.dump(value,Dumper=ReadableDumper,sort_keys=False,allow_unicode=True,width=100)
    formatter=HtmlFormatter(style='monokai',noclasses=True)
    return dict(yaml=text,html=highlight(text,YamlLexer(),formatter))

def reasoning_prompt(options):
    profile=make_profile(options.model,reasoning=options.reasoning)
    text=options.prompt if options.prompt is not None else experiment_prompt_text(options.target,profile)
    return dict(prompt=text,system_prompt=profile['system_prompt'],custom=options.prompt is not None,
                sha256=hashlib.sha256(text.encode()).hexdigest(),
                scope='User message before the model chat template; image F1 is supplied separately. The parser still expects the door-state schema.')
