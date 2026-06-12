"""
LangGraph node --> call_mcp_tool --> MCP server.py --> MCP tool --> RAG ή SQL --> Answer
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_tool_async(
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """
    Calls an MCP tool asynchronously through the local MCP server.
    """

    project_root = Path(__file__).parents[2]
    server_path = project_root / "app" / "mcp" / "server.py"

    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.structuredContent and "result" in result.structuredContent:
                raw_result = result.structuredContent["result"]

                try:
                    return json.loads(raw_result)
                except json.JSONDecodeError:
                    return raw_result

            if result.content:
                return result.content[0].text

            return ""


def call_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """
    Synchronous wrapper around the async MCP call.
    LangGraph nodes can call this more easily.
    """

    return asyncio.run(
        call_mcp_tool_async(
            tool_name=tool_name,
            arguments=arguments,
        )
    )