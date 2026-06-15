"""
Persistent MCP client.

Instead of starting a new MCP server process on every tool call,
this keeps one MCP server/session alive for the lifetime of the app process.
"""

import asyncio
import atexit
import json
import threading
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class PersistentMCPClient:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.loop.run_forever,
            daemon=True,
        )

        self.exit_stack: AsyncExitStack | None = None
        self.session: ClientSession | None = None
        self.initialized = False
        self.lock = threading.Lock()

    def start(self) -> None:
        with self.lock:
            if self.initialized:
                return

            if not self.thread.is_alive():
                self.thread.start()

            future = asyncio.run_coroutine_threadsafe(
                self._async_start(),
                self.loop,
            )

            future.result()
            self.initialized = True

    async def _async_start(self) -> None:
        project_root = Path(__file__).parents[2]
        server_path = project_root / "app" / "mcp" / "server.py"

        server_params = StdioServerParameters(
            command="python",
            args=[str(server_path)],
        )

        self.exit_stack = AsyncExitStack()

        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await self.session.initialize()

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        self.start()

        future = asyncio.run_coroutine_threadsafe(
            self._async_call_tool(
                tool_name=tool_name,
                arguments=arguments,
            ),
            self.loop,
        )

        return future.result()

    async def _async_call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        if self.session is None:
            raise RuntimeError("MCP session has not been initialized.")

        result = await self.session.call_tool(
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

    def close(self) -> None:
        if not self.initialized:
            return

        if self.exit_stack is not None:
            future = asyncio.run_coroutine_threadsafe(
                self.exit_stack.aclose(),
                self.loop,
            )
            future.result()

        self.loop.call_soon_threadsafe(self.loop.stop)
        self.initialized = False


_mcp_client: PersistentMCPClient | None = None


def get_mcp_client() -> PersistentMCPClient:
    global _mcp_client

    if _mcp_client is None:
        _mcp_client = PersistentMCPClient()
        atexit.register(_mcp_client.close)

    return _mcp_client


def call_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    client = get_mcp_client()

    return client.call_tool(
        tool_name=tool_name,
        arguments=arguments,
    )