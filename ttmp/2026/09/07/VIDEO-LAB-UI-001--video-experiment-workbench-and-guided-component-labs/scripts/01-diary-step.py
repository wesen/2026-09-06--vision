"""Append a skill-format diary step from a JSON file supplied by the operator."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=json.loads(Path(sys.argv[1]).read_text())
p=root/'reference/01-implementation-diary.md'
with p.open('a') as f:
    f.write(f'\n## Step {s["number"]}: {s["title"]}\n\n{s["intro"]}\n\n### Prompt Context\n\n**User prompt (verbatim):** (see Step 1)\n\n**Assistant interpretation:** {s["interpretation"]}\n\n**Inferred user intent:** Make experimental evidence understandable and reproducible.\n')
    if s.get('commit'): f.write(f'\n**Commit (code):** {s["commit"]}\n')
    for title in ['What I did','Why','What worked',"What didn't work",'What I learned','What was tricky to build','What warrants a second pair of eyes','What should be done in the future','Code review instructions','Technical details']:
        f.write('\n### '+title+'\n\n'+s.get(title,'N/A')+'\n')
