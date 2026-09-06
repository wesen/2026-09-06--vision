"""Independent multiclass ridge baseline on frozen sequence features."""
import numpy as np


def fit(sequences, classes, ridge=.01):
    if not sequences or ridge<=0:raise ValueError('training sequences and positive ridge required')
    spaces={s.feature_space_id for s in sequences}
    if len(spaces)!=1:raise ValueError('mixed feature spaces')
    for s in sequences:s.validate(classes)
    x=np.concatenate([s.features[s.loss_mask] for s in sequences]);y=np.concatenate([s.targets[s.loss_mask] for s in sequences])
    if set(y.tolist())!=set(range(classes)):raise ValueError('every class requires supervised training evidence')
    mean=x.mean(0);bias=np.eye(classes)[y].mean(0);center=x-mean;target=np.eye(classes)[y]-bias
    weights=np.linalg.solve(center.T@center+ridge*np.eye(x.shape[1]),center.T@target) if x.shape[1]<=len(x) else center.T@np.linalg.solve(center@center.T+ridge*np.eye(len(x)),target)
    return {'space':next(iter(spaces)),'classes':classes,'ridge':ridge,'mean':mean.tolist(),'bias':bias.tolist(),'weights':weights.tolist(),'training_episodes':[s.episode_id for s in sequences],'training_rows':len(x)}


def predict(model, sequence):
    sequence.validate(model['classes'])
    if sequence.feature_space_id!=model['space']:raise ValueError('linear feature-space mismatch')
    scores=(sequence.features-model['mean'])@np.asarray(model['weights'])+model['bias']
    scores[~sequence.valid]=np.nan
    labels=np.full(len(scores),-1,dtype=np.int64);labels[sequence.valid]=scores[sequence.valid].argmax(1)
    return scores,labels
