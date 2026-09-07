"""Fixed trusted worker entry point. Recorded work is explicitly marked."""
from pathlib import Path
import json
import sys
import time


def main():
    source, destination = map(Path, sys.argv[1:3])
    job = json.loads(source.read_text())
    if job['mode'] == 'recorded':
        seconds = job['service_seconds']
        if type(seconds) not in (float,int) or not 0 <= seconds <= 120:
            raise ValueError('invalid recorded service duration')
        time.sleep(seconds)
        result = dict(mode='recorded', payload=job['result'])
    elif job['mode'] == 'live_verifier':
        # Invoke the accepted worker in this same process so the scheduler's
        # process-group deadline covers model loading, generation, and cleanup.
        from video_workbench.verifiers.adapter import check_packet
        from video_workbench.verifiers.profiles import validate_profile
        from video_workbench.verifiers.worker import run as infer
        check_packet(job['request'])
        validate_profile(job['profile'], job['request'])
        request = source.with_name('request.json')
        profile = source.with_name('profile.json')
        raw = source.with_name('worker-result.json')
        request.write_text(json.dumps(job['request']))
        profile.write_text(json.dumps(job['profile']))
        infer(job['model'], str(request), str(raw), 'visibility', str(profile))
        check_packet(job['request'])
        result = dict(mode='live_verifier', payload=json.loads(raw.read_text()))
    else:
        raise ValueError('unsupported replay worker mode')
    destination.write_text(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    main()
