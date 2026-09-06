"""Own an isolated simulator port and log for the paired-action corpus."""
from pathlib import Path
import json,os,plistlib
root=Path('output/virtualhome-install').resolve();app=Path(json.loads((root/'installation.json').read_text())['app']);info=plistlib.loads((app/'Contents/Info.plist').read_bytes());exe=app/'Contents/MacOS'/info['CFBundleExecutable']
out=Path('output/action-benchmark-v1').resolve();out.mkdir(exist_ok=True)
os.execv(str(exe),[str(exe),'-http-port=18084','-screen-width','960','-screen-height','720','-logFile',str(out/'unity.log')])
