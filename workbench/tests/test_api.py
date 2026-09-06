from fastapi.testclient import TestClient
from video_workbench.api import create_app
from video_workbench.index import build
from video_workbench.registry import Registry
from test_registry import video, row, manifest
from test_index import FakeEmbedder


class QueryEmbedder(FakeEmbedder):
    def text(self, text):
        return [1, 1, 0.2]


def test_api_and_registered_video_range(tmp_path, video):
    db = tmp_path / "r.sqlite"
    r = Registry(db)
    r.ingest(manifest(tmp_path, [row(video)]))
    e = QueryEmbedder()
    index = build(r, e, tmp_path / "cache", 0.2, 5, progress=lambda *a, **k: None)
    r.close()
    with TestClient(create_app(db, index["manifest"], e)) as client:
        assert client.get("/").status_code == 200
        result = client.post(
            "/v1/search", json={"query": "open fridge", "split": "train"}
        ).json()
        assert result["hits"][0]["feature_space_id"] == e.space.id
        assert "video" not in result["hits"][0]
        assert (
            client.post(
                "/v1/search", json={"query": "x", "index_id": "wrong"}
            ).status_code
            == 409
        )
        for request in (
            {"query": " "},
            {"query": "x", "top_k": 0},
            {"query": "x", "path": "/etc/passwd"},
            {"query": "x", "split": "other"},
        ):
            assert client.post("/v1/search", json=request).status_code == 422
        assert (
            client.post("/v1/search", json={"query": "x", "split": "test"}).json()[
                "hits"
            ]
            == []
        )
        assert client.get("/v1/episodes/not-registered/video").status_code == 404
        assert (
            client.get("/v1/episodes/..%2F..%2Fetc%2Fpasswd/video").status_code == 404
        )
        response = client.get(
            "/v1/episodes/ep-one/video", headers={"Range": "bytes=0-31"}
        )
        assert response.status_code == 206 and len(response.content) == 32
        assert response.headers["content-range"].startswith("bytes 0-31/")
        video.write_bytes(b"changed")
        assert client.get("/v1/episodes/ep-one/video").status_code == 409
