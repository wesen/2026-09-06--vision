"""One feature-boundary smoke check; actual replay is exercised by its CLI."""
from dataclasses import replace
import sqlite3
import pytest
from video_workbench.temporal.store import Observation,Store


def test_observation_store_smoke(tmp_path):
    path=tmp_path/'observations.sqlite'
    o=Observation('a','run','F','episode','door','open',False,10,20,30,('frame',),'producer','space','causal')
    store=Store(path)
    assert store.append(o)
    assert not store.append(replace(o,committed_us=40))
    args=('run','F','episode','door','open')
    assert store.state_at(*args,event_us=10,as_of_us=29)['status']=='unknown'
    expected=store.state_at(*args,event_us=10,as_of_us=30)
    assert expected['value'] is False
    assert store.state_at(*args,event_us=11,as_of_us=100)['status']=='unknown'
    with pytest.raises(ValueError,match='changed content'):store.append(replace(o,value=True))
    with pytest.raises(ValueError,match='mixed producers'):store.append(replace(o,observation_id='b',producer='other'))
    with pytest.raises(sqlite3.IntegrityError,match='append-only'):store.connection.execute('DELETE FROM observations')
    assert store.append(replace(o,observation_id='unknown',event_us=11,value=None,unknown_reason='missing_crop'))
    assert store.state_at(*args,event_us=11,as_of_us=30)['reason']=='source_unknown'
    store.close();store=Store(path)
    assert store.state_at(*args,event_us=10,as_of_us=30)==expected
    store.close()
