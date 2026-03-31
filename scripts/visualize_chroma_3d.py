"""
Visualize persisted Chroma embeddings as 3D t-SNE scatter.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from chromadb import PersistentClient
from dotenv import load_dotenv
from sklearn.manifold import TSNE

load_dotenv(override=True)

DEFAULT_PERSIST = Path(__file__).resolve().parent.parent / "chroma_db"
DEFAULT_COLLECTION = "test_cases_chunks"
DEFAULT_OUT_HTML = Path(__file__).resolve().parent.parent / "tsne_3d.html"


def build_hover_text(document: str, metadata: dict, max_len: int = 180) -> str:
    preview = (document or "").replace("\n", " ").strip()
    if len(preview) > max_len:
        preview = preview[:max_len] + "..."
    return (
        f"<b>metadata</b>: {json.dumps(metadata, ensure_ascii=False)}"
        f"<br><b>text</b>: {preview}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize Chroma collection embeddings in 3D (t-SNE)."
    )
    parser.add_argument(
        "--persist-directory",
        type=Path,
        default=DEFAULT_PERSIST,
        help=f"Chroma persist directory (default: {DEFAULT_PERSIST})",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help=f"Chroma collection name (default: {DEFAULT_COLLECTION})",
    )
    parser.add_argument(
        "--max-points",
        type=int,
        default=None,
        help="Use at most this many points (random sample) for faster plotting.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling and t-SNE (default: 42).",
    )
    parser.add_argument(
        "--out-html",
        type=Path,
        default=DEFAULT_OUT_HTML,
        help=f"Path to output HTML (default: {DEFAULT_OUT_HTML})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    persist_dir = args.persist_directory.resolve()

    if not persist_dir.exists():
        print(f"Persist directory not found: {persist_dir}", file=sys.stderr)
        return 1

    client = PersistentClient(path=persist_dir.as_posix())
    collection = client.get_collection(name=args.collection)
    result = collection.get(include=["embeddings", "documents", "metadatas"])

    embeddings = result.get("embeddings")
    documents = result.get("documents")
    metadatas = result.get("metadatas")

    if embeddings is None:
        embeddings = []
    if documents is None:
        documents = []
    if metadatas is None:
        metadatas = []

    if len(embeddings) == 0:
        print(
            f"No embeddings found in collection '{args.collection}'.",
            file=sys.stderr,
        )
        return 1

    if not (len(embeddings) == len(documents) == len(metadatas)):
        print("Collection payload lengths are inconsistent.", file=sys.stderr)
        return 1

    vectors = np.array(embeddings, dtype=np.float32)
    total_points = len(vectors)

    rng = random.Random(args.seed)
    if args.max_points is not None and args.max_points > 0 and total_points > args.max_points:
        idx = list(range(total_points))
        rng.shuffle(idx)
        idx = idx[: args.max_points]
        vectors = vectors[idx]
        documents = [documents[i] for i in idx]
        metadatas = [metadatas[i] for i in idx]

    n_points = len(vectors)
    if n_points < 4:
        print("Need at least 4 vectors to run stable 3D t-SNE.", file=sys.stderr)
        return 1

    perplexity = max(2, min(30, n_points - 1))
    reduced = TSNE(
        n_components=3,
        random_state=args.seed,
        perplexity=perplexity,
        init="random",
        learning_rate="auto",
    ).fit_transform(vectors)

    hover_text = [
        build_hover_text(doc or "", meta or {})
        for doc, meta in zip(documents, metadatas)
    ]

    fig = go.Figure(
        data=go.Scatter3d(
            x=reduced[:, 0],
            y=reduced[:, 1],
            z=reduced[:, 2],
            mode="markers",
            marker={"size": 5, "opacity": 0.85},
            text=hover_text,
            hoverinfo="text",
        )
    )
    fig.update_layout(
        title=f"3D Chroma Vector Store Visualization ({args.collection})",
        scene={"xaxis_title": "x", "yaxis_title": "y", "zaxis_title": "z"},
        width=950,
        height=700,
    )

    print(f"Collection: {args.collection}")
    print(f"Persist directory: {persist_dir.as_posix()}")
    print(f"Points plotted: {n_points} (total available: {total_points})")
    print(f"t-SNE perplexity: {perplexity}")

    out = args.out_html.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out.as_posix(), include_plotlyjs="cdn")
    print(f"Saved HTML: {out.as_posix()}")

    fig.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
