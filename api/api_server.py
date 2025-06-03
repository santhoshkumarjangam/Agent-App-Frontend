from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3, pickle
from dotenv import load_dotenv
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from agent_templates import SingleAgent

load_dotenv()

app = FastAPI()

session_service = DatabaseSessionService(db_url='sqlite:///./sessions.db')

class AgentRequestBody(BaseModel):
    user_id: str
    message: str

@app.post("/interact/{agent_id}")
async def interact(body: AgentRequestBody, agent_id: int):
    print("interact has called",agent_id)
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT agent_instance FROM single_agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()

    agent = pickle.loads(row[0])
    print(agent)

    runner = Runner(app_name="MyApp", agent=agent, session_service=session_service)

    session = await session_service.create_session(app_name="MyApp", user_id=body.user_id)
    
    content = Content(parts=[Part(text=body.message)], role="user")
    events = runner.run_async(user_id=body.user_id, session_id=session.id, new_message=content)

    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text

    return JSONResponse(content=response_text)

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
        INSERT INTO single_agents (agent_name, agent_instance) VALUES (?, ?);
        """,(single_agent.name, serialized))
        connection.commit()

    return {"STATUS":"Success"}

class CreateMultiAgentRequestBody(BaseModel):
    name : str
    model : str
    description : str
    instruction : str
    subagents : list

@app.post("/create-multi-agent")
def create_multi_agent(body: CreateMultiAgentRequestBody):
    pass

@app.get("/get-agents")
def get_agents():
    import sqlite3

    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT agent_id, agent_name from single_agents")
        result = cursor.fetchall()
        agents = [{"id": row[0], "name": row[1]} for row in result]

    return {"agents":agents}