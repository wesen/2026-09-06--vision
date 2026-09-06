"""Decode presentation timestamps; never infer VFR times from frame numbers."""

from fractions import Fraction
import av


def micros(value):
    return round(value * 1_000_000)


def probe(path):
    with av.open(str(path)) as container:
        if not container.streams.video:
            raise ValueError("no video stream")
        stream = container.streams.video[0]
        pts, raw = [], []
        last_duration = None
        for frame in container.decode(stream):
            if frame.pts is None or frame.time_base is None:
                raise ValueError("missing presentation timestamp")
            raw.append(frame.pts)
            pts.append(micros(frame.pts * frame.time_base))
            last_duration = (
                micros(frame.duration * frame.time_base) if frame.duration else None
            )
        if not pts or any(b <= a for a, b in zip(pts, pts[1:])):
            raise ValueError("empty or non-increasing presentation timestamps")
        origin = pts[0]
        pts = [p - origin for p in pts]
        # Last-frame duration cannot be inferred from a next PTS. Prefer encoded duration.
        tail = last_duration or (
            pts[-1] - pts[-2]
            if len(pts) > 1
            else micros(1 / Fraction(stream.average_rate))
            if stream.average_rate
            else 1
        )
        return {
            "pts_us": pts,
            "raw_pts": raw,
            "origin_us": origin,
            "time_base": str(stream.time_base),
            "duration_us": pts[-1] + tail,
            "tail_duration_source": "frame" if last_duration else "estimated",
            "width": stream.width,
            "height": stream.height,
            "frames": len(pts),
            "variable_rate": len(set(b - a for a, b in zip(pts, pts[1:]))) > 1,
        }


def selected_indices(pts, start_us, end_us, fps):
    """First frame at/after each requested grid point, within a half-open clip."""
    from bisect import bisect_left

    if fps <= 0 or start_us < 0 or end_us <= start_us:
        raise ValueError("invalid sampling interval")
    step = Fraction(1_000_000, 1) / Fraction(str(fps))
    indices = []
    t = Fraction(start_us)
    while t < end_us:
        i = bisect_left(pts, t)
        if i < len(pts) and pts[i] < end_us and (not indices or indices[-1] != i):
            indices.append(i)
        t += step
    return indices


def decode_selected(path, indices):
    wanted = set(indices)
    images = {}
    if not wanted:
        return images
    with av.open(str(path)) as container:
        for i, frame in enumerate(container.decode(video=0)):
            if i in wanted:
                images[i] = frame.to_image()
            if i >= max(wanted):
                break
    if set(images) != wanted:
        raise ValueError("video changed or selected frame missing")
    return images
