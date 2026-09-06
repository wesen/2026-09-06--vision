"""Local video workbench command line."""

import argparse
import json
from .registry import Registry


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default="output/video-workbench/registry.sqlite")
    commands = p.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("manifest")
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--split")
    index = commands.add_parser("index")
    index.add_argument("--model", default="output/models/qwen3-vl-embedding-2b-4bit")
    index.add_argument("--root", default="output/video-workbench")
    index.add_argument("--seconds", type=float, default=5)
    index.add_argument("--fps", type=float, default=1)
    index.add_argument("--splits", nargs="+", default=["train", "development", "test"])
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--manifest", required=True)
    search.add_argument("--model", default="output/models/qwen3-vl-embedding-2b-4bit")
    search.add_argument("--split", choices=["train", "development", "test"])
    search.add_argument("--top-k", type=int, default=5)
    serve = commands.add_parser("serve")
    serve.add_argument("--manifest", required=True)
    serve.add_argument("--model", default="output/models/qwen3-vl-embedding-2b-4bit")
    serve.add_argument("--port", type=int, default=8767)
    evaluate = commands.add_parser("evaluate-retrieval")
    evaluate.add_argument("--model", default="output/models/qwen3-vl-embedding-2b-4bit")
    evaluate.add_argument("--root", default="output/video-workbench")
    evaluate.add_argument(
        "--protocol", default="configs/retrieval/home-v1-protocol.json"
    )
    evaluate.add_argument("--queries", default="configs/retrieval/home-v1-queries.json")
    evaluate.add_argument(
        "--corpus-manifest", default="output/virtualhome-corpus/home-v1/inputs.jsonl"
    )
    evaluate.add_argument(
        "--report-dir", default="output/video-workbench/evaluation-v1"
    )
    for command in (index, search, serve):
        command.add_argument(
            "--mode", choices=["pooled_images", "native_video"], default="pooled_images"
        )
        command.set_defaults(model=None)
    index.set_defaults(root=None)
    args = p.parse_args()

    def encoder():
        if args.mode == "native_video":
            from .native_video import NativeVideoEmbedder, DEFAULT_MODEL

            return NativeVideoEmbedder(args.model or DEFAULT_MODEL)
        from .embedding import QwenEmbedder

        return QwenEmbedder(args.model or "output/models/qwen3-vl-embedding-2b-4bit")

    registry = Registry(args.db)
    try:
        if args.command == "evaluate-retrieval":
            from .embedding import QwenEmbedder
            from .evaluation import run

            result = run(
                registry,
                QwenEmbedder(args.model),
                args.root,
                args.protocol,
                args.queries,
                args.corpus_manifest,
                args.report_dir,
            )
        elif args.command in ("search", "serve"):
            e = encoder()
            if args.command == "serve":
                import uvicorn
                from .api import create_app

                uvicorn.run(
                    create_app(args.db, args.manifest, e),
                    host="127.0.0.1",
                    port=args.port,
                )
                return
            from .index import Index

            result = Index(args.manifest, e.space.id).search(
                e.text(args.query), e.space.id, args.top_k, args.split
            )
        elif args.command == "index":
            from .index import build

            if args.mode == "native_video":
                from .native_index import build_native as build
            result = build(
                registry,
                encoder(),
                args.root
                or (
                    "output/video-workbench-native"
                    if args.mode == "native_video"
                    else "output/video-workbench"
                ),
                args.seconds,
                args.fps,
                args.splits,
            )
        elif args.command == "ingest":
            result = registry.ingest(args.manifest)
        elif args.command == "inspect":
            result = [
                {k: v for k, v in r.items() if k != "media"}
                | {
                    "media": {
                        k: v
                        for k, v in r["media"].items()
                        if k not in ("pts_us", "raw_pts")
                    }
                }
                for r in registry.episodes(args.split)
            ]
        print(json.dumps(result, indent=2))
    finally:
        registry.close()


if __name__ == "__main__":
    main()
