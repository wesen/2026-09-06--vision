#!/usr/bin/env python3
"""Rasterize all guide pages and build contact sheets; do not assert visual approval."""
import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'various/project-tickets.json').read_text())
for r in records:
    out=Path('output/pdf/project-guides')/r['ticket']
    pdf=out/(r['ticket']+'_Intern_Guide.pdf')
    qa=out/'qa';qa.mkdir(exist_ok=True)
    subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=png16m','-r90',
                    '-sOutputFile='+str(qa/'page-%03d.png'),str(pdf)],check=True,capture_output=True)
    subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=txtwrite',
                    '-sOutputFile='+str(qa/'text.txt'),str(pdf)],check=True,capture_output=True)
    bbox=subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=bbox',str(pdf)],check=True,capture_output=True,text=True)
    (qa/'bbox.txt').write_text(bbox.stderr)
    pages=sorted(qa.glob('page-*.png'))
    text=(qa/'text.txt').read_text()
    assert len(text)>5000 and 'Implementation phases' in text
    sheets=[]
    for start in range(0,len(pages),9):
        chunk=pages[start:start+9]
        sheet=Image.new('RGB',(1050,((len(chunk)+2)//3)*480),'#ccc')
        draw=ImageDraw.Draw(sheet)
        for j,page in enumerate(chunk):
            with Image.open(page) as image:
                image.thumbnail((340,450))
                x,y=(j%3)*350,(j//3)*480
                sheet.paste(image,(x,y+25))
                draw.text((x+5,y+6),r['ticket']+' / '+page.stem,fill='black')
        dest=qa/f'contact-{start//9+1}.jpg';sheet.save(dest,quality=92);sheets.append(str(dest))
    source=Path(r['guide'])
    result={'ticket':r['ticket'],'pdf':str(pdf.resolve()),'pages':len(pages),
            'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'renderer':'remarquee/Pandoc/XeLaTeX; Helvetica/Menlo; 11pt; 0.8in margins',
            'qa_renderer':'Ghostscript 90 dpi PNG and text extraction','contact_sheets':sheets,
            'visual_review':'pending','scope':'Documentation layout review, not application execution'}
    (Path(r['path'])/'various/pdf-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(r['ticket'],len(pages),'pages',sheets,flush=True)
