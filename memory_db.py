import sqlite3
from pathlib import Path

MEMORY_DB = Path("memories.db")


def init_memory_db() -> None:
    """Create the memories and pending_memories tables if they do not exist."""
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                fact       TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # HITL: facts waiting for approval
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_memories (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                fact       TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_memory(user_id: str, fact: str) -> None:
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            "INSERT INTO memories (user_id, fact) VALUES (?, ?)",
            (user_id, fact),
        )


def get_memories(user_id: str) -> list[str]:
    with sqlite3.connect(MEMORY_DB) as conn:
        rows = conn.execute(
            "SELECT fact FROM memories WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        ).fetchall()
    return [row[0] for row in rows]


def get_memories_with_ids(user_id: str) -> list[tuple[int, str]]:
    """Return (id, fact) pairs so the UI can delete single facts."""
    with sqlite3.connect(MEMORY_DB) as conn:
        return conn.execute(
            "SELECT id, fact FROM memories WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        ).fetchall()


def delete_memory(user_id: str, memory_id: int) -> None:
    """Delete one fact; user_id check prevents deleting other users' facts."""
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            "DELETE FROM memories WHERE id = ? AND user_id = ?",
            (memory_id, user_id),
        )


def add_pending(user_id: str, fact: str) -> None:
    """Agent proposes a fact; it waits for human approval."""
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            "INSERT INTO pending_memories (user_id, fact) VALUES (?, ?)",
            (user_id, fact),
        )


def get_pending(user_id: str) -> list[tuple[int, str]]:
    """Return (id, fact) pairs that are waiting for approval."""
    with sqlite3.connect(MEMORY_DB) as conn:
        return conn.execute(
            "SELECT id, fact FROM pending_memories WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        ).fetchall()


def approve_pending(user_id: str, pending_id: int) -> None:
    """Move a pending fact into long-term memory."""
    with sqlite3.connect(MEMORY_DB) as conn:
        row = conn.execute(
            "SELECT fact FROM pending_memories WHERE id = ? AND user_id = ?",
            (pending_id, user_id),
        ).fetchone()
        if row:
            conn.execute(
                "INSERT INTO memories (user_id, fact) VALUES (?, ?)",
                (user_id, row[0]),
            )
            conn.execute(
                "DELETE FROM pending_memories WHERE id = ?",
                (pending_id,),
            )


def discard_pending(user_id: str, pending_id: int) -> None:
    """Reject a pending fact."""
    with sqlite3.connect(MEMORY_DB) as conn:
        conn.execute(
            "DELETE FROM pending_memories WHERE id = ? AND user_id = ?",
            (pending_id, user_id),
        )