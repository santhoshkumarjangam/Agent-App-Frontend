import sqlite3

with sqlite3.connect('./api/database.db') as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM single_agents;")
    cursor.execute("ALTER TABLE single_agents ADD COLUMN tools TEXT;")

# with sqlite3.connect('./api/database.db') as conn:
#     cursor = conn.cursor()

#     cursor.execute("DELETE FROM multi_agents")

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS multi_agents (
#         agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         agent_name TEXT NOT NULL,
#         model TEXT,
#         description TEXT,
#         instruction TEXT,
#         sub_agents TEXT,
#         agent_instance BLOB
#     );
#     """)
#     conn.commit()

# with sqlite3.connect("todo.db") as conn:
#     cur = conn.cursor()
#     cur.execute("""CREATE TABLE users(
#                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name VARCHAR(50)
#             )""")
#     cur.execute("DROP TABLE todo")
#     cur.execute("""CREATE TABLE todo(
#                 user_id INTEGER,
#                 task_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 task VARCHAR(50),
#                 status BOOLEAN,
#                 FOREIGN KEY (user_id) REFERENCES users(user_id)
#         )"""
#     )