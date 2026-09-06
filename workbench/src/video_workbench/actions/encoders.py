"""Official FP32 image pooling shares artifacts, not feature identity, with native."""
from dataclasses import replace
from pathlib import Path
import numpy as np
from PIL import Image
from video_workbench.embedding import normalize
from video_workbench.registry import file_hash


class OfficialImagePool:
    def __init__(self):
        from video_workbench.native_video import NativeVideoEmbedder
        self.native = NativeVideoEmbedder()
        self.space = replace(self.native.space, mode='official_fp32_pooled_images',
            adapter='official-image-pool-v1', pooling='unit-mean-of-unit-image-vectors',
            temporal='order-invariant-images-no-video-timestamps',
            adapter_source=file_hash(Path(__file__)))

    def image(self, image):
        image = image.convert('RGB').resize(self.space.image_size, Image.Resampling.BICUBIC)
        return self.native._encode([{'type':'image'}], images=[image])

    def text(self, text):
        return self.native.text(text)

    def video(self, frames, pts_us=None, start_us=0):
        if not frames:raise ValueError('no images to pool')
        return normalize(np.mean([self.image(im) for im in frames], axis=0)[None])[0]


def intervention(frames, pts_us, mode):
    """Keep monotonic slots; return the original-source index in each slot."""
    if not frames or len(frames)!=len(pts_us) or any(b<=a for a,b in zip(pts_us,pts_us[1:])):
        raise ValueError('invalid source frame/timestamp sequence')
    if mode=='original':indices=list(range(len(frames)))
    elif mode=='reverse':indices=list(reversed(range(len(frames))))
    elif mode=='repeat_first':indices=[0]*len(frames)
    else:raise ValueError('unknown intervention')
    return [frames[i] for i in indices],list(pts_us),indices
