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
        order = s.get("order")
        if order is not None:
            block.append(f"Order: {order}")
        if name:
            block.append(f"Step: {name}")
        if exp:
            block.append(f"Expected: {exp}")
        if "executionType" in s:
            block.append(f"Step execution type (code): {s['executionType']}")
        if block:
            parts.append("\n".join(block))
    return "\n\n".join(parts)


def identifiers_to_text(obj: dict) -> str:
    lines: list[str] = []
    if obj.get("id") is not None:
        lines.append(f"TestIT case id: {obj['id']}")
    ext = obj.get("externalId")
    if ext is not None and str(ext).strip():
        lines.append(f"External id: {ext}")
    return "\n".join(lines)


def custom_fields_to_text(raw: object) -> str:
    if not isinstance(raw, list) or not raw:
        return ""
    lines: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        label = (item.get("label") or item.get("name") or "").strip()
        values = item.get("customValues")
        if not isinstance(values, list) or not values:
            continue
        str_vals = [str(v).strip() for v in values if v is not None and str(v).strip()]
        if not str_vals:
            continue
        header = label if label else "Custom field"
        lines.append(f"{header}: {', '.join(str_vals)}")
    return "\n".join(lines)


def related_issues_to_text(raw: object) -> str:
    if not isinstance(raw, list) or not raw:
        return ""
    keys = [str(x).strip() for x in raw if x is not None and str(x).strip()]
    if not keys:
        return ""
    return "Related issues: " + ", ".join(keys)


def behaviour_groups_to_text(raw: object) -> str:
    if not isinstance(raw, list) or not raw:
        return ""
    lines: list[str] = []
    for i, bg in enumerate(raw, start=1):
        if isinstance(bg, dict):
            name = (bg.get("name") or "").strip()
            desc = html_to_text(bg.get("description")) if bg.get("description") else ""
            chunk = f"Behaviour group {i}"
            if name:
                chunk += f": {name}"
            if desc:
                chunk += f"\n{desc}"
            lines.append(chunk)
        else:
            lines.append(str(bg))
    return "\n\n".join(lines)


def execution_attrs_to_text(obj: dict) -> str:
    lines: list[str] = []
    if "executionType" in obj and obj["executionType"] is not None:
        lines.append(f"Case execution type (code): {obj['executionType']}")
    if "priority" in obj and obj["priority"] is not None:
        lines.append(f"Priority (code): {obj['priority']}")
    return "\n".join(lines)


def testcase_to_page_content(obj: dict) -> str:
    id_block = identifiers_to_text(obj)
    name = (obj.get("name") or "").strip()
    summary = html_to_text(obj.get("summary"))
    custom_txt = custom_fields_to_text(obj.get("customFields"))
    related_txt = related_issues_to_text(obj.get("relatedIssues"))
    behaviour_txt = behaviour_groups_to_text(obj.get("behaviourGroups"))
    attrs_txt = execution_attrs_to_text(obj)
    pre = html_to_text(obj.get("preconditions"))
    steps_text = steps_to_text(obj.get("steps"))
    sections: list[str] = []
    if id_block:
        sections.append(id_block)
    if name:
        sections.append(f"Name: {name}")
    if summary:
        sections.append(f"Summary:\n{summary}")
    if custom_txt:
        sections.append(f"Custom fields:\n{custom_txt}")
    if related_txt:
        sections.append(related_txt)
    if behaviour_txt:
        sections.append(f"Behaviour groups:\n{behaviour_txt}")
    if attrs_txt:
        sections.append(attrs_txt)
    if pre:
        sections.append(f"Preconditions:\n{pre}")
    if steps_text:
        sections.append(f"Steps:\n{steps_text}")
    return "\n\n".join(sections)


def testcase_metadata_extra(obj: dict) -> dict[str, str]:
    """Flat strings for vector DB metadata (Chroma-friendly)."""
    extra: dict[str, str] = {}
    keywords: list[str] = []
    test_type = ""
    for item in obj.get("customFields") or []:
        if not isinstance(item, dict):
            continue
        label = (item.get("label") or item.get("name") or "").strip().lower()
        values = item.get("customValues")
        if not isinstance(values, list):
            continue
        str_vals = [str(v).strip() for v in values if v is not None and str(v).strip()]
        if not str_vals:
            continue
        if label == "keywords":
            keywords.extend(str_vals)
        elif "test type" in label or label == "testtype":
            test_type = str_vals[0]
    if keywords:
        joined = ", ".join(keywords)
        extra["keywords"] = joined[:4000] if len(joined) > 4000 else joined
    if test_type:
        extra["test_type"] = test_type[:512]
    return extra


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
            meta.update(testcase_metadata_extra(obj))
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
