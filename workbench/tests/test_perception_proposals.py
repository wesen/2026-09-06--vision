from video_workbench.perception.proposals import select,uniform


def test_future_perturbation_and_periodic_fallback():
    frames=[dict(frame_id=str(i),episode_id='ep',video_sha256='sha',pts_us=i*100000,full_frame_change=0.) for i in range(51)]
    base=select(frames,{})
    changed=[dict(f,full_frame_change=1.) if f['pts_us']>2000000 else f for f in frames]
    later=select(changed,{})
    assert [p for p in base if p['available_at_us']<=2000000]==[p for p in later if p['available_at_us']<=2000000]
    assert [p['interval_us'][0] for p in base if p['selected']]==[0,3000000]
    assert len(uniform(frames))==5
    assert len({p['packet_id'] for p in base})==len(base)
