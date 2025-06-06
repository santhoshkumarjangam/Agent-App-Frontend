import sqlite3, json

with sqlite3.connect("./api/database.db") as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT agent_name, model, description, instruction, tools FROM single_agents WHERE agent_id = 2")
    row = cursor.fetchone()

    name = row[0]
    model = row[1]
    description = row[2]
    instruction = row[3]
    tools = json.loads(row[4])

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

root_agent = Agent(
    name = "_".join(name.title().split()),
    model = model,
    description = description,
    instruction= instruction,
    tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"), tool_filter=tools)]
)