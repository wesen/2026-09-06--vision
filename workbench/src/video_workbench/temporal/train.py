"""Small CPU frozen-feature TCN experiment with development-only selection.

CLI: python -m video_workbench.temporal.train DATASET FEATURES DESTINATION
"""
from pathlib import Path
import argparse
import copy
import json
import time
import resource
import numpy as np
import torch
from video_workbench.registry import file_hash
from video_workbench.perception.store import write_json
from .benchmark import load_sequences
from .tcn import CausalMultiStageTCN,segmentation_loss,ChunkPredictor


def run(dataset,features,destination):
    dest=Path(destination)
    if dest.exists():raise ValueError('fresh TCN destination required')
    classes,sequences,dm,fm=load_sequences(dataset,features)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    train=[s for part,s in sequences if part=='train'];d=train[0].features.shape[1];k=len(classes)
    values=np.concatenate([s.features[s.valid] for s in train]);mean=values.mean(0);scale=np.maximum(values.std(0),.01)
    counts=np.bincount(np.concatenate([s.targets[s.loss_mask] for s in train]),minlength=k)
    if (counts==0).any():raise ValueError('every class requires train supervision')
    class_weights=1/counts;class_weights/=class_weights.mean();weight=torch.tensor(class_weights,dtype=torch.float32)
    length=max(len(s.features) for s in train)
    x=torch.zeros(len(train),d,length);valid=torch.zeros(len(train),length,dtype=torch.bool);mask=valid.clone();targets=torch.full((len(train),length),-1,dtype=torch.long)
    for i,s in enumerate(train):
        n=len(s.features);x[i,:,:n]=torch.tensor(s.features.T);valid[i,:n]=torch.tensor(s.valid);mask[i,:n]=torch.tensor(s.loss_mask);targets[i,:n]=torch.tensor(s.targets)
    def evaluate(model,split):
        model.eval();pairs=[];episodes={}
        with torch.no_grad():
            for part,s in sequences:
                if part!=split:continue
                logits=model(torch.tensor(s.features.T)[None],torch.tensor(s.valid)[None])[-1,0]
                pred=logits.argmax(0).numpy();pred[~s.valid]=-1
                pairs.extend(zip(s.targets[s.loss_mask].tolist(),pred[s.loss_mask].tolist()))
                episodes[s.episode_id]={'predictions':pred.tolist(),'targets':s.targets.tolist(),'label_mask':s.label_mask.tolist(),'valid':s.valid.tolist(),'end_us':s.end_us.tolist()}
        per={name:{'n':sum(y==i for y,p in pairs),'correct':sum(y==i and p==i for y,p in pairs)} for i,name in enumerate(classes)}
        return {'weak_interior_accuracy':sum(y==p for y,p in pairs)/len(pairs),'macro_recall':float(np.mean([r['correct']/r['n'] for r in per.values() if r['n']])),'n':len(pairs),'per_class':per,'episodes':episodes}
    dest.mkdir(parents=True);candidates=[]
    for layers in (1,2):
        for seed in (7,17,27):
            torch.manual_seed(seed);config={'input_dim':d,'classes':k,'channels':16,'layers':layers,'stages':2}
            model=CausalMultiStageTCN(**config)
            model.feature_mean.copy_(torch.tensor(mean)[None,:,None]);model.feature_scale.copy_(torch.tensor(scale)[None,:,None])
            optimizer=torch.optim.Adam(model.parameters(),lr=.003)
            best=-1;state=None;trace=[];start=time.perf_counter()
            for epoch in range(1,81):
                model.train();optimizer.zero_grad();loss=segmentation_loss(model(x,valid),targets,mask,class_weight=weight);loss.backward();optimizer.step()
                if epoch%10==0:
                    dev=evaluate(model,'development');score=dev['macro_recall'];trace.append({'epoch':epoch,'training_loss':float(loss.detach()),'development_macro_recall':score})
                    if score>best:best=score;state=copy.deepcopy(model.state_dict());best_epoch=epoch
            checkpoint=dest/f'layers-{layers}-seed-{seed}.pt'
            torch.save({'config':config,'state_dict':state,'seed':seed,'epoch':best_epoch,'feature_space_id':fm['space_id']},checkpoint)
            record={'config':config,'seed':seed,'selected_epoch':best_epoch,'development_macro_recall':best,'trace':trace,'training_wall_seconds':time.perf_counter()-start,'checkpoint':checkpoint.name,'checkpoint_sha256':file_hash(checkpoint)}
            candidates.append(record);print('trained',layers,seed,best_epoch,best,flush=True)
    selected_layers=max((1,2),key=lambda layers:float(np.mean([r['development_macro_recall'] for r in candidates if r['config']['layers']==layers])))
    results=[]
    for r in candidates:
        if r['config']['layers']!=selected_layers:continue
        ck=torch.load(dest/r['checkpoint'],map_location='cpu',weights_only=True);model=CausalMultiStageTCN(**ck['config']);model.load_state_dict(ck['state_dict']);model.eval()
        start=time.perf_counter();metrics={split:evaluate(model,split) for split in ('train','development','test')};seconds=time.perf_counter()-start
        # Actual trained weights: prefix and single-cell streaming equivalence.
        errors=[];future_errors=[]
        with torch.no_grad():
            for part,s in sequences:
                if part!='test':continue
                xx=torch.tensor(s.features.T)[None];vv=torch.tensor(s.valid)[None];full=model(xx,vv)
                stream=ChunkPredictor(model);chunked=torch.cat([stream.push(xx[:,:,i:i+1],vv[:,i:i+1]) for i in range(len(s.features))],dim=-1)
                errors.append(float((full-chunked).abs().max()))
                cutoff=max(1,len(s.features)//2);other=xx.clone();other[:,:,cutoff:]+=100
                future_errors.append(float((full[...,:cutoff]-model(other,vv)[...,:cutoff]).abs().max()))
        if max(errors)>1e-4 or max(future_errors)>1e-6:raise ValueError('trained TCN causality/chunk check failed')
        result=dict(r,metrics=metrics,evaluation_wall_seconds=seconds,receptive_field_samples=model.receptive_field,
                    parameters=sum(p.numel() for p in model.parameters()),chunk_max_abs_error=max(errors),future_max_abs_error=max(future_errors))
        results.append(result);print('selected test',r['seed'],metrics['test']['weak_interior_accuracy'],metrics['test']['macro_recall'],flush=True)
    report={'status':'complete','kind':'weak-label frozen pooled-feature causal TCN; no native-video claim',
            'feature_space_id':fm['space_id'],'features_manifest_sha256':file_hash(Path(features)/'manifest.json'),
            'inputs_sha256':dm['inputs_sha256'],'labels_sha256':dm['labels_sha256'],
            'code_sha256':{name:file_hash(Path(__file__).parent/name) for name in ('train.py','tcn.py','benchmark.py')},
            'runtime':{'torch':torch.__version__,'device':'cpu','threads':2,'deterministic_algorithms':True,'max_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
            'training':{'episodes':[s.episode_id for s in train],'epochs':80,'optimizer':'Adam','lr':.003,'normalization':'train-valid feature mean/std floor .01 stored in model buffers','class_weights':class_weights.tolist(),'smooth_weight':0,'dropout':.1},
            'selection':'checkpoint by development macro recall every 10 epochs; architecture by mean development macro recall across three seeds; first wins ties',
            'selected_layers':selected_layers,'candidates':candidates,'selected_seed_results':results,
            'test_macro_recall_mean':float(np.mean([r['metrics']['test']['macro_recall'] for r in results])),
            'test_macro_recall_std':float(np.std([r['metrics']['test']['macro_recall'] for r in results])),
            'clock_policy':'trailing source features; ordered stream waits for available inputs; compute latency must be recorded by replay caller'}
    write_json(dest/'results.json',report);return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dataset');parser.add_argument('features');parser.add_argument('destination');args=parser.parse_args()
    run(args.dataset,args.features,args.destination)
