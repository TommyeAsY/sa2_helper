import sqlite3
from pprint import pprint

query = "SELECT * FROM messages LIMIT 50;"

conn = sqlite3.connect("rag/knowledge_base/data/guild_1449773237595537601.sqlite")
cursor = conn.cursor()

cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    pprint(row)

conn.close()
