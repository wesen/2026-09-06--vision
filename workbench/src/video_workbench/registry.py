"""Transactional, model-safe manifest registry. Labels are never loaded here."""

from pathlib import Path
import hashlib
import json
import re
import sqlite3
from .media import probe


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class Registry:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise ValueError(f"unsupported registry schema {version}")
        with self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS episodes (
                episode_id TEXT PRIMARY KEY, split TEXT NOT NULL,
                split_group TEXT NOT NULL, video TEXT NOT NULL,
                video_sha256 TEXT NOT NULL, media TEXT NOT NULL)""")
            self.db.execute("PRAGMA user_version=1")

    def close(self):
        self.db.close()

    def episodes(self, split=None):
        sql = "SELECT * FROM episodes"
        args = ()
        if split is not None:
            sql += " WHERE split=?"
            args = (split,)
        rows = self.db.execute(sql + " ORDER BY episode_id", args).fetchall()
        return [dict(r, media=json.loads(r["media"])) for r in rows]

    def get(self, episode_id):
        r = self.db.execute(
            "SELECT * FROM episodes WHERE episode_id=?", (episode_id,)
        ).fetchone()
        if r is None:
            raise KeyError(episode_id)
        return dict(r, media=json.loads(r["media"]))

    def ingest(self, manifest):
        # Serialize validation with publication, so a second writer cannot validate
        # split ownership against an out-of-date registry snapshot.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            return self._ingest(manifest)

    def _ingest(self, manifest):
        manifest = Path(manifest).resolve()
        root = manifest.parent
        required = {"episode_id", "split", "split_group", "video", "video_sha256"}
        incoming = []
        ids = set()
        existing = {r["episode_id"]: r for r in self.episodes()}
        groups = {}
        hash_splits = {}
        for row in existing.values():
            groups[row["split_group"]] = row["split"]
            hash_splits[row["video_sha256"]] = row["split"]
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if set(r) != required:
                raise ValueError("manifest must contain exactly model-safe fields")
            if not all(isinstance(v, str) and v for v in r.values()):
                raise ValueError("manifest fields must be nonempty strings")
            eid = r["episode_id"]
            if not re.fullmatch(r"[A-Za-z0-9_-]+", eid):
                raise ValueError("unsafe episode ID")
            if eid in ids:
                raise ValueError(f"duplicate episode ID {eid}")
            ids.add(eid)
            if r["split"] not in {"train", "development", "test"}:
                raise ValueError("invalid split")
            if groups.setdefault(r["split_group"], r["split"]) != r["split"]:
                raise ValueError("group crosses splits")
            if hash_splits.setdefault(r["video_sha256"], r["split"]) != r["split"]:
                raise ValueError("identical video crosses splits")
            video = (root / r["video"]).resolve()
            if not video.is_relative_to(root):
                raise ValueError("video escapes manifest root")
            if file_hash(video) != r["video_sha256"]:
                raise ValueError(f"hash mismatch {eid}")
            r["video"] = str(video)
            r["media"] = probe(video)
            if eid in existing and existing[eid] != r:
                raise ValueError(f"immutable episode changed {eid}")
            incoming.append(r)
        if not incoming:
            raise ValueError("empty manifest")
        with self.db:
            for r in incoming:
                self.db.execute(
                    "INSERT OR IGNORE INTO episodes VALUES (?,?,?,?,?,?)",
                    (
                        r["episode_id"],
                        r["split"],
                        r["split_group"],
                        r["video"],
                        r["video_sha256"],
                        json.dumps(r["media"], sort_keys=True),
                    ),
                )
        return {
            "ingested": len(incoming),
            "registered": len(self.episodes()),
            "frames": sum(r["media"]["frames"] for r in incoming),
            "duration_seconds": sum(r["media"]["duration_us"] for r in incoming) / 1e6,
        }
