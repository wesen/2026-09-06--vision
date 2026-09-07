"""Curated reading paths and a read-only Markdown/source browser.

Only indexed project code, ticket documents and ticket raster figures are served.
Resource IDs are hashes of relative paths, never client-supplied filesystem paths.
"""
from pathlib import Path
from hashlib import sha256
from html import escape
from urllib.parse import urlsplit,unquote
import re
from fastapi import HTTPException
from fastapi.responses import HTMLResponse,PlainTextResponse,FileResponse
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_for_filename,get_lexer_by_name,TextLexer
from pygments.formatters import HtmlFormatter

EXTERNAL={
 'shared': [('Presentation timestamps in PyAV','https://pyav.org/docs/stable/api/time.html','Read this to distinguish frame indices, time bases and presentation time. The linked page documents timestamp concepts; installed PyAV version is recorded by our adapters.')],
 'detection':[('YOLO11 model documentation','https://docs.ultralytics.com/models/yolo11/','The checkpoint family used locally; compare model tasks and sizes.')],
 'segmentation':[('Ultralytics instance segmentation','https://docs.ultralytics.com/tasks/segment/','Mask polygons, pixel coordinates and result fields. Current examples may use newer checkpoints; this lab uses YOLO11n-seg.')],
 'tracking':[('Ultralytics tracking guide','https://docs.ultralytics.com/modes/track/','Tracker configuration and association controls; compare with our explicit cadence/reset policy.')],
 'reasoning':[('Qwen3-VL-8B-Instruct model card','https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct','Upstream model capabilities and prompt examples. Our accepted adapter currently uses one image.'),('Cosmos-Reason2-8B model card','https://huggingface.co/nvidia/Cosmos-Reason2-8B','Upstream model information; local 8-bit weights and accepted runtime differ from upstream examples.'),('NVIDIA Cosmos Cookbook','https://nvidia-cosmos.github.io/cosmos-cookbook/','Official recipes and prompting guidance; local guidance reports below explain what transfers to our verifier.')],
 'states':[],
 'embeddings':[('Qwen3-VL-Embedding-2B model card','https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B','Embedding inputs and upstream usage. Read our native repair handoff for the accepted MLX implementation.')],
}
EXTERNAL['states']=EXTERNAL['reasoning']
CODE={
 'shared':[('media.py','PTS decoding and first-frame-at-or-after sampling'),('registry.py','Source hash and partition contracts'),('lab/evidence.py','Exact PNG inputs and crop rounding')],
 'detection':[('perception/detector.py','Detector defaults, RGB contract and output coordinates')],
 'segmentation':[('perception/segmentation.py','Mask extraction and source-image overlays'),('perception/contracts.py','Frame, box and detection identity')],
 'tracking':[('perception/tracking.py','ByteTrack cadence, predicted tracks and reset conditions')],
 'reasoning':[('verifiers/adapter.py','Evidence validation and worker deadlines'),('verifiers/worker.py','Exact prompt preparation and MLX generation'),('verifiers/profiles.py','Generation parameters and profile hashes'),('verifiers/recovery.py','Conservative wrapper recovery')],
 'states':[('temporal/store.py','Exact observations and availability clocks'),('temporal/linear.py','Ridge score computation and feature-space validation'),('rules/evaluate.py','PASS, VIOLATION and UNKNOWN semantics')],
 'embeddings':[('embedding.py','Unit normalization and pooled frame embeddings'),('native_video.py','Repaired native video preprocessing and inference'),('index.py','Compatible vector search and immutable indices')],
}
TICKETS={
 'shared':['VIDEO-LAB-UI-001','VIDEO-CORPUS-001'],
 'detection':['VIDEO-YOLO-001','VIDEO-PERCEPTION-001','VIDEO-LOCALIZATION-001'],
 'segmentation':['VIDEO-YOLO-001','VIDEO-PERCEPTION-001','VIDEO-LOCALIZATION-001'],
 'tracking':['VIDEO-YOLO-001','VIDEO-PERCEPTION-001'],
 'reasoning':['COSMOS-VERIFY-001'],
 'states':['VIDEO-TEMPORAL-001','VIDEO-RULES-001'],
 'embeddings':['VIDEO-SEARCH-001','MLX-VIDEO-FIX-001','COSMOS-EMBED-001'],
}
CSS='''body{margin:0;background:#101619;color:#e6eeeb;font:16px/1.7 system-ui}header{position:sticky;top:0;background:#182226;padding:12px 24px;border-bottom:1px solid #334449;z-index:2}main{max-width:1100px;padding:28px;margin:auto}a{color:#a5ebc8}h1,h2,h3{line-height:1.3;scroll-margin-top:90px}pre{overflow:auto;font:13px/1.6 ui-monospace;padding:12px;background:#182226}code{font-family:ui-monospace;font-size:.9em}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #334449;padding:8px}img{max-width:100%}blockquote{border-left:3px solid #a5ebc8;padding-left:18px;color:#b0c2bd}.meta{font-size:12px;color:#b0c2bd;overflow-wrap:anywhere}.highlight{overflow:auto}.highlight pre{padding:0}.source-line{display:block;scroll-margin-top:90px}.source-line:target{background:#394b30}.line-number{display:inline-block;width:4em;text-align:right;margin-right:1em;color:#8fa5a0;text-decoration:none;user-select:none}nav a{margin-right:20px}details{border:1px solid #334449;padding:12px;margin:15px 0}summary{cursor:pointer}'''

class Resources:
    def __init__(self,root):
        self.root=Path(root).resolve();self.paths={};self.by_path={}
        candidates=list((self.root/'workbench/src/video_workbench').rglob('*.py'))
        candidates+=list((self.root/'workbench/src/video_workbench').rglob('*.html'))
        candidates += [self.root/'workbench/README.md']
        candidates+=[self.root/'workbench/pyproject.toml']
        for ticket in (self.root/'ttmp').glob('*/*/*/*--*'):
            for folder in ('design-doc','reference'):
                candidates+=list((ticket/folder).glob('*.md'))
            for suffix in ('*.png','*.jpg','*.jpeg'):
                candidates+=list((ticket/'various').rglob(suffix))
        for p in candidates:
            resolved=p.resolve()
            if not resolved.is_relative_to(self.root) or not resolved.is_file():continue
            rel=str(resolved.relative_to(self.root));rid=sha256(rel.encode()).hexdigest()[:20]
            self.paths[rid]=resolved;self.by_path[resolved]=rid

    def path(self,rid):
        p=self.paths.get(rid)
        if p is None or not p.is_file() or p.resolve()!=p:raise HTTPException(404,'unknown project resource')
        if p.stat().st_size>10*1024*1024:raise HTTPException(413,'resource exceeds reader size limit')
        return p

    def entry(self,p,why=''):
        rid=self.by_path[p];kind='markdown' if p.suffix=='.md' else 'image' if p.suffix in ('.png','.jpg','.jpeg') else 'source'
        title=p.name
        if kind=='markdown':
            text=p.read_text();match=re.search(r'^Title:\s*(.+)$',text,re.M)
            if match:title=match.group(1).strip('"')
        return dict(id=rid,title=title,path=str(p.relative_to(self.root)),kind=kind,why=why,url='/resources/'+rid,raw_url='/resources/'+rid+'/raw')

    def catalog(self,component=None):
        if component is not None and component not in CODE:raise HTTPException(404,'unknown component')
        if component is None:
            return dict(local=[self.entry(p) for p in self.paths.values() if p.suffix not in ('.png','.jpg','.jpeg')],external=[])
        local=[]
        for filename,why in CODE['shared']+CODE.get(component,[]):
            p=self.root/'workbench/src/video_workbench'/filename
            if p in self.by_path:local.append(self.entry(p,why))
        prefixes=TICKETS['shared']+TICKETS.get(component,[])
        for p in self.paths.values():
            if p.suffix!='.md':continue
            if any(any(part.startswith(prefix+'--') for part in p.parts) for prefix in prefixes):
                if 'design-doc' in p.parts or ('reference' in p.parts and 'diary' not in p.name):
                    local.append(self.entry(p,'Local design or measured report: connects implementation choices to evidence and limitations.'))
        return dict(local=local,external=[dict(title=t,url=u,why=w,checked='2026-09-07') for t,u,w in EXTERNAL['shared']+EXTERNAL.get(component,[])])

    def rewrite(self,url,current):
        parts=urlsplit(url)
        if parts.scheme in ('https','http') or url.startswith('#'):return url
        if parts.scheme or parts.netloc:return None
        path=unquote(parts.path)
        target=Path(path) if path.startswith('/') else current.parent/path
        candidates=[target.resolve(),(self.root/path).resolve()]
        for candidate in candidates:
            rid=self.by_path.get(candidate)
            if rid:return '/resources/'+rid+('#'+parts.fragment if parts.fragment else '')
        return None

    def render(self,rid):
        p=self.path(rid)
        if p.suffix in ('.png','.jpg','.jpeg'):return FileResponse(p)
        text=p.read_text();title=str(p.relative_to(self.root));toc=[]
        def code_block(code,lang,*args):
            try:lexer=get_lexer_by_name(lang)
            except Exception:lexer=TextLexer()
            return highlight(code,lexer,HtmlFormatter())
        if p.suffix=='.md':
            if text.startswith('---\n'):text=text.split('---',2)[-1].lstrip()
            md=MarkdownIt('commonmark',{'html':False,'highlight':code_block}).enable('table')
            tokens=md.parse(text);slugs={}
            def walk(items):
                for i,t in enumerate(items):
                    if t.type=='heading_open':
                        label=items[i+1].content;base=re.sub(r'[^\w\s-]','',label.lower()).strip().replace(' ','-')
                        n=slugs.get(base,0);slugs[base]=n+1;slug=base+(f'-{n}' if n else '')
                        t.attrSet('id',slug);toc.append((label,slug))
                    for attr in ('href','src'):
                        if t.attrGet(attr):
                            rewritten=self.rewrite(t.attrGet(attr),p)
                            if rewritten:t.attrSet(attr,rewritten)
                            else:
                                # Unindexed local references remain visible text, not filesystem links.
                                t.attrSet(attr,'#unavailable-reference');t.attrSet('title','Not in the served project resource catalog')
                    if t.children:walk(t.children)
            walk(tokens)
            body=md.renderer.render(tokens,md.options,{})
            contents='<details><summary>Contents</summary><ul>'+''.join(f'<li><a href="#{escape(s)}">{escape(t)}</a></li>' for t,s in toc)+'</ul></details>'
            body=contents+body
        else:
            try:lexer=get_lexer_for_filename(p.name)
            except Exception:lexer=TextLexer()
            formatted=highlight(text,lexer,HtmlFormatter(nowrap=True)).splitlines()
            body='<div class="highlight"><pre>'+''.join(f'<span class="source-line" id="L{i}"><a class="line-number" href="#L{i}">{i}</a>{line}</span>' for i,line in enumerate(formatted,1))+'</pre></div>'
        styles=CSS+HtmlFormatter(style='monokai').get_style_defs('.highlight')
        page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(p.name)} — Video Laboratory</title><style>{styles}</style><header><nav><a href="/" target="_top">← Laboratory</a><a href="/resources" target="_top">Project browser</a><a href="/resources/{rid}/raw">Raw file</a></nav><div class="meta">{escape(title)} · SHA-256 {sha256(p.read_bytes()).hexdigest()}</div></header><main>{body}</main></html>'''
        return HTMLResponse(page,headers={'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; img-src 'self' https:; base-uri 'none'; frame-ancestors 'self'",'X-Content-Type-Options':'nosniff'})

    def attach(self,app):
        @app.get('/v1/lab/resources')
        def listing(component:str|None=None):return self.catalog(component)
        @app.get('/resources',response_class=HTMLResponse)
        def library():
            return (Path(__file__).parent/'browser.html').read_text()
        @app.get('/resources/{rid}/raw')
        def raw(rid:str):
            p=self.path(rid)
            if p.suffix in ('.png','.jpg','.jpeg'):return FileResponse(p)
            return PlainTextResponse(p.read_text(),headers={'X-Content-Type-Options':'nosniff'})
        @app.get('/resources/{rid}')
        def reader(rid:str):return self.render(rid)
