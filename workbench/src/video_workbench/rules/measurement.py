"""One-to-one event matching and end-to-end alert accounting."""
from functools import lru_cache


def match_events(reference, candidates, tolerance_us):
    """Maximize matches then minimize error, independently within each episode.

    Sorted scalar timestamps admit an optimal non-crossing assignment. Dynamic
    programming avoids greedy nearest-neighbor loss when tolerance bands overlap.
    Returned IDs refer to caller records; unmatched reference events stay visible.
    """
    if type(tolerance_us) is not int or tolerance_us < 0:
        raise ValueError('nonnegative integer matching tolerance required')
    for population in (reference, candidates):
        if len({r['event_id'] for r in population}) != len(population):
            raise ValueError('duplicate event identity')
        if any(type(r['event_us']) is not int or r['event_us'] < 0 for r in population):
            raise ValueError('invalid event timestamp')
    matched=[]
    for episode in sorted({r['episode_id'] for r in reference+candidates}):
        refs=sorted((r for r in reference if r['episode_id']==episode),key=lambda r:(r['event_us'],r['event_id']))
        preds=sorted((r for r in candidates if r['episode_id']==episode),key=lambda r:(r['event_us'],r['event_id']))
        @lru_cache(None)
        def solve(i,j):
            if i==len(refs) or j==len(preds):return (0,0,())
            options=[solve(i+1,j),solve(i,j+1)]
            error=abs(refs[i]['event_us']-preds[j]['event_us'])
            if error<=tolerance_us:
                count,cost,pairs=solve(i+1,j+1)
                options.append((count+1,cost+error,((refs[i]['event_id'],preds[j]['event_id']),)+pairs))
            return min(options,key=lambda x:(-x[0],x[1],x[2]))
        matched.extend(solve(0,0)[2])
    used_refs={r for r,_ in matched};used_preds={p for _,p in matched}
    return dict(pairs=matched,missed=[r['event_id'] for r in reference if r['event_id'] not in used_refs],
                unmatched_candidates=[p['event_id'] for p in candidates if p['event_id'] not in used_preds])


def measure(reference,candidates,decisions,duration_us,tolerance_us=500000):
    """Unknown and missing candidates are never counted as successful alerts."""
    if duration_us<=0:raise ValueError('positive observed source duration required')
    if set(decisions)!={p['event_id'] for p in candidates}:raise ValueError('one decision per candidate required')
    if any(d not in ('PASS','VIOLATION','UNKNOWN') for d in decisions.values()):raise ValueError('invalid decision')
    matches=match_events(reference,candidates,tolerance_us)
    truth={r['event_id']:r for r in reference};pred_to_ref={p:r for r,p in matches['pairs']}
    positives={r['event_id'] for r in reference if r['door_open'] is True}
    alerts={p for p,d in decisions.items() if d=='VIOLATION'}
    true_alerts={p for p in alerts if pred_to_ref.get(p) in positives}
    # An alert on an unknown reference is unscorable, not a proven false alarm.
    unscorable={p for p in alerts if p in pred_to_ref and truth[pred_to_ref[p]]['door_open'] is None}
    false_alerts=alerts-true_alerts-unscorable
    ratio=lambda a,b:a/b if b else None
    return dict(reference_events=len(reference),candidates=len(candidates),matching=matches,
                candidate_recall=ratio(len(matches['pairs']),len(reference)),candidate_precision=ratio(len(matches['pairs']),len(candidates)),
                positive_events=len(positives),true_alerts=len(true_alerts),missed_positive_events=len(positives)-len(true_alerts),
                violation_recall=ratio(len(true_alerts),len(positives)),false_alerts=len(false_alerts),
                false_alerts_per_source_hour=len(false_alerts)*3600000000/duration_us,unscorable_alerts=len(unscorable),
                unknowns=sum(d=='UNKNOWN' for d in decisions.values()),unknown_fraction=ratio(sum(d=='UNKNOWN' for d in decisions.values()),len(candidates)),
                source_duration_us=duration_us)
