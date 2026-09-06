import argparse,json
from .data import prepare,review_sheets
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
a=sub.add_parser('prepare');a.add_argument('--state',required=True);a.add_argument('--pilot',required=True);a.add_argument('--out',required=True)
a=sub.add_parser('review');a.add_argument('--dataset',required=True);a.add_argument('--out',required=True)
a=p.parse_args()
print(json.dumps(prepare(a.state,a.pilot,a.out) if a.command=='prepare' else review_sheets(a.dataset,a.out)))
