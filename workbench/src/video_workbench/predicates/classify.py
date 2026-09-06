"""Small deterministic baselines and development-only calibration."""
import numpy as np


def margins(images, hypotheses):
    images, hypotheses = np.asarray(images), np.asarray(hypotheses)
    if images.ndim != 2 or hypotheses.shape != (2, images.shape[1]):
        raise ValueError('margin dimension mismatch')
    if not np.isfinite(images).all() or not np.isfinite(hypotheses).all():
        raise ValueError('nonfinite feature')
    return images @ (hypotheses[1]-hypotheses[0])


def fit_head(features, values, feature_space_id, entity_classes, ridge=.01):
    """Dual ridge regression; all inputs must already be filtered to visible train."""
    x, y = np.asarray(features,dtype=float), np.asarray(values,dtype=float)*2-1
    if len(x) != len(y) or set(y.tolist()) != {-1.,1.}:
        raise ValueError('head requires both visible training classes')
    mean, bias = x.mean(axis=0), float(y.mean())
    centered = x-mean
    weights = centered.T @ np.linalg.solve(centered@centered.T+ridge*np.eye(len(x)), y-bias)
    return {'weights':weights.tolist(), 'mean':mean.tolist(), 'bias':bias, 'ridge':ridge,
            'feature_space_id':feature_space_id, 'entity_classes':sorted(entity_classes)}


def head_scores(head, features, feature_space_id, entity_classes):
    if head['feature_space_id'] != feature_space_id:
        raise ValueError('head feature-space mismatch')
    if not set(entity_classes) <= set(head['entity_classes']):
        raise ValueError('head entity-class mismatch')
    return (np.asarray(features)-head['mean'])@np.asarray(head['weights'])+head['bias']


def sigmoid(x):
    return 1/(1+np.exp(-np.clip(x,-40,40)))


def fit_calibration(scores, values):
    """Regularized Platt fit; standardization uses development scores only."""
    s, y = np.asarray(scores,dtype=float), np.asarray(values,dtype=float)
    if len(s) != len(y) or set(y.tolist()) != {0.,1.}:
        raise ValueError('calibration requires both visible development classes')
    mean, scale = float(s.mean()), max(float(s.std()),1e-8)
    x = np.column_stack(((s-mean)/scale, np.ones(len(s))))
    w = np.array([0., np.log((y.sum()+.5)/(len(y)-y.sum()+.5))])
    penalty = np.diag([.01, .001])
    for _ in range(100):
        p = sigmoid(x@w)
        g = x.T@(p-y)/len(y)+penalty@w
        h = (x.T*(p*(1-p)))@x/len(y)+penalty
        delta = np.linalg.solve(h,g)
        w -= delta
        if np.linalg.norm(delta)<1e-9:
            break
    return {'mean':mean,'scale':scale,'weights':w.tolist(),'method':'regularized-platt-development-only','n':len(y)}


def probabilities(calibration, scores):
    return sigmoid((np.asarray(scores)-calibration['mean'])/calibration['scale']*calibration['weights'][0]+calibration['weights'][1])


def confusion(y, pred):
    y, pred = np.asarray(y,dtype=bool), np.asarray(pred,dtype=bool)
    return {'tn':int((~y & ~pred).sum()),'fp':int((~y & pred).sum()),'fn':int((y & ~pred).sum()),'tp':int((y & pred).sum())}


def macro_f1(counts):
    c=counts
    terms=[]
    for hit, a, b in ((c['tp'],c['fp'],c['fn']),(c['tn'],c['fp'],c['fn'])):
        denominator=2*hit+a+b
        terms.append(2*hit/denominator if denominator else 0.)
    return sum(terms)/2


def select_policy(p, y):
    """Maximize development F1, then retain most answers at <=10% empirical risk."""
    p,y = np.asarray(p),np.asarray(y,dtype=bool)
    distinct = np.unique(p)
    thresholds = np.r_[0., (distinct[:-1]+distinct[1:])/2, 1.]
    threshold = float(max(thresholds, key=lambda t:(macro_f1(confusion(y,p>=t)),-abs(t-.5))))
    for radius in (0.,.05,.1,.2,.3,.4,.5,1.01):
        answered = np.abs(p-threshold)>=radius
        risk = float(((p[answered]>=threshold)!=y[answered]).mean()) if answered.any() else 0.
        if risk <= .1:
            return {'threshold':threshold,'radius':radius,'development_answered':int(answered.sum()),'development_errors':int(((p[answered]>=threshold)!=y[answered]).sum()),'target_empirical_risk':.1}
    raise AssertionError('reject-all fallback must be reachable')


def evaluate(p, labels, policy):
    p=np.asarray(p)
    known=np.array([l.value is not None for l in labels])
    y=np.array([l.value is True for l in labels])
    pred=p>=policy['threshold']
    answered=np.abs(p-policy['threshold'])>=policy['radius']
    valid=answered&known
    counts=confusion(y[known],pred[known])
    errors=int((pred[valid]!=y[valid]).sum())
    return {'n':len(p),'known':int(known.sum()),'unknown':int((~known).sum()),
            'visible_confusion_without_abstention':counts,
            'visible_macro_f1_without_abstention':macro_f1(counts) if known.any() else None,
            'model_answered':int(answered.sum()),'coverage':float(answered.mean()) if len(p) else None,
            'known_answered':int(valid.sum()),'known_answered_errors':errors,
            'known_selective_risk':errors/int(valid.sum()) if valid.any() else None,
            'unknown_false_certainty':int((answered&~known).sum()),
            'oracle_visibility_answered':int(valid.sum()),
            'oracle_visibility_note':'Diagnostic only: suppresses predictions using reviewed visibility, not an implemented visibility model.'}
