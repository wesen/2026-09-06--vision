#!/usr/bin/env python3
"""Render report figures directly from measured JSON, without model execution."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
root=Path(__file__).resolve().parents[1]
out=root/'various/vault-report/_assets';out.mkdir(parents=True,exist_ok=True)
report=json.loads((root/'various/audit-comparison.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':160})
fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
names=['video','reverse','video1','video3','mixed'];x=np.arange(len(names));width=.34
for offset,kind,label,color in [(-width/2,'tokens','Token/timestamp-only change','#ac3d36'),(width/2,'pixels','Pixel-only change','#247c91')]:
 values=[1-next(r for r in report['preprocessing'] if r['case']==n)['embedding_effect'][kind]['cosine'] for n in names]
 ax.bar(x+offset,values,width,label=label,color=color)
ax.set_yscale('log');ax.set_xticks(x,names);ax.set_ylabel('1 − cosine to official-processor FP32 output');ax.set_title('Processor differences: token changes dominate pixel resizing')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=2);ax.grid(axis='y',alpha=.2);fig.savefig(out/'mlx-video-fix-preprocessing.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
names=['text','image','video','black','reverse','video1','video3','mixed'];x=np.arange(len(names));width=.21
for i,(mode,label,color) in enumerate([('mlx','MLX FP32','#247c91'),('bf16','MLX BF16','#69a785'),('quant','Controlled all-layer 4-bit','#da9e36'),('community','Community 4-bit','#ac3d36')]):
 vals=[next(r for r in report['comparisons'] if r['case']==n and r['mode']==mode)['layers']['embedding']['cosine'] for n in names]
 ax.bar(x+(i-1.5)*width,vals,width,label=label,color=color)
ax.set_xticks(x,names);ax.set_ylim(0,1.06);ax.set_ylabel('Cosine to Torch FP32, identical official inputs');ax.set_title('Precision and artifact changes require separate acceptance');ax.legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,-.12));ax.grid(axis='y',alpha=.2)
fig.savefig(out/'mlx-video-fix-precision.png');plt.close(fig)
print(out)
