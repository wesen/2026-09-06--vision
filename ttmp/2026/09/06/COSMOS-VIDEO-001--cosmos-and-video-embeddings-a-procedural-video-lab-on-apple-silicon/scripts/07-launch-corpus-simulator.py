"""Launch an owned simulator with an isolated log; keep graphics enabled."""
from pathlib import Path
import argparse, os, plistlib, socket
p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=18081)
a=p.parse_args()
root=Path('output/virtualhome-install').resolve()
with socket.socket() as sock:
 if sock.connect_ex(('127.0.0.1',a.port))==0:
  raise SystemExit(f'Port {a.port} is already owned; choose another port')
app=next((root/'simulator').glob('*.app'))
info=plistlib.loads((app/'Contents/Info.plist').read_bytes())
exe=app/'Contents/MacOS'/info['CFBundleExecutable']
logs=Path('output/virtualhome-corpus').resolve(); logs.mkdir(parents=True,exist_ok=True)
os.execv(str(exe),[str(exe),f'-http-port={a.port}','-batchmode','-screen-width','960','-screen-height','720','-logFile',str(logs/f'unity-{a.port}.log')])
