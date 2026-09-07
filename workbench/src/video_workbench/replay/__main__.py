"""Run bounded evidence replay or serve the local inspection application."""
import argparse
import json
from .engine import Catalog, Options, ReplayEngine, DEFAULT_RECORDINGS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recordings',default=DEFAULT_RECORDINGS)
    parser.add_argument('--traces',default='output/rules-departure-v1')
    parser.add_argument('--states',default='output/temporal-v1/replay-v1/observations.sqlite')
    parser.add_argument('--output',default='output/replay-workbench')
    commands=parser.add_subparsers(dest='command',required=True)
    run=commands.add_parser('run')
    run.add_argument('episode_id')
    run.add_argument('--mode',choices=['recorded','live_verifier'],default='recorded')
    run.add_argument('--family',choices=['qwen','cosmos'],default='qwen')
    run.add_argument('--speed',type=float,default=1.)
    run.add_argument('--repetitions',type=int,default=1)
    run.add_argument('--max-jobs',type=int,default=16)
    run.add_argument('--max-bytes',type=int,default=16*1024*1024)
    run.add_argument('--perception-deadline-seconds',type=float,default=2.)
    run.add_argument('--verifier-deadline-seconds',type=float,default=120.)
    run.add_argument('--service-multiplier',type=float,default=1.)
    serve=commands.add_parser('serve');serve.add_argument('--port',type=int,default=8775)
    args=parser.parse_args()
    catalog=Catalog(args.recordings,args.traces,args.states)
    if args.command=='run':
        options=Options(**{key:getattr(args,key) for key in Options.__dataclass_fields__})
        engine=ReplayEngine(catalog,args.output,options)
        result=engine.run()
        print(json.dumps(result,indent=2))
        if result['status']!='complete':raise SystemExit(1)
    else:
        import uvicorn
        from .app import create_app
        uvicorn.run(create_app(catalog,args.output),host='127.0.0.1',port=args.port)


if __name__=='__main__':main()
