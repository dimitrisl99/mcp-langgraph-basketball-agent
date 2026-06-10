import asyncio #επειδή το MCP client δουλεύει ασύγχρονα γιατί η επικοινωνία client-server θέλει await
from pathlib import Path

from mcp import ClientSession, StdioServerParameters #Τα 2 βασικά πράγματα απο MCP SDK
#ClientSession είναι η σύνδεση/συνεδρία ανάμεσα στον client και τον server
#StdioServerParameters λέει στον client πως να ξεκινήσει τον server

from mcp.client.stdio import stdio_client #Το studio σημαίνει οτι client & Server μιλάνε τοπικά
#μέσα απο input/output streams

#Για να ξεκινήσεις τον MCP server, τρέξε: python app/mcp/server.py --> o client θα τρέξει μόνος του το server.py
async def main():
    server_path = Path(__file__).parent / "server.py"

    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )

    #ανοίγει η επικοινωνία με τον MCP server (read --> κανάλι που ο client διαβάζει απαντήσεις /
    #write --> κανάλι που ο client στέλνει αιτήματα
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session: #δημιουργεί MCP session
            await session.initialize() # το αρχικό "handshake"

            tools = await session.list_tools() #ζητάμε απο τον server να μας πει ποιά tools έχει
            print("Available tools:")
            print(tools)

            result = await session.call_tool(
                "answer_basketball_question",
                arguments={
                    "question": "How does Spain Pick and Roll work?",
                    "top_k": 5,
                },
            )

            print("\nTool result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main()) #εδώ ξεκινάει το async πρόγραμμα