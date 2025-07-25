from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3, json
from dotenv import load_dotenv
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

load_dotenv()

app = FastAPI()

session_service = DatabaseSessionService(db_url='sqlite:///./sessions.db')

class AgentRequestBody(BaseModel):
    user_id: str
    message: str

@app.post("/interact/{agent_type}/{agent_id}")
async def interact(body: AgentRequestBody, agent_type: str, agent_id: int):
    if agent_type == "single":
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT agent_name, model, description, instruction, tools FROM single_agents WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()

        name = row[0]
        model = row[1]
        description = row[2]
        instruction = row[3]
        tools = json.loads(row[4])

        from google.adk.agents import LlmAgent
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
        agent = LlmAgent(
            name = "_".join(name.title().split()),
            model = model,
            description = description,
            instruction= instruction,
            tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"), tool_filter=tools)]
        )

        runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
        session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

        content = Content(parts=[Part(text=body.message)], role="user")
        events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

        response_text = ""
        async for event in events:  
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text

        return JSONResponse(content={"response": response_text})
    
    elif agent_type == "multi":
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT agent_name, model, description, instruction, sub_agents, tools FROM multi_agents WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()

        name = row[0]
        model = row[1]
        description = row[2]
        instruction = row[3]
        sub_agents = json.loads(row[4])
        tools = json.loads(row[5])

        from google.adk.agents import LlmAgent
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

        sub_agents_list = []
        for sub in sub_agents:
            sub_agents_list.append(
                LlmAgent(
                    name="_".join(sub.get("name").title().split()),
                    model=sub.get("model"),
                    description=sub.get("description"),
                    instruction=sub.get("instruction"),
                    tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"), tool_filter=sub.get("tools"))]
                )
            )

        agent = LlmAgent(
            name = "_".join(name.title().split()),
            model = model,
            description = description,
            instruction= instruction,
            sub_agents = sub_agents_list,
            tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"), tool_filter=tools)]
        )

        runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
        session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

        content = Content(parts=[Part(text=body.message)], role="user")
        events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

        response_text = ""
        async for event in events:  
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text

        return JSONResponse(content={"response": response_text})

class CreateSingleAgentRequestBody(BaseModel):
    name : str
    model : str
    description : str
    instruction : str
    tools : list[str]

@app.post("/create-single-agent")
def create_single_agent(body: CreateSingleAgentRequestBody):
    import json
    tools_json = json.dumps([tool for tool in body.tools])

    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO single_agents (agent_name, model, description, instruction, tools) VALUES (?, ?, ?, ?, ?);
        """,(body.name, body.model,  body.description, body.instruction, tools_json))
        connection.commit()

class SubAgent(BaseModel):
    name: str
    model: str
    description: str
    instruction: str
    tools: list[str]

class CreateMultiAgentRequestBody(BaseModel): 
    name: str
    model: str
    description: str
    instruction: str
    tools: list[str]
    subagents: list[SubAgent]

@app.post("/create-multi-agent")
def create_multi_agent(body: CreateMultiAgentRequestBody):

    import json
    tools_json = json.dumps([tool for tool in body.tools])
    subagents_as_dicts = [subagent.model_dump() for subagent in body.subagents]
    subagents_json = json.dumps(subagents_as_dicts)

    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO multi_agents (agent_name, model, description, instruction, sub_agents, tools) VALUES (?, ?, ?, ?, ?, ?);
        """,(body.name, body.model,  body.description, body.instruction, subagents_json, tools_json))
        connection.commit()

@app.post("/delete/{agent_type}/{agent_id}")
def delete_agent(agent_type: str, agent_id: int):
    if agent_type == "single":
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM single_agents WHERE agent_id=?",(agent_id,))
            connection.commit()

    elif agent_type == "multi":
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM multi_agents WHERE agent_id=?",(agent_id,))
            connection.commit()

    return {"status": "success"}
        
@app.get("/get-agents")
def get_agents():
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT agent_id, agent_name FROM single_agents")
        single_result = cursor.fetchall()
        single_agents = [{"id": row[0], "name": row[1], "agent_type": "single"} for row in single_result]

        cursor.execute("SELECT agent_id, agent_name FROM multi_agents")
        multi_result = cursor.fetchall()
        multi_agents = [{"id": row[0], "name": row[1], "agent_type": "multi"} for row in multi_result]

    return {
        "single_agents": single_agents,
        "multi_agents": multi_agents
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, port=8080)




















# USE LATER FOR MEMORY FEATURE

# At the top of your file
# agents = {}  # {session_id: {"agent": LlmAgent, "runner": Runner}}

# @app.post("/interact/{agent_type}/{agent_id}")
# async def interact(body: AgentRequestBody, agent_type: str, agent_id: int):
#     """ Handle interaction with a single or multi agent """
#     with sqlite3.connect("database.db") as connection:
#         cursor = connection.cursor()
#         if agent_type == "single":
#             cursor.execute("SELECT agent_name, model, description, instruction, tools FROM single_agents WHERE agent_id = ?", (agent_id,))
#         else:
#             cursor.execute("SELECT agent_name, model, description, instruction, sub_agents, tools FROM multi_agents WHERE agent_id = ?", (agent_id,))
#         row = cursor.fetchone()

#     name = row[0]
#     model = row[1]
#     description = row[2]
#     instruction = row[3]
#     if agent_type == "single":
#         tools = json.loads(row[4])

#         from google.adk.agents import LlmAgent
#         from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

#         agent_key = f"{body.user_id}_{agent_id}"

#         if agent_key not in agents:
#             agent = LlmAgent(
#                 name="_".join(name.title().split()),
#                 model=model,
#                 description=description,
#                 instruction=instruction,
#                 tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"),
#                                    tool_filter=tools)]

#             )
#             runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
#             session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

#             agents[agent_key] = {"agent": agent, "runner": runner, "session": session}
#         else:
#             agent = agents[agent_key]["agent"]
#             runner = agents[agent_key]["runner"]
#             session = agents[agent_key]["session"]

#     else:
#         sub_agents = json.loads(row[4])
#         tools = json.loads(row[5])

#         from google.adk.agents import LlmAgent
#         from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

#         agent_key = f"{body.user_id}_{agent_id}"

#         if agent_key not in agents:
#             sub_agents_list = []
#             for sub in sub_agents:
#                 sub_agents_list.append(
#                     LlmAgent(
#                         name="_".join(sub.get("name").title().split()),
#                         model=sub.get("model"),
#                         description=sub.get("description"),
#                         instruction=sub.get("instruction"),
#                         tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"),
#                                          tool_filter=sub.get("tools"))]
#                     )
#                 )

#             agent = LlmAgent(
#                 name="_".join(name.title().split()),
#                 model=model,
#                 description=description,
#                 instruction=instruction,
#                 sub_agents=sub_agents_list,
#                 tools=[MCPToolset(connection_params=SseServerParams(url="http://127.0.0.1:8000/sse"),
#                                    tool_filter=tools)]

#             )
#             runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
#             session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

#             agents[agent_key] = {"agent": agent, "runner": runner, "session": session}
#         else:
#             agent = agents[agent_key]["agent"]
#             runner = agents[agent_key]["runner"]
#             session = agents[agent_key]["session"]

#     # Prepare content and send
#     content = Content(parts=[Part(text=body.message)], role="user")
#     events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

#     response = ""
#     async for event in events:
#         if event.is_final_response() and event.content and event.content.parts:
#             response = event.content.parts[0].text

#     return JSONResponse(content={"response": response})