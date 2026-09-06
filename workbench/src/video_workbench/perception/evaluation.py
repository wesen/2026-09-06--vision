"""Evaluator-only count metrics over explicitly reviewed correspondences."""


def identity_counts(assignments):
    """Rows: visible (bool) and observed_track_id or None, one true entity/span."""
    visible=matched=switches=fragments=0;previous=None;gap=False
    for row in assignments:
        if not row['visible']:continue
        visible+=1;current=row['observed_track_id']
        if current is None:
            if previous is not None:gap=True
            continue
        matched+=1
        if previous is not None:
            switches+=int(previous!=current)
            fragments+=int(gap)
        previous=current;gap=False
    return {'visible_rows':visible,'matched_rows':matched,'id_switches':switches,'fragmentations':fragments,'visible_coverage':matched/visible if visible else None}
