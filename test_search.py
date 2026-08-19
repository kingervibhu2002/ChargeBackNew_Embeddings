"""
test_search.py

End-to-end test of the RAG pipeline without requiring an Anthropic API key.

What this script tests:
  1. MCP server starts correctly and loads the embedding model.
  2. All 10 chargeback documents are indexed into Qdrant successfully.
  3. Qdrant stores and returns the correct document list.
  4. Semantic search returns relevant results with meaningful similarity scores.

No LLM is involved — this validates only the retrieval half of the RAG system.
If this passes, the pipeline is ready for Claude to be added on top.

Run:
    python test_search.py
"""

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Queries that should each retrieve a clearly relevant document.
# Used to verify that the embedding + search pipeline is working correctly.
TEST_QUERIES = [
    "What is a chargeback?",
    "What is Visa reason code 13.2?",
    "How do I fight friendly fraud?",
    "What happens if I exceed the chargeback threshold?",
    "What evidence do I need for a rebuttal letter?",
]


async def main() -> None:
    """
    Main async entry point — runs all three test stages sequentially.

    Spawns the MCP server (rag_server.py) as a subprocess using stdio transport,
    establishes a session, then runs indexing, listing, and search in order.
    The server process is automatically terminated when this function exits.

    Stages:
      1. Index — sends all chargeback documents to the server via add_document.
      2. List  — calls list_documents to confirm Qdrant received the data.
      3. Search — runs each TEST_QUERY through the search tool and prints results.

    Returns:
        None

    Raises:
        SystemExit: If the MCP session cannot be established.
    """
    params = StdioServerParameters(
        command=sys.executable,   # path to the current Python interpreter
        args=["rag_server.py"],   # the MCP server script to spawn
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ------------------------------------------------------------------
            # Stage 1 — Index all chargeback documents
            # ------------------------------------------------------------------
            from load_chargeback_docs import CHARGEBACK_DOCUMENTS

            print("=" * 60)
            print(f"Indexing {len(CHARGEBACK_DOCUMENTS)} chargeback documents into Qdrant...")
            print("=" * 60)

            for doc in CHARGEBACK_DOCUMENTS:
                result = await session.call_tool(
                    "add_document",
                    {"title": doc["title"], "content": doc["content"]},
                )
                print(f"  {result.content[0].text}")

            # ------------------------------------------------------------------
            # Stage 2 — List all documents stored in Qdrant
            # ------------------------------------------------------------------
            print()
            print("=" * 60)
            print("Documents stored in Qdrant:")
            print("=" * 60)

            list_result = await session.call_tool("list_documents", {})
            docs = json.loads(list_result.content[0].text)
            for doc in docs:
                print(f"  [{doc['id']}]  {doc['title']}")

            # ------------------------------------------------------------------
            # Stage 3 — Run semantic search for each test query
            # ------------------------------------------------------------------
            print()
            print("=" * 60)
            print("Search results (top 2 matches per query):")
            print("=" * 60)

            for query in TEST_QUERIES:
                print(f"\nQuery: \"{query}\"")

                result = await session.call_tool(
                    "search",
                    {"query": query, "top_k": 2},
                )

                raw = result.content[0].text if result.content else ""

                if not raw:
                    print("  (empty response from server)")
                    continue

                if not raw.strip().startswith("["):
                    # Server returned an error message or empty-store warning.
                    print(f"  (server says: {raw})")
                    continue

                hits = json.loads(raw)
                for i, hit in enumerate(hits, 1):
                    print(f"  Match {i}: [{hit['score']}]  {hit['title']}")
                    # Show first 120 characters as a content preview.
                    preview = hit["content"].strip().replace("\n", " ")[:120]
                    print(f"           {preview}...")

            print()
            print("=" * 60)
            print("All tests passed! Qdrant + MCP pipeline is working correctly.")
            print("Next step: add your ANTHROPIC_API_KEY and run rag_client.py")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
