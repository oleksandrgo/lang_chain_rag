"""
CLI retrieval helper for test case impact analysis.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)

DEFAULT_PERSIST = Path(__file__).resolve().parent.parent / "chroma_db"
DEFAULT_COLLECTION = "test_cases_chunks"
DEFAULT_EMBED_MODEL = "text-embedding-3-small"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrieve relevant test-case chunks from Chroma."
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
        "--k",
        type=int,
        default=6,
        help="Top-k documents to retrieve (default: 6).",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBED_MODEL,
        help=f"Embeddings model id (default: {DEFAULT_EMBED_MODEL})",
    )
    return parser.parse_args()


def format_sources(documents: list, max_preview: int = 140) -> str:
    lines: list[str] = []
    for i, doc in enumerate(documents, start=1):
        meta = doc.metadata or {}
        preview = (doc.page_content or "").replace("\n", " ").strip()
        if len(preview) > max_preview:
            preview = preview[:max_preview] + "..."
        lines.append(f"{i}. metadata={meta} | preview={preview}")
    return "\n".join(lines)


def format_context_for_cursor(user_query: str, documents: list) -> str:
    context_blocks: list[str] = []
    for i, doc in enumerate(documents, start=1):
        context_blocks.append(
            f"[DOC {i}]\nmetadata={doc.metadata}\ntext={doc.page_content}"
        )
    context = "\n\n".join(context_blocks)
    return (
        "Use this retrieved context to answer the user in compact format with sections:\n"
        "## Summary\n"
        "## Potentially impacted test cases\n"
        "## What to test first\n"
        "## Sources\n\n"
        f"User request:\n{user_query}\n\n"
        f"Retrieved context:\n{context}"
    )


def main() -> int:
    args = parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set. Add it to .env or environment.", file=sys.stderr)
        return 1

    persist_dir = args.persist_directory.resolve()
    if not persist_dir.exists():
        print(f"Persist directory not found: {persist_dir}", file=sys.stderr)
        return 1

    embeddings = OpenAIEmbeddings(model=args.embedding_model)
    vectorstore = Chroma(
        persist_directory=persist_dir.as_posix(),
        collection_name=args.collection,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": args.k})

    print("Retriever is ready. Type your request (or 'exit').")
    while True:
        user_query = input("\nYou> ").strip()
        if not user_query:
            continue
        if user_query.lower() in {"exit", "quit", "q"}:
            print("Bye.")
            break

        docs = retriever.invoke(user_query)
        if not docs:
            print("\nNo relevant documents found in the collection.")
            continue

        context_for_cursor = format_context_for_cursor(user_query, docs)
        print("\n--- Context for Cursor LLM ---")
        print(context_for_cursor)
        print("\n--- Retrieved sources ---")
        print(format_sources(docs))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
