"""Validate the prepared article and copy only new note/assets into go-go-parc.

Git staging, commit, and push are explicit separate operations. Existing vault
files are never replaced. Run without --copy-to-vault for read-only validation.
"""
import argparse
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import yaml

ROOT=Path(__file__).resolve().parents[6]
TICKET=Path(__file__).resolve().parent.parent
DRAFT=ROOT/'output/vault-report'
NAME='ARTICLE - Timestamped Video Search - From Verified Pixels to Frozen Evaluation.md'
VAULT=Path('/Users/manuel/code/wesen/go-go-golems/go-go-parc')
DEST=VAULT/'Projects/2026/09/06'
ASSETS={
 '01-corpus-before-search.png':'video-search-01-corpus-gallery.png',
 '02-first-search-and-seek.png':'video-search-02-first-search.png',
 '03-selected-index-test-playback.png':'video-search-03-selected-index.png',
 '04-frozen-evaluation-report.png':'video-search-04-evaluation.png',
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--copy-to-vault',action='store_true');args=parser.parse_args()
    text=(DRAFT/NAME).read_text()
    assert text.startswith('---\n')
    metadata=yaml.safe_load(text.split('---',2)[1])
    assert metadata['type']=='article' and metadata['implementation_revision']=='cc58db0'
    assert len(text.split())>5000
    assert text.count('```')%2==0 and text.count('```mermaid')==3
    assert not re.search(r'\b(think of this as|imagine a|like a traffic|like a kitchen)\b',text,re.I)
    expected={f'_assets/{name}' for name in ASSETS.values()}
    embeds=set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text));assert embeds==expected
    for source,name in ASSETS.items():
        image=TICKET/'various/screenshots'/source
        assert image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        target=DRAFT/'_assets'/name
        if not target.exists():shutil.copy2(image,target)
        assert sha(target)==sha(image)
    for link in re.findall(r'\[\[([^\]|]+)',text):
        assert list(VAULT.rglob(link+'.md')),f'unresolved wiki link: {link}'
    test=json.loads((TICKET/'various/evaluation/test-report.json').read_text())
    assert test['evaluation']['metrics']['5']['success']==.75
    assert test['evaluation']['metrics']['5']['interval_recall']==.6875
    # Analytical explanation of already-frozen labels; no new model ranking.
    probabilities=[1-math.comb(14-r,5)/math.comb(14,5) for r in (4,2,4,2)]
    report={'draft':str(DRAFT/NAME),'destination':str(DEST/NAME),'words':len(text.split()),
        'mermaid_diagrams':3,'screenshots':4,'article_sha256':sha(DRAFT/NAME),
        'assets':{name:sha(DRAFT/'_assets'/name) for name in ASSETS.values()},
        'analytical_random_success_at_5':sum(probabilities)/4,
        'observed_random_success_at_5':test['evaluation']['random_success_at_5'],
        'implementation_revision':'cc58db0','copied':False}
    if args.copy_to_vault:
        targets=[(DRAFT/NAME,DEST/NAME)]+[(DRAFT/'_assets'/name,DEST/'_assets'/name) for name in ASSETS.values()]
        for source,target in targets:
            if target.exists():raise FileExistsError(f'append-only destination already exists: {target}')
        (DEST/'_assets').mkdir(parents=True,exist_ok=True)
        for source,target in targets:
            with target.open('xb') as f:f.write(source.read_bytes())
            assert sha(source)==sha(target)
        report['copied']=True
    (TICKET/'various/vault-article-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
