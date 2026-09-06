import argparse
from .pipeline import detect
p=argparse.ArgumentParser(description='Source-aligned perception artifacts')
sub=p.add_subparsers(dest='command',required=True)
s=sub.add_parser('detect')
for arg in ('manifest','checkpoint','out'):s.add_argument('--'+arg,required=True)
s.add_argument('--device',choices=('cpu','mps'),default='mps')
s=sub.add_parser('derive');s.add_argument('--run',required=True);s.add_argument('--out',required=True)
s=sub.add_parser('serve');s.add_argument('--run',required=True);s.add_argument('--derived',required=True);s.add_argument('--port',type=int,default=8773)
a=p.parse_args()
if a.command=='detect':detect(a.manifest,a.checkpoint,a.out,a.device)
elif a.command=='derive':
    from .derive import derive
    derive(a.run,a.out)
else:
    import uvicorn
    from .app import create_app
    uvicorn.run(create_app(a.run,a.derived),host='127.0.0.1',port=a.port)
