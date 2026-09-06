#!/usr/bin/env python3
"""Rasterize the PDF and collect review evidence without asserting approval."""
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
out=Path('output/pdf/MLX-VIDEO-FIX-001').resolve();qa=out/'qa';qa.mkdir(exist_ok=True)
pdf=out/'MLX-VIDEO-FIX-001_Intern_Guide.pdf'
for device,name in [('png16m','page-%03d.png'),('txtwrite','text.txt')]:
 subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE='+device,'-r90','-sOutputFile='+str(qa/name),str(pdf)],check=True,capture_output=True)
bbox=subprocess.run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=bbox',str(pdf)],check=True,capture_output=True,text=True)
(qa/'bbox.txt').write_text(bbox.stderr)
pages=sorted(qa.glob('page-*.png'));sheets=[]
for start in range(0,len(pages),9):
 chunk=pages[start:start+9];sheet=Image.new('RGB',(1200,((len(chunk)+2)//3)*550),'#ccc');draw=ImageDraw.Draw(sheet)
 for j,page in enumerate(chunk):
  with Image.open(page) as im:
   im.thumbnail((390,515));x,y=(j%3)*400,(j//3)*550;sheet.paste(im,(x,y+25));draw.text((x+8,y+5),page.stem,fill='black')
 dest=qa/f'contact-{start//9+1}.jpg';sheet.save(dest,quality=93);sheets.append(str(dest))
guide=next((root/'design-doc').glob('01-*.md'))
text=(qa/'text.txt').read_text()
assert 'Implementation phases' in text and 'Intern' in text and len(text)>20000
result={'pdf':str(pdf),'pages':len(pages),'source_sha256':hashlib.sha256(guide.read_bytes()).hexdigest(),
 'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'contact_sheets':sheets,
 'visual_review':'pending','scope':'PDF layout review, not runtime validation'}
(root/'various/pdf-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
