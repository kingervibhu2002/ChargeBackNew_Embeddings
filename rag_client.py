"""
MCP RAG Client

Demonstrates end-to-end RAG with Claude as the orchestrator:
  1. Spawns the MCP RAG server as a subprocess.
  2. Indexes a set of sample documents via the `add_document` MCP tool.
  3. Lets Claude answer user questions by calling `search` and synthesising
     the retrieved context — all through the MCP tool protocol.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python rag_client.py
"""

import asyncio
import json
import os
import sys

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------------------------------------------------------------------------
# Sample knowledge base
# ---------------------------------------------------------------------------

# Demo questions that exercise retrieval across different chargeback documents
DEMO_QUESTIONS = [
    "What is a chargeback and who are the parties involved?",
    "What is the difference between friendly fraud and real fraud?",
    "How do I write a strong chargeback rebuttal letter?",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mcp_tools_to_anthropic(tools) -> list[dict]:
    """Convert MCP tool definitions to the format Anthropic's API expects."""
    return [
        {
            "name": t.name,
            "description": t.description or "",
            "input_schema": t.inputSchema,
        }
        for t in tools
    ]


async def run_agentic_loop(
    client: anthropic.Anthropic,
    session: ClientSession,
    anthropic_tools: list[dict],
    question: str,
) -> str:
    """
    Run a single agentic turn:
      - Send the user question to Claude with the MCP tools available.
      - If Claude calls a tool, execute it via the MCP session and feed the
        result back.
      - Repeat until Claude stops with end_turn and returns its final answer.
    """
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "You are a helpful assistant with access to a knowledge base. "
                "When the user asks a question, always call the `search` tool first "
                "to retrieve relevant context before answering. "
                "Base your answer on the retrieved documents and be concise."
            ),
            tools=anthropic_tools,
            messages=messages,
        )

        # Collect any text the model emitted before/without tool use
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]

        if response.stop_reason == "end_turn":
            return "\n".join(text_blocks)

        if response.stop_reason == "tool_use":
            # Append assistant turn (may include tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_input = block.input
                print(f"    → [{tool_name}] {json.dumps(tool_input)}")

                mcp_result = await session.call_tool(tool_name, tool_input)
                result_text = (
                    mcp_result.content[0].text
                    if mcp_result.content
                    else "(no result)"
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason — return whatever text we have
            return "\n".join(text_blocks) or f"(stopped: {response.stop_reason})"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    server_params = StdioServerParameters(
        command=sys.executable,        # same Python interpreter running this script
        args=["rag_server.py"],
        env=None,                      # inherit current environment
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ------------------------------------------------------------------
            # 1. Show what's in the knowledge base
            # ------------------------------------------------------------------
            #    Run load_chargeback_docs.py first to populate the store.
            # ------------------------------------------------------------------
            list_result = await session.call_tool("list_documents", {})
            raw = list_result.content[0].text
            if raw.startswith("["):
                docs = json.loads(raw)
                print(f"Knowledge base: {len(docs)} document(s) indexed.")
                for d in docs:
                    print(f"  [{d['id']}] {d['title']}")
            else:
                print(raw)
                print("Tip: run `python load_chargeback_docs.py` to populate the knowledge base.")
                print()

            # ------------------------------------------------------------------
            # 3. Answer questions with Claude + RAG
            # ------------------------------------------------------------------
            mcp_tools_list = (await session.list_tools()).tools
            anthropic_tools = mcp_tools_to_anthropic(mcp_tools_list)
            claude = anthropic.Anthropic()

            print()
            print("=" * 60)
            print("Q&A with Claude (RAG via MCP)")
            print("=" * 60)
            for question in DEMO_QUESTIONS:
                print(f"\nQ: {question}")
                answer = await run_agentic_loop(
                    claude, session, anthropic_tools, question
                )
                print(f"A: {answer}")

            # ------------------------------------------------------------------
            # 4. Interactive mode
            # ------------------------------------------------------------------
            print()
            print("=" * 60)
            print("Interactive mode  (type 'quit' to exit)")
            print("=" * 60)
            while True:
                try:
                    user_input = input("\nYour question: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if user_input.lower() in {"quit", "exit", "q"}:
                    break
                if not user_input:
                    continue
                answer = await run_agentic_loop(
                    claude, session, anthropic_tools, user_input
                )
                print(f"Answer: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
