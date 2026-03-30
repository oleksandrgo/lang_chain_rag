"""
Load TestIT JSON exports from test_cases/, build LangChain Documents, split into chunks.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

import tiktoken
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "test_cases"


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def steps_to_text(steps: list[dict] | None) -> str:
    if not steps:
        return ""
    parts: list[str] = []
    for s in sorted(steps, key=lambda x: x.get("order", 0)):
        name = html_to_text(s.get("name"))
        exp = html_to_text(s.get("expectedResult"))
        block = []
        if name:
            block.append(f"Step: {name}")
        if exp:
            block.append(f"Expected: {exp}")
        if block:
            parts.append("\n".join(block))
    return "\n\n".join(parts)


def testcase_to_page_content(obj: dict) -> str:
    name = (obj.get("name") or "").strip()
    summary = html_to_text(obj.get("summary"))
    pre = html_to_text(obj.get("preconditions"))
    steps_text = steps_to_text(obj.get("steps"))
    sections = []
    if name:
        sections.append(f"Name: {name}")
    if summary:
        sections.append(f"Summary:\n{summary}")
    if pre:
        sections.append(f"Preconditions:\n{pre}")
    if steps_text:
        sections.append(f"Steps:\n{steps_text}")
    return "\n\n".join(sections)


def iter_json_files(root: Path) -> Iterator[Path]:
    if not root.is_dir():
        raise FileNotFoundError(f"Not a directory: {root}")
    yield from sorted(root.rglob("*.json"))


def load_documents(
    root: Path,
) -> tuple[list[Document], list[str]]:
    """Returns documents and warning lines for duplicate ids (keeps first occurrence)."""
    seen_ids: dict[int, str] = {}
    warnings: list[str] = []
    documents: list[Document] = []

    for path in iter_json_files(root):
        rel = path.relative_to(root)
        suite = rel.parts[0] if len(rel.parts) > 1 else ""

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            warnings.append(f"Skip {path}: root JSON is not a list")
            continue

        for obj in data:
            if not isinstance(obj, dict):
                continue
            tc_id = obj.get("id")
            if tc_id is None:
                warnings.append(f"Skip entry in {path}: missing id")
                continue
            try:
                id_int = int(tc_id)
            except (TypeError, ValueError):
                warnings.append(f"Skip entry in {path}: invalid id {tc_id!r}")
                continue

            if id_int in seen_ids:
                warnings.append(
                    f"Duplicate test case id {id_int}: keeping {seen_ids[id_int]}, skipping {path.as_posix()}"
                )
                continue

            content = testcase_to_page_content(obj)
            if not content.strip():
                warnings.append(f"Skip id {id_int} in {path}: empty content after build")
                continue

            seen_ids[id_int] = path.as_posix()
            external = obj.get("externalId")
            meta = {
                "source": path.as_posix(),
                "test_case_id": id_int,
                "external_id": external if external is not None else "",
                "suite": suite,
            }
            documents.append(Document(page_content=content, metadata=meta))

    return documents, warnings


def make_splitter(
    chunk_size: int,
    chunk_overlap: int,
    use_tokens: bool,
    encoding_model: str,
) -> tuple[RecursiveCharacterTextSplitter, bool]:
    """
    Returns (splitter, used_token_length).
    If token counting fails (e.g. tiktoken cannot download/cache encodings), falls back to character length.
    """
    separators = ["\n\n", "\n", " ", ""]
    if use_tokens:
        try:
            enc = tiktoken.encoding_for_model(encoding_model)
        except Exception:
            try:
                enc = tiktoken.get_encoding("cl100k_base")
            except Exception as exc:
                print(
                    f"tiktoken unavailable ({exc}); using character length instead.",
                    file=sys.stderr,
                )
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=separators,
                )
                return splitter, False

        def length_function(text: str) -> int:
            return len(enc.encode(text))

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=length_function,
        )
        return splitter, True

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    return splitter, False


def chunks_to_jsonl_lines(chunks: list[Document]) -> list[str]:
    lines: list[str] = []
    for i, doc in enumerate(chunks):
        payload = {
            "chunk_index": i,
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        }
        lines.append(json.dumps(payload, ensure_ascii=False))
    return lines


def main() -> int:   
    parser = argparse.ArgumentParser(description="Chunk TestIT JSON test cases with LangChain.")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"Root folder with JSON exports (default: {DEFAULT_ROOT})",
    )
    parser.add_argument("--chunk-size", type=int, default=5000)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument(
        "--use-tokens",
        action="store_true",
        help="Measure chunk size in tokens (tiktoken) instead of characters",
    )
    parser.add_argument(
        "--encoding-model",
        default="gpt-4",
        help="tiktoken model name for encoding (with --use-tokens)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write all chunks as JSON Lines to this file",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    documents, warnings = load_documents(root)

    for w in warnings:
        print(w, file=sys.stderr)

    splitter, token_mode_ok = make_splitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        use_tokens=args.use_tokens,
        encoding_model=args.encoding_model,
    )
    chunks = splitter.split_documents(documents)

    print(f"JSON root: {root.as_posix()}")
    if args.use_tokens:
        print(f"Chunk length unit: {'tokens (tiktoken)' if token_mode_ok else 'characters (fallback)'}")
    print(f"Documents (test cases): {len(documents)}")
    print(f"Chunks after split: {len(chunks)}")
    if chunks:
        first = chunks[0] 
        preview = first.page_content[:500] + ("..." if len(first.page_content) > 500 else "")
        print("First chunk preview:", preview)
        print("First chunk metadata:", first.metadata)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        lines = chunks_to_jsonl_lines(chunks)
        args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote {len(lines)} lines to {args.output.as_posix()}")       

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
