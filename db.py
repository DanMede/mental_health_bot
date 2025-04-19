import sqlite3
from datetime import datetime

DB_PATH = "moods.db"

def init_db():
    """
    สร้างตาราง moods ถ้ายังไม่มี
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_mood(user_id: int, mood: str):
    """
    บันทึกอารมณ์ user พร้อมเวลา UTC
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO moods (user_id, mood, timestamp) VALUES (?, ?, ?)",
        (user_id, mood, datetime.utcnow().isoformat())
    )
   
