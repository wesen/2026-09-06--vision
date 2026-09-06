#!/usr/bin/env python3
"""Create the eight child ticket workspaces; never overwrite existing documents."""
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
SPECS = [
 ('COSMOS-EMBED-001','Embedding runtime baseline on MLX',[], 'Prove text, image, and video embedding behavior and freeze a feature-space contract.'),
 ('VIDEO-SEARCH-001','Project 1 - Timestamped video search',['COSMOS-EMBED-001'],'Build timestamped retrieval, cache integrity, a local viewer, and split-aware evaluation.'),
 ('VIDEO-STATE-001','Project 2 - Observable state recognition',['COSMOS-EMBED-001','VIDEO-SEARCH-001'],'Measure visual state discrimination, context effects, calibration, and abstention.'),
 ('VIDEO-TEMPORAL-001','Project 3 - Temporal models and durable memory',['VIDEO-SEARCH-001','VIDEO-STATE-001'],'Compare temporal decoders and store availability-aware facts without inventing missing steps.'),
 ('COSMOS-VERIFY-001','Cosmos and Qwen verifier runtime baseline',[],'Compare bounded, evidence-grounded verifier behavior on identical local clips.'),
 ('VIDEO-RULES-001','Project 4 - Temporal rules and bounded investigation',['VIDEO-TEMPORAL-001','COSMOS-VERIFY-001'],'Evaluate typed three-valued rules and audit bounded evidence refinement.'),
 ('VIDEO-REPLAY-001','Project 5 - Replay and incident workbench',['VIDEO-SEARCH-001','VIDEO-STATE-001','VIDEO-TEMPORAL-001','VIDEO-RULES-001'],'Integrate causal replay, incident revisions, a viewer, and held-out real-video evaluation.'),
 ('VIDEO-CORPUS-001','VirtualHome corpus expansion and label calibration',[],'Extend the working VirtualHome corpus with calibrated labels, controlled variations, and verified additional scenes.')]
PROMPT = 'Ok, create the tickets, and Create  a detailed analysis / design / implementation guide that is for a new intern, explaining all the parts of the system needed to understand what it is, with prose paragraphs and bullet point sand pseudocode and diagrams and api references and file references. It should be very clear and technical. Store in the ticket and the nupload to remarkable.'
records=[]
for ticket,title,deps,scope in SPECS:
    found=list(Path('ttmp/2026/09/06').glob(ticket+'--*'))
    if not found:
        for args in [ ['ticket','create-ticket','--ticket',ticket,'--title',title,'--topics','video,embeddings,cosmos'],
                      ['doc','add','--ticket',ticket,'--doc-type','design-doc','--title','Intern analysis design and implementation guide'],
                      ['doc','add','--ticket',ticket,'--doc-type','reference','--title','Design and delivery diary'] ]:
            subprocess.run(['docmgr',*args],check=True,stdout=subprocess.DEVNULL)
        path=next(Path('ttmp/2026/09/06').glob(ticket+'--*'))
        diary=next((path/'reference').glob('*.md'))
        front=diary.read_text().split('---',2)[1]
        diary.write_text('---'+front+'---\n\n'+f'''# Diary

## Goal

Record evidence, design decisions, implementation-task decomposition, and reMarkable delivery for {ticket}. This ticket is a design deliverable now; application implementation remains open.

## Step 1: Establish the project boundary

Created this child of COSMOS-VIDEO-001 and inspected the existing generator, validated corpus, teaching labs, and umbrella guide. The project scope is: {scope} Dependencies are {', '.join(deps) or 'the existing corpus and shared schema agreements; no model ticket is a hard prerequisite'}.

### Prompt Context

**User prompt (verbatim):** "{PROMPT}"

**User prompt (verbatim):** "for each"

**User prompt (verbatim):** "use virtual home instead of habitat btw"

**Assistant interpretation:** Create a separate technical intern guide and executable task breakdown for every project; use VirtualHome for synthetic data.

**Inferred user intent:** Make each project independently understandable, reviewable, and ready for an intern to implement.

### What I did
- Created ticket, guide document, diary, and explicit dependency boundary with docmgr.
- Inspected `src/virtualhome_corpus/core.py`, `runner.py`, the checked configuration, and the corpus inventory.

### Why
- The umbrella checklist is too broad to assign or verify without project-level contracts and acceptance gates.

### What worked
- Existing 24-episode corpus and teaching code provide concrete inputs and API examples.

### What didn't work
- No ticket-creation failure occurred. Runtime APIs are references to verify at implementation time, not measured local model support.

### What I learned
- Current corpus timing is weak supervision; endpoint simulator truth must not become certified pixel labels.

### What was tricky to build
- Avoiding circular dependencies requires shared schema ownership and oracle fixtures before model integration.

### What warrants a second pair of eyes
- Scope boundaries and whether acceptance gates depend on evidence the present corpus cannot provide.

### What should be done in the future
- Complete the project-specific guide, validate its examples and PDF, upload it, then implement the open tasks in phase order.

### Code review instructions
- Read the guide alongside the umbrella corpus report; distinguish existing files from proposed modules.

### Technical details
- Parent: COSMOS-VIDEO-001.
- Simulator selection: VirtualHome, explicitly requested by the user.
''')
        index=path/'index.md';front=index.read_text().split('---',2)[1]
        index.write_text('---'+front+'---\n\n'+f'# {title}\n\n{scope}\n\nParent: COSMOS-VIDEO-001. Dependencies: '+(', '.join(deps) or 'existing VirtualHome corpus')+'.\n\n- [Intern guide](design-doc/01-intern-analysis-design-and-implementation-guide.md)\n- [Tasks](tasks.md)\n- [Diary](reference/01-design-and-delivery-diary.md)\n\nDesign preparation is in progress; implementation has not started.\n')
        (path/'tasks.md').write_text('# Tasks\n\n- [x] Establish scope and dependencies.\n- [ ] Complete intern design guide and detailed implementation tasks.\n- [ ] Review technical contracts and rendered PDF.\n- [ ] Upload this guide to reMarkable.\n')
    path=next(Path('ttmp/2026/09/06').glob(ticket+'--*'))
    records.append({'ticket':ticket,'title':title,'dependencies':deps,'scope':scope,'path':str(path),'guide':str(next((path/'design-doc').glob('*.md')))})
(ROOT/'various/project-tickets.json').write_text(json.dumps(records,indent=2)+'\n')
print('\n'.join(r['ticket']+' '+r['path'] for r in records))
