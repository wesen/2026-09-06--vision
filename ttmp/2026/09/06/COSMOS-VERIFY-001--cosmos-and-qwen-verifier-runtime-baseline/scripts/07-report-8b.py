"""Join independently supervised 8B runs without altering the original evidence."""
from pathlib import Path
import json
import shutil
import subprocess
root=Path(__file__).resolve().parents[1]
out=Path('output/verifier-v1/image-gate-8b-comparison');out.mkdir(parents=True,exist_ok=True)
records=[];reports=[]
for folder in ['image-gate-8b','image-gate-cosmos-8b']:
 source=Path('output/verifier-v1')/folder
 request=json.loads((source/'request.json').read_text())
 if records: assert request==json.loads((out/'request.json').read_text()),'matched requests required'
 for p in source.iterdir():
  if p.suffix in ['.json','.log'] and p.name!='manifest.json':shutil.copyfile(p,out/p.name)
 for entry in json.loads((source/'manifest.json').read_text()):
  if entry['result']:
   reports.append(json.loads(Path(entry['result']).read_text()));entry['result']=str(out/Path(entry['result']).name)
  entry['log']=str(out/Path(entry['log']).name);records.append(entry)
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
subprocess.run(['workbench/.venv/bin/python',str(root/'scripts/04-archive-image-gate.py'),'--source',str(out),'--destination',str(root/'various/v1-image-gate-8b-comparison')],check=True)
conversion=json.loads((root/'various/cosmos-8b-conversion.json').read_text())
rows=[]
for d in reports:
 rows.append(f"| {Path(d['model_path']).name} | {d['load_seconds']:.3f} | {d['generation_seconds']:.3f} | {d['generation']['generation_tokens']} | {d['peak_mlx_memory_bytes']/1e9:.3f} | {d['parsed']['status']} |")
p=root/'reference/03-8b-verifier-runtime-follow-up.md';header=p.read_text().split('---',2)[1]
p.write_text('---'+header+'---\n\n# 8B verifier runtime follow-up\n\n'+f'''Both 8B candidates were run on the exact request and approved image used for the 2B runtime gate. This is a single development smoke example, not the frozen V4 comparison or an accuracy estimate.

## Models, format, and engine

- Qwen: `mlx-community/Qwen3-VL-8B-Instruct-8bit`, revision `a0093b9b5fda6f76ddd4a462c6830ae7c4fe47ec`.
- Cosmos source: official `nvidia/Cosmos-Reason2-8B`, revision `a9fae2cf89dc64db96b12860417f0eb403013bb9`; converted locally with MLX-VLM 0.6.17, 8-bit affine quantization, group size 64, and remote code disabled.
- Both execute through the existing generative MLX-VLM 0.6.17 worker, MLX 0.32.2, in `workbench/verify-env/.venv`. These are answer-generating models; they do not consume the TEMPORAL embedding vectors.

Cosmos access required web agreement and a valid local Hugging Face credential. Merely agreeing in the browser did not replace the previously invalid CLI token. The successful source download is pinned; converted output file hashes and conversion settings are stored in `various/cosmos-8b-conversion.json`.

## Conversion cost

Local conversion took **{conversion['conversion_seconds']:.2f} seconds**. Output hashing took **{conversion['hashing_seconds']:.2f} seconds**; together they took {conversion['seconds']:.2f} seconds. These timings exclude download time. They measure this checkpoint, machine, and conversion method; they are not a general quantization timing guarantee.

## Single-image measurements

| Candidate | Load s | Generate s | Output tokens | Peak MLX GB | Strict JSON |
|---|---:|---:|---:|---:|---|
'''+ '\n'.join(rows)+'''

The approved 640 × 480 full frame shows the microwave at 12.700 seconds. Both runs use the same question, request/evidence identifiers, 256 generated-token ceiling, and temperature zero. The archived formatted prompts capture candidate chat-template behavior. The 120-second whole-process ceiling is a runtime smoke guard, not the production request-deadline implementation. Peak memory measures MLX allocations rather than total system memory. Single-run timings are not latency distributions.

![Matched 8B input and raw responses](../various/v1-image-gate-8b-comparison/runtime-audit.png)

## Acceptance limits

Generation success, strict answer validity, and factual support are distinct outcomes. Preserve the exact response and parser status; never silently repair invalid JSON for the measured result. This example can establish usable local inference, but cannot establish that 8B is more accurate than 2B or that one model is better at household reasoning.

The Qwen community conversion and local Cosmos conversion have different provenance; identical declared bit width is not numerical parity. Floating-point modules may remain under the converter's multimodal quantization policy. We have not compared quantized outputs against official unquantized reference logits or validated native-video input for these verifier checkpoints.

## Reproduction and next work

Ticket scripts `05-download-8b.py`, `06-convert-cosmos-8b.py`, and `03-image-runtime-gate.py --pins FILE --output DIRECTORY` implement the pinned sequence. Use `07-report-8b.py` to assemble the saved runs and regenerate the visual report without model inference. Existing 2B and individual 8B results remain separate.

Next work is V2 bounded evidence execution and V3 output/timeout fixtures, followed by the frozen reviewed V4 comparison. The 8B embedding proposal is explicitly deferred in VIDEO-TEMPORAL-001; it is not part of this run.
''')
print('\n'.join(rows))
