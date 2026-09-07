"""Trusted host broker. Complete video paths never enter worker payloads."""
from pathlib import Path
import json
from video_workbench.media import decode_selected
from video_workbench.registry import file_hash
from video_workbench.rules.evaluate import digest
from .clock import ReplayClock


class EvidenceBroker:
    def __init__(self, source, directory):
        self.source = dict(source)
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        if file_hash(source['video']) != source['video_sha256']:
            raise ValueError('registered source hash mismatch')

    def released(self, *, pts_us, available_us, dependency_end_us, cycle, horizon_us):
        offset = cycle * self.source['duration_us']
        ReplayClock.source_time(pts_us, cycle, self.source['duration_us'])
        if not pts_us <= dependency_end_us <= available_us or offset + available_us > horizon_us:
            raise ValueError('evidence dependency beyond replay horizon')
        return offset

    def trace_packet(self, frame, value, *, cycle, horizon_us, available_us=None, dependency_end_us=None):
        if frame['episode_id'] != self.source['episode_id'] or frame['video_sha256'] != self.source['video_sha256']:
            raise ValueError('trace source binding mismatch')
        expected = {'episode_id','video_sha256','frame_index','raw_pts','time_base','pts_us','width','height'}
        if set(frame) != expected:
            raise ValueError('invalid trace frame fields')
        pts = frame['pts_us']
        self.released(pts_us=pts, available_us=pts if available_us is None else available_us,
                      dependency_end_us=pts if dependency_end_us is None else dependency_end_us,
                      cycle=cycle, horizon_us=horizon_us)
        def reject_paths(value):
            if isinstance(value, dict):
                if any(k in {'path','video','command','model'} for k in value):
                    raise ValueError('path or command forbidden in released trace')
                for child in value.values(): reject_paths(child)
            elif isinstance(value, list):
                for child in value: reject_paths(child)
        reject_paths(value)
        text = json.dumps(value, allow_nan=False)
        if len(text.encode()) > 256_000:
            raise ValueError('trace payload too large')
        return dict(frame=frame, value=value)

    def image(self, frame, *, entity_id, cycle, horizon_us):
        index = frame['frame_index']
        if type(index) is not int or not 0 <= index < len(self.source['pts_us']):
            raise ValueError('unregistered frame index')
        if self.source['pts_us'][index] != frame['pts_us']:
            raise ValueError('registered frame timestamp mismatch')
        self.trace_packet(frame, {}, cycle=cycle, horizon_us=horizon_us)
        evidence_id = digest([self.source['video_sha256'], index])[:24]
        path = self.directory / (evidence_id + '.png')
        if file_hash(self.source['video']) != self.source['video_sha256']:
            raise ValueError('registered source changed')
        if not path.exists():
            image = decode_selected(self.source['video'], [index])[index]
            if image.width * image.height > 2_073_600:
                raise ValueError('image pixel budget exceeded')
            image.save(path)
        return dict(id=evidence_id, episode_id=self.source['episode_id'], entity_id=entity_id,
                    pts_us=frame['pts_us'], available_us=frame['pts_us'], path=str(path), sha256=file_hash(path))
