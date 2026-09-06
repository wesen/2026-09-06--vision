"""Sequence contracts: missing features and missing labels are independent."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Sequence:
    episode_id: str
    feature_space_id: str
    features: np.ndarray
    start_us: np.ndarray
    end_us: np.ndarray
    available_us: np.ndarray
    valid: np.ndarray
    label_mask: np.ndarray
    targets: np.ndarray
    evidence_ids: list[tuple[str, ...]]

    def validate(self, classes):
        x=np.asarray(self.features)
        if x.ndim!=2 or not len(x) or not np.isfinite(x).all():
            raise ValueError('finite nonempty [T,D] features required')
        t=len(x)
        for name in ('start_us','end_us','available_us','valid','label_mask','targets'):
            a=getattr(self,name)
            if not isinstance(a,np.ndarray) or a.shape!=(t,):raise ValueError('sequence shape mismatch')
        for name in ('start_us','end_us','available_us','targets'):
            if not np.issubdtype(getattr(self,name).dtype,np.integer):raise ValueError('integer clocks and targets required')
        if self.valid.dtype!=np.bool_ or self.label_mask.dtype!=np.bool_:raise ValueError('boolean masks required')
        if (np.any(self.start_us<0) or np.any(self.end_us<=self.start_us)
                or np.any(np.diff(self.end_us)<=0) or np.any(self.available_us<self.end_us)):
            raise ValueError('invalid feature horizon or availability')
        if np.any(self.targets[self.label_mask]<0) or np.any(self.targets[self.label_mask]>=classes):raise ValueError('invalid supervised target')
        if not self.episode_id or not self.feature_space_id or len(self.evidence_ids)!=t:raise ValueError('sequence provenance required')
        if any(self.valid[i] and not ids for i,ids in enumerate(self.evidence_ids)):raise ValueError('valid feature requires evidence')
        if np.any(x[~self.valid]!=0):raise ValueError('missing features require zero storage and false validity')
        return self

    @property
    def loss_mask(self):
        return self.valid & self.label_mask

    def available_indices(self, as_of_us):
        """Return only features whose entire source horizon is available."""
        return np.flatnonzero(self.valid & (self.available_us<=as_of_us))

    def segment_time(self, start, end):
        """Map a half-open feature segment without claiming coverage through gaps."""
        if not 0<=start<end<=len(self.features):raise ValueError('invalid segment index')
        intervals=[]
        for i in range(start,end):
            if not self.valid[i]:continue
            a,b=int(self.start_us[i]),int(self.end_us[i])
            if intervals and a<=intervals[-1][1]:intervals[-1][1]=max(intervals[-1][1],b)
            else:intervals.append([a,b])
        return {'bounds_us':[int(self.start_us[start]),int(self.end_us[end-1])],
                'evidence_coverage_us':intervals,'contains_missing_features':bool((~self.valid[start:end]).any())}


def trailing_grid(pts_us, duration_us, window_us=2_000_000, stride_us=500_000):
    """Dense half-open trailing windows; source frames are never at/after end."""
    pts=np.asarray(pts_us)
    if (pts.ndim!=1 or not len(pts) or not np.issubdtype(pts.dtype,np.integer)
            or pts[0]<0 or np.any(np.diff(pts)<=0) or duration_us<=pts[-1]
            or min(window_us,stride_us)<=0):raise ValueError('invalid native timestamp grid')
    ends=list(range(stride_us,duration_us+1,stride_us))
    if not ends or ends[-1]!=duration_us:ends.append(duration_us)
    return [{'start_us':max(0,end-window_us),'end_us':end,'available_us':end,
             'source_indices':np.flatnonzero((pts>=max(0,end-window_us))&(pts<end)).tolist()}
            for end in ends]
