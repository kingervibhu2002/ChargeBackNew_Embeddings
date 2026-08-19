"""
load_encyclopedia.py — Index the full Chargeback Encyclopedia into Qdrant.

Walks chargeback-encyclopedia/ recursively, reads every .md file,
strips YAML frontmatter for metadata, and upserts each document into
the vector store via the MCP RAG server.

Usage:
    python load_encyclopedia.py              # index everything
    python load_encyclopedia.py --dry-run    # count docs without indexing
    python load_encyclopedia.py --section 04_Visa  # index one section only

The script is idempotent — re-running it re-indexes all documents (useful
when you update or add files).
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ENCYCLOPEDIA_DIR = Path(__file__).parent / "chargeback-encyclopedia"


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_OVERVIEW_RE    = re.compile(r"##\s+Overview\s*\n(.*?)(?=\n##|\Z)", re.DOTALL)


def _extract_overview(body: str) -> str:
    """
    Pull the ## Overview section from a document body.
    Falls back to the first non-empty paragraph if no ## Overview heading exists.
    Capped at 600 characters so it stays well within token budgets.
    """
    m = _OVERVIEW_RE.search(body)
    if m:
        return m.group(1).strip()[:600]
    # Fallback: first non-empty paragraph
    for para in body.split("\n\n"):
        clean = para.strip()
        if clean and not clean.startswith("#"):
            return clean[:600]
    return body[:600]


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Split a Markdown file into (metadata_dict, body_text).
    If no YAML frontmatter is found, returns ({}, full_text).
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    body = text[m.end():]
    return meta, body


# ---------------------------------------------------------------------------
# Document discovery
# ---------------------------------------------------------------------------

def discover_documents(section_filter: str | None = None) -> list[dict]:
    """
    Walk encyclopedia dir and return a list of document dicts:
      { title, content, metadata, file_path }
    """
    docs = []
    root = ENCYCLOPEDIA_DIR

    if not root.exists():
        print(f"ERROR: {root} does not exist. Run from the project root.")
        sys.exit(1)

    md_files = sorted(root.rglob("*.md"))

    for path in md_files:
        # Optional section filter
        if section_filter and section_filter not in str(path):
            continue

        raw = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)

        # Derive title: prefer frontmatter, fall back to filename
        title = meta.get("title") or path.stem.replace("_", " ")

        # Build rich content = title + body (helps retrieval)
        content = f"# {title}\n\n{body.strip()}"
        summary = _extract_overview(body)

        docs.append({
            "title":     title,
            "content":   content,
            "summary":   summary,
            "metadata":  meta,
            "file_path": str(path.relative_to(ENCYCLOPEDIA_DIR)),
        })

    return docs


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

async def index_documents(docs: list[dict], dry_run: bool = False) -> None:
    if dry_run:
        print(f"\nDry run — {len(docs)} documents found:\n")
        for i, doc in enumerate(docs, 1):
            print(f"  {i:3}. [{doc['file_path']}]  {doc['title']}")
        return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["rag_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            total   = len(docs)
            success = 0
            failed  = []

            print(f"\nIndexing {total} encyclopedia documents into Qdrant...\n")

            for i, doc in enumerate(docs, 1):
                try:
                    meta = doc.get("metadata", {})
                    # Derive section from file path (first path component)
                    section = doc["file_path"].split("/")[0] if "/" in doc["file_path"] else ""
                    result = await session.call_tool(
                        "add_document",
                        {
                            "title":         doc["title"],
                            "content":       doc["content"],
                            "summary":       doc["summary"],
                            "section":       meta.get("section", section),
                            "network":       meta.get("network", ""),
                            "reason_code":   str(meta.get("reason_code", "")),
                            "document_type": meta.get("chargeback_type", meta.get("document_type", "")),
                            "keywords":      ", ".join(meta.get("tags", [])) if meta.get("tags") else "",
                        },
                    )
                    status = result.content[0].text if result.content else "OK"
                    print(f"  [{i:3}/{total}] ✓  {doc['file_path']}")
                    success += 1
                except Exception as e:
                    print(f"  [{i:3}/{total}] ✗  {doc['file_path']}  ERROR: {e}")
                    failed.append(doc["file_path"])

            print(f"\n{'='*60}")
            print(f"  Indexed : {success}/{total}")
            if failed:
                print(f"  Failed  : {len(failed)}")
                for f in failed:
                    print(f"    - {f}")
            print(f"{'='*60}")
            print("\nKnowledge base ready. Restart api_server.py to use the new documents.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index Chargeback Encyclopedia into Qdrant")
    parser.add_argument("--dry-run",  action="store_true", help="List documents without indexing")
    parser.add_argument("--section",  default=None,        help="Index only one section, e.g. 04_Visa")
    args = parser.parse_args()

    docs = discover_documents(section_filter=args.section)

    if not docs:
        print("No documents found. Check the encyclopedia directory.")
        sys.exit(1)

    print(f"Found {len(docs)} documents" + (f" in section '{args.section}'" if args.section else ""))

    asyncio.run(index_documents(docs, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
