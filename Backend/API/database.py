import sqlite3
from sqlite3 import Connection
from fastapi import HTTPException

DATABASE_PATH = '../DB/MultipleChoiceTool.db'

# Database setup
def get_db_connection() -> Connection:
    """Returns a SQLite connection."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Allows column access by name
        return conn
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
