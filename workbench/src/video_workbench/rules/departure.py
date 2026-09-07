"""Causal camera-exit candidates from an ordered person-detection prefix.

Disappearance is a proposal, never proof of a room crossing. Keep detection gaps
visible to evaluation; do not filter candidates using reviewed event labels.
"""
from dataclasses import dataclass
from video_workbench.embedding import digest


@dataclass(frozen=True)
class DeparturePolicy:
    person_threshold: float = 0.25
    arm_frames: int = 3
    absent_frames: int = 3

    def __post_init__(self):
        if not 0 <= self.person_threshold <= 1:
            raise ValueError('person threshold outside [0, 1]')
        if self.arm_frames < 1 or self.absent_frames < 1:
            raise ValueError('positive consecutive frame counts required')


class DepartureDetector:
    """One instance per episode; O(1) prefix memory, strictly increasing PTS."""
    def __init__(self, episode_id, policy=DeparturePolicy()):
        self.episode_id, self.policy = episode_id, policy
        self.last_pts = -1
        self.present_count = self.absent_count = 0
        self.armed = False
        self.first_absent = None

    def observe(self, frame_id, pts_us, person_score):
        if pts_us <= self.last_pts or not 0 <= person_score <= 1:
            raise ValueError('unordered frame or invalid person score')
        self.last_pts = pts_us
        if person_score >= self.policy.person_threshold:
            self.present_count += 1
            self.absent_count = 0
            self.first_absent = None
            if self.present_count >= self.policy.arm_frames:
                self.armed = True
            return None
        self.present_count = 0
        if not self.armed:
            return None
        if self.absent_count == 0:
            self.first_absent = (frame_id, pts_us)
        self.absent_count += 1
        if self.absent_count < self.policy.absent_frames:
            return None
        first_id, first_us = self.first_absent
        self.armed = False
        self.absent_count = 0
        event = dict(episode_id=self.episode_id, kind='camera_exit_candidate',
                     frame_id=first_id, event_us=first_us, available_us=pts_us,
                     confirmation_frame_id=frame_id)
        return dict(event, event_id=digest(event)[:24])
