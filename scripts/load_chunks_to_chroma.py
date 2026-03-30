"""
Load chunk records from JSONL, embed with OpenAI, persist to Chroma.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)

DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "chunks.jsonl"
DEFAULT_PERSIST = Path(__file__).resolve().parent.parent / "chroma_db"
DEFAULT_COLLECTION = "test_cases_chunks"
DEFAULT_MODEL = "text-embedding-3-small"


def load_documents_from_jsonl(path: Path) -> list[Document]:
    documents: list[Document] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            page_content = row.get("page_content") or ""
            meta = dict(row.get("metadata") or {})
            if "chunk_index" in row:
                meta["chunk_index"] = row["chunk_index"]
            documents.append(Document(page_content=page_content, metadata=meta))
    if not documents:
        raise ValueError(f"No documents loaded from {path}")
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load chunks.jsonl into a persisted Chroma vector store.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"JSONL file (default: {DEFAULT_INPUT})",
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
        "--model-name",
        default=DEFAULT_MODEL,
        help=f"OpenAI embeddings model id (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove persist directory before loading (full re-ingest)",
    )
    parser.add_argument(
        "--smoke-query",
        default=None,
        metavar="TEXT",
        help="If set, run one similarity_search with this query after ingest",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    persist_dir = args.persist_directory.resolve()

    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    if args.reset and persist_dir.exists():
        shutil.rmtree(persist_dir)
        print(f"Removed existing persist directory: {persist_dir.as_posix()}")

    documents = load_documents_from_jsonl(input_path)
    print(f"Loaded {len(documents)} documents from {input_path.as_posix()}")

    if not os.getenv("OPENAI_API_KEY"):
        print(
            "OPENAI_API_KEY is not set. Add it to your environment or .env file.",
            file=sys.stderr,
        )
        return 1

    embeddings = OpenAIEmbeddings(model=args.model_name)
    print(f"Using embeddings model: {args.model_name}")

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir.as_posix(),
        collection_name=args.collection,
    )

    print(f"Chroma collection: {args.collection}")
    print(f"Persist directory: {persist_dir.as_posix()}")

    if args.smoke_query:
        results = vectorstore.similarity_search(args.smoke_query, k=3)
        print("Smoke query results (k=3):")
        for i, doc in enumerate(results):
            print(f"--- [{i}] metadata={doc.metadata}")
            preview = doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else "")
            print(preview)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
