"""Render/review/deliver both new guides; upload requires recorded visual approval."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('mode',choices=['render','dry-run','upload']);p.add_argument('--ticket');a=p.parse_args()
base=Path('ttmp/2026/09/06');umbrella=next(base.glob('COSMOS-VIDEO-001*'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for tid in ('VIDEO-ACTIONS-001','VIDEO-LOCALIZATION-001'):
 if a.ticket and a.ticket!=tid:continue
 ticket=next(base.glob(tid+'*'));guide=ticket/'design-doc/01-intern-analysis-design-and-implementation-guide.md';out=Path('output/pdf/next-guides')/tid;out.mkdir(parents=True,exist_ok=True)
 header=ticket/'scripts/pdf-header.tex'
 if a.mode=='render':header.write_text((umbrella/'scripts/04-pdf-header.tex').read_text().replace('COSMOS-VIDEO-001',tid))
 cmd=['remarquee','upload','md',str(guide.resolve()),'--name',tid+' Intern Guide','--remote-dir','/ai/2026/09/06/'+tid,'--pandoc',str((umbrella/'scripts/05-pdf-pandoc.sh').resolve()),'--pdf-engine','/Library/TeX/texbin/xelatex','--mainfont','Helvetica','--monofont','Menlo','--geometry','margin=0.8in','--latex-header-file',str(header.resolve()),'--non-interactive']
 if a.mode=='render':cmd+=['--pdf-only','--output-dir',str(out.resolve())]
 elif a.mode=='dry-run':cmd+=['--dry-run']
 else:
  review=json.loads((ticket/'various/pdf-validation.json').read_text());dry=json.loads((ticket/'various/upload-dry-run.json').read_text());assert review['visual_review']=='passed' and review['source_sha256']==sha(guide)==dry['source_sha256'] and dry['returncode']==0
 env=dict(os.environ);env['PATH']='/Library/TeX/texbin:'+env['PATH'];r=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=240)
 receipt={'mode':a.mode,'ticket':tid,'returncode':r.returncode,'source_sha256':sha(guide),'output':r.stdout+r.stderr,'remote_dir':'/ai/2026/09/06/'+tid};(out/(a.mode+'.log')).write_text(receipt['output']);print(tid,a.mode,receipt['output'][-800:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
 if a.mode!='render':
  if a.mode=='upload':assert 'OK: uploaded' in receipt['output']
  (ticket/'various'/('upload-dry-run.json' if a.mode=='dry-run' else 'remarkable-upload.json')).write_text(json.dumps(receipt,indent=2)+'\n');continue
 pdf=out/(tid+'_Intern_Guide.pdf');qa=out/'qa';qa.mkdir(exist_ok=True)
 subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=png16m','-r90','-sOutputFile='+str(qa/'page-%03d.png'),str(pdf)],check=True,capture_output=True)
 subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=txtwrite','-sOutputFile='+str(qa/'text.txt'),str(pdf)],check=True,capture_output=True)
 text=(qa/'text.txt').read_text();assert 'Implementation phases' in text and len(text)>10000
 pages=sorted(qa.glob('page-*.png'));sheets=[]
 for start in range(0,len(pages),6):
  chunk=pages[start:start+6];im=Image.new('RGB',(1100,((len(chunk)+1)//2)*730),'#ccc');draw=ImageDraw.Draw(im)
  for j,page in enumerate(chunk):
   img=Image.open(page);img.thumbnail((540,700));x,y=(j%2)*550,(j//2)*730;im.paste(img,(x,y+25));draw.text((x+5,y+5),tid+' / '+page.stem,fill='black')
  path=qa/f'contact-{start//6+1}.jpg';im.save(path,quality=92);sheets.append(str(path))
 (ticket/'various/pdf-validation.json').write_text(json.dumps({'source_sha256':sha(guide),'pdf_sha256':sha(pdf),'pdf':str(pdf),'pages':len(pages),'contact_sheets':sheets,'visual_review':'pending'},indent=2)+'\n');print(sheets,flush=True)
