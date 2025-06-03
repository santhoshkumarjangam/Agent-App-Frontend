from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3, pickle
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from agent_templates import SingleAgent, MultiAgent

load_dotenv()

app = FastAPI()

session_service = DatabaseSessionService(db_url='sqlite:///./sessions.db')

class AgentRequestBody(BaseModel):
    user_id: str
    message: str

@app.post("/interact/single/{agent_id}")
async def interact_single(body: AgentRequestBody, agent_id: int):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT agent_instance FROM single_agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()

    agent = pickle.loads(row[0])
    runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
    session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

    content = Content(parts=[Part(text=body.message)], role="user")
    events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

    response_text = ""
    async for event in events:  
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text

    return JSONResponse(content={"response": response_text})

@app.post("/interact/multi/{agent_id}")
async def interact_multi(body: AgentRequestBody, agent_id: int):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT agent_instance FROM multi_agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()

    agent = pickle.loads(row[0])
    runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)
    session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)

    content = Content(parts=[Part(text=body.message)], role="user")
    events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

    final_response = ""

    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            final_response += event.content.parts[0].text

    return JSONResponse(content={
        "response": final_response,
    })

class CreateSingleAgentRequestBody(BaseModel):
    name : str
    model : str
    description : str
    instruction : str

@app.post("/create-single-agent")
def create_single_agent(body: CreateSingleAgentRequestBody):

    single_agent = SingleAgent(body.name, body.model, body.description, body.instruction)
    agent = single_agent.create_ADK_agent()

    serialized = pickle.dumps(agent)

    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO single_agents (agent_name, model, description, instruction, agent_instance) VALUES (?, ?, ?, ?, ?);
        """,(single_agent.name, single_agent.model,  single_agent.description, single_agent.instruction, serialized))
        connection.commit()

    return {"STATUS":"Success"}

class SubAgent(BaseModel):
    name: str
    model: str
    description: str
    instruction: str

class CreateMultiAgentRequestBody(BaseModel): 
    name: str
    model: str
    description: str
    instruction: str
    subagents: list[SubAgent]

@app.post("/create-multi-agent")
def create_multi_agent(body: CreateMultiAgentRequestBody):

    subagents = []
    for sub in body.subagents:
        subagents.append(
            Agent(
                name="_".join(sub.name.title().split()),
                model=sub.model,
                description=sub.description,
                instruction=sub.instruction
            )
        )
    
    multi_agent = MultiAgent(
        name=body.name,
        model=body.model,
        description=body.description,
        instruction=body.instruction,
        subagents=subagents
    )

    agent = multi_agent.create_ADK_agent()

    serialized = pickle.dumps(agent)

    import json
    subagents_json = json.dumps([dict(sa) for sa in body.subagents]) # to store subagents info to the database

    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO multi_agents (agent_name, model, description, instruction, sub_agents, agent_instance) VALUES (?, ?, ?, ?, ?, ?);
        """, (multi_agent.name, multi_agent.model, multi_agent.description, multi_agent.instruction, subagents_json, serialized))

        connection.commit()

    return {"STATUS":"Success"}

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
    uvicorn.run(app=app)