import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters


from mcp.client.stdio import stdio_client

async def main():
    server_path = Path(__file__).parent / "server.py"

    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session: #create MCP session
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            print(tools)

            result = await session.call_tool(
                "answer_nba_stats_question",
                arguments={
                    "question": "Who are the top 5 players by assists?"
                },
            )

            print("\nTool result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())