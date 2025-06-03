import sqlite3

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import pickle
import asyncio

from dotenv import load_dotenv

load_dotenv()

with sqlite3.connect('./api/database.db') as conn:
    cursor = conn.cursor()

    cursor.execute("DELETE FROM multi_agents")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS multi_agents (
        agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT NOT NULL,
        model TEXT,
        description TEXT,
        instruction TEXT,
        sub_agents TEXT,
        agent_instance BLOB
    );
    """)
    conn.commit()



    