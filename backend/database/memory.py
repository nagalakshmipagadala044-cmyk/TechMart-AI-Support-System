import sqlite3 #importing sqlite3 for database operations
import os
from datetime import datetime, timezone #print timestamps in UTC for consistency

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")

def init_db():
    conn = sqlite3.connect(DB_PATH) #connect to the SQLite database (or create it if it doesn't exist)
    cursor = conn.cursor() 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            agent TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class ConversationMemory:
    def __init__(self):
        init_db()

    def add_message(self, session_id: str, role: str, content: str, agent: str = None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, agent, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, agent, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 10):
        """Returns recent messages formatted for passing to an agent as conversation_history"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        # Reverse to chronological order, format as {role, content} dicts
        history = [{"role": role, "content": content} for role, content in reversed(rows)]
        return history

    def get_full_log(self, session_id: str):
        """Returns full conversation with agent attribution, for display/debugging"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, agent, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1], "agent": r[2], "timestamp": r[3]} for r in rows]


if __name__ == "__main__":
    memory = ConversationMemory()
    memory.add_message("test-session-1", "user", "I paid but Premium is still locked")
    memory.add_message("test-session-1", "assistant", "Let me check that for you", agent="billing")

    history = memory.get_history("test-session-1")
    print("History:", history)