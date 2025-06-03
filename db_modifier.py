import sqlite3

with sqlite3.connect("./api/database.db") as conn:
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE single_agents (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    agent_instance BLOB
    );
    """)
    conn.commit()