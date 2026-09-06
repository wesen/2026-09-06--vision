"""Local video workbench command line."""
import argparse
import json
from .registry import Registry


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='output/video-workbench/registry.sqlite')
    commands=p.add_subparsers(dest='command',required=True)
    ingest=commands.add_parser('ingest');ingest.add_argument('manifest')
    inspect=commands.add_parser('inspect');inspect.add_argument('--split')
    args=p.parse_args()
    registry=Registry(args.db)
    try:
        if args.command=='ingest':result=registry.ingest(args.manifest)
        elif args.command=='inspect':
            result=[{k:v for k,v in r.items() if k!='media'}|{'media':{k:v for k,v in r['media'].items() if k not in ('pts_us','raw_pts')}} for r in registry.episodes(args.split)]
        print(json.dumps(result,indent=2))
    finally:registry.close()


if __name__=='__main__':main()
