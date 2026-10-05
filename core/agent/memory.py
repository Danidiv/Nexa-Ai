import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "aziz_memory.db")


@contextmanager
def _connect():
    """Open a SQLite connection and ALWAYS close it.

    sqlite3.Connection's own context manager commits/rolls back but does
    not close the connection. The explicit contextmanager here prevents
    Windows from keeping aziz_memory.db locked after tests finish.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_memory():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                pending_question TEXT,
                agent_state TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                action TEXT NOT NULL,
                arguments_json TEXT NOT NULL,
                result TEXT,
                success INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
        """)

        # Setup 4.14 migration: add persistent agent state to databases
        # created by Setup 4.9-4.13.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(conversations)").fetchall()
        }
        if "agent_state" not in columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN agent_state TEXT")


def _now():
    return datetime.now(timezone.utc).isoformat()


def create_conversation(conversation_id, task):
    initialize_memory()
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations(id, task, status, created_at, updated_at) VALUES (?, ?, 'active', ?, ?)",
            (conversation_id, task, now, now),
        )


def update_conversation(conversation_id, status=None, pending_question=None, agent_state=None):
    """Update conversation lifecycle and optionally persist agent state.

    agent_state is JSON-encoded only when supplied, so older callers can
    continue updating status/question without accidentally erasing state.
    """
    initialize_memory()
    now = _now()
    with _connect() as conn:
        if agent_state is not None:
            state_json = json.dumps(agent_state, ensure_ascii=False, sort_keys=True)
            if status is None:
                conn.execute(
                    "UPDATE conversations SET pending_question=?, agent_state=?, updated_at=? WHERE id=?",
                    (pending_question, state_json, now, conversation_id),
                )
            else:
                conn.execute(
                    "UPDATE conversations SET status=?, pending_question=?, agent_state=?, updated_at=? WHERE id=?",
                    (status, pending_question, state_json, now, conversation_id),
                )
        elif status is None:
            conn.execute(
                "UPDATE conversations SET pending_question=?, updated_at=? WHERE id=?",
                (pending_question, now, conversation_id),
            )
        else:
            conn.execute(
                "UPDATE conversations SET status=?, pending_question=?, updated_at=? WHERE id=?",
                (status, pending_question, now, conversation_id),
            )

def set_conversation_status(conversation_id, status, pending_question=None, agent_state=None):
    """Set one of the explicit Setup 4.15 lifecycle states."""
    allowed = {"active", "running", "waiting_for_user", "completed"}
    if status not in allowed:
        raise ValueError(f"Invalid conversation status: {status}")
    return update_conversation(
        conversation_id,
        status=status,
        pending_question=pending_question,
        agent_state=agent_state,
    )

def recoverable_conversations(limit=20):
    """Return newest conversations that can safely be recovered."""
    initialize_memory()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, task, status, created_at, updated_at, pending_question "
            "FROM conversations "
            "WHERE status IN ('active', 'running', 'waiting_for_user') "
            "ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

def add_message(conversation_id, role, content):
    initialize_memory()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversation_messages(conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, _now()),
        )


def add_action(conversation_id, action, arguments, result, success):
    initialize_memory()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversation_actions(conversation_id, action, arguments_json, result, success, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conversation_id, action, json.dumps(arguments, ensure_ascii=False, sort_keys=True), str(result), int(bool(success)), _now()),
        )


def list_conversations(limit=20):
    initialize_memory()
    with _connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT id, task, status, created_at, updated_at, pending_question FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()]


def get_conversation(conversation_id):
    initialize_memory()
    with _connect() as conn:
        conversation = conn.execute(
            "SELECT * FROM conversations WHERE id=?", (conversation_id,)
        ).fetchone()
        if conversation is None:
            return None
        messages = conn.execute(
            "SELECT role, content, created_at FROM conversation_messages WHERE conversation_id=? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        actions = conn.execute(
            "SELECT action, arguments_json, result, success, created_at FROM conversation_actions WHERE conversation_id=? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        data = dict(conversation)
        data["messages"] = [dict(row) for row in messages]
        data["actions"] = [dict(row) for row in actions]
        return data


def resume_conversation(conversation_id):
    """Return a conversation prepared for restoring an AgentSession."""
    data = get_conversation(conversation_id)
    if data is None:
        return None

    # Resume means the user intends to continue the saved task.
    if data.get("status") != "active":
        update_conversation(
            conversation_id,
            status="active",
            pending_question=data.get("pending_question"),
        )
        data["status"] = "active"

    return data
