import argparse,json
from .data import prepare,review_sheets
from .review import render_overlays
from .detector_audit import audit
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
a=sub.add_parser('prepare');a.add_argument('--state',required=True);a.add_argument('--pilot',required=True);a.add_argument('--out',required=True)
a=sub.add_parser('review');a.add_argument('--dataset',required=True);a.add_argument('--out',required=True)
a=sub.add_parser('overlays');a.add_argument('--dataset',required=True);a.add_argument('--reviews',required=True);a.add_argument('--out',required=True)
a=sub.add_parser('audit');a.add_argument('--dataset',required=True);a.add_argument('--reviews',required=True);a.add_argument('--detector',required=True);a.add_argument('--out',required=True)
a=p.parse_args()
if a.command=='prepare': result=prepare(a.state,a.pilot,a.out)
elif a.command=='review': result=review_sheets(a.dataset,a.out)
elif a.command=='overlays': result=render_overlays(a.dataset,a.reviews,a.out)
else: result=audit(a.dataset,a.reviews,a.detector,a.out)
print(json.dumps(result))
