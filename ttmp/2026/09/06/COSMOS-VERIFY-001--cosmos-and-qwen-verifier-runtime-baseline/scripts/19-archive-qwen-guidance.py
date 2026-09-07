"""Archive pinned Qwen guidance; notebooks are never executed."""
from pathlib import Path
import urllib.request,json,hashlib
root=Path(__file__).resolve().parents[1]/'sources/qwen3-vl';root.mkdir(parents=True,exist_ok=True)
rev='96588727e44c78b25ba03ea03b8e12f7e64fd0da'
paths=['README.md','LICENSE','qwen-vl-utils/README.md','qwen-vl-utils/src/qwen_vl_utils/vision_process.py','cookbooks/video_understanding.ipynb','cookbooks/2d_grounding.ipynb','cookbooks/spatial_understanding.ipynb','cookbooks/think_with_images.ipynb','evaluation/VideoMME/README.md','evaluation/RealWorldQA/README.md']
records=[]
def save(url,name):
 data=urllib.request.urlopen(url,timeout=60).read();p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 records.append(dict(url=url,local=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 if name.endswith('.ipynb'):
  notebook=json.loads(data);text='\n\n'.join('## Cell '+str(i)+' ('+c['cell_type']+')\n\n'+''.join(c['source']) for i,c in enumerate(notebook['cells']))
  p.with_suffix('.cells.md').write_text(text+'\n')
for p in paths:save(f'https://raw.githubusercontent.com/QwenLM/Qwen3-VL/{rev}/{p}',p)
for model in ['Qwen/Qwen3-VL-8B-Instruct','Qwen/Qwen3-VL-8B-Thinking','mlx-community/Qwen3-VL-8B-Instruct-8bit']:
 sha='a0093b9b5fda6f76ddd4a462c6830ae7c4fe47ec' if model.startswith('mlx-community') else json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+model))['sha']
 for name in ['README.md','generation_config.json']:
  save(f'https://huggingface.co/{model}/resolve/{sha}/{name}',model.replace('/','--')+'/'+name)
(root/'provenance.json').write_text(json.dumps(dict(repository_revision=rev,files=records),indent=2)+'\n')
print('Archived',len(records),'original sources plus notebook text derivatives')
