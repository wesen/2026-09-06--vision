import argparse
import json
from pathlib import Path
from .features import extract
from .experiment import run

parser=argparse.ArgumentParser(description='Observable-state baseline workbench')
commands=parser.add_subparsers(dest='command',required=True)
p=commands.add_parser('encode')
p.add_argument('--samples',required=True)
p.add_argument('--model',required=True)
p.add_argument('--cache',required=True)
p=commands.add_parser('evaluate')
for name in ('samples','labels','cache','out'):
    p.add_argument('--'+name,required=True)
p=commands.add_parser('serve')
p.add_argument('--run',required=True)
p.add_argument('--port',type=int,default=8772)
args=parser.parse_args()
if args.command=='encode':
    extract(json.loads(Path(args.samples).read_text()),args.model,args.cache)
elif args.command=='evaluate':
    run(args.samples,args.labels,args.cache,args.out)
else:
    import uvicorn
    from .app import create_app
    uvicorn.run(create_app(Path(args.run)),host='127.0.0.1',port=args.port)
