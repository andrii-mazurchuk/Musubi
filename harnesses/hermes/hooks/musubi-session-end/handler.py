"""
Musubi — session:end hook for Hermes.

1. Removes the injected Musubi context file from Hermes's memory directory.
2. Pulls the full session transcript from Hermes's SQLite store.
3. Spawns a headless Claude Code session (via the `claude` CLI) to run the
   Musubi processing agent, which writes updated relationship state + memory files
   using its built-in Write tool.

No external Python packages required — uses the same `claude -p` pattern as
the rest of the Hermes agent infrastructure.

Context keys expected from Hermes:
    platform    — string identifier of the originating platform
    user_id     — platform-native user identifier
    session_id  — Hermes internal session UUID

DB schema note:
    Hermes stores conversations in ~/.hermes/hermes_state.db.
    The query in _get_transcript() targets the most common schema pattern.
    If your Hermes version uses different table/column names, adjust there.
"""

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
MUSUBI_DIR = HERMES_DIR / "musubi"
INJECT_DIR = HERMES_DIR / "memories"
HERMES_DB = HERMES_DIR / "hermes_state.db"

# claude CLI — matches the path used by the rest of the Hermes infrastructure
CLAUDE = Path.home() / ".local" / "bin" / "claude"


async def handle(event_type: str, context: dict) -> None:
    platform = context.get("platform", "unknown")
    user_id = context.get("user_id", "default")
    session_id = context.get("session_id")
    musubi_id = f"{platform}_{user_id}"

    # Clean up injected context file regardless of what follows
    inject_file = INJECT_DIR / f"musubi_{musubi_id}.md"
    if inject_file.exists():
        inject_file.unlink()

    if not session_id:
        print("[musubi] No session_id in context — skipping post-processing.", file=sys.stderr)
        return

    transcript = _get_transcript(session_id)
    if not transcript:
        return  # Empty or unreadable session — nothing to process

    user_file = MUSUBI_DIR / "data" / "users" / f"{musubi_id}.md"
    memories_file = MUSUBI_DIR / "data" / "memories" / f"{musubi_id}.md"

    _run_processing_agent(musubi_id, transcript, user_file, memories_file)


def _get_transcript(session_id: str) -> str:
    """
    Pull conversation turns from Hermes's SQLite store.

    Tries two common schema patterns. If neither works, prints a diagnostic
    and returns empty string so the session-end hook fails gracefully.
    """
    import sqlite3

    if not HERMES_DB.exists():
        print(f"[musubi] Hermes DB not found at {HERMES_DB}", file=sys.stderr)
        return ""

    queries = [
        # Pattern 1: messages table with session_id + created_at
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        # Pattern 2: messages table with session_id + id (no timestamp)
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
    ]

    conn = sqlite3.connect(str(HERMES_DB))
    rows = None
    try:
        for query in queries:
            try:
                cursor = conn.execute(query, (session_id,))
                rows = cursor.fetchall()
                break
            except sqlite3.OperationalError:
                continue
    finally:
        conn.close()

    if rows is None:
        print(
            f"[musubi] Could not query transcript for session {session_id}. "
            "Check the DB schema and update the query in handler.py.",
            file=sys.stderr,
        )
        return ""

    if not rows:
        return ""

    lines = [f"# Session Transcript\n**Date:** {date.today().isoformat()}\n"]
    for role, content in rows:
        label = "User" if role == "user" else "Agent"
        lines.append(f"**{label}:** {content}")

    return "\n\n".join(lines)


def _run_processing_agent(
    musubi_id: str,
    transcript: str,
    user_file: Path,
    memories_file: Path,
) -> None:
    """
    Spawn a headless Claude Code session to run the Musubi processing agent.

    Uses `claude -p` — the same pattern as the Hermes agent infrastructure.
    The agent receives all five required inputs inline in the prompt and writes
    the two output files directly using its built-in Write tool.
    """
    claude_bin = str(CLAUDE) if CLAUDE.exists() else shutil.which("claude")
    if not claude_bin:
        print("[musubi] claude CLI not found — cannot run processing agent.", file=sys.stderr)
        return

    persona = (MUSUBI_DIR / "persona.md").read_text()
    processing_skill = (MUSUBI_DIR / "skills" / "processing.md").read_text()
    user_state = user_file.read_text() if user_file.exists() else ""
    memories = memories_file.read_text() if memories_file.exists() else ""

    user_path = str(user_file)
    memories_path = str(memories_file)

    prompt = f"""You are the Musubi processing agent. Read all context below and follow your instructions exactly.

---

# PERSONA

{persona}

---

# PROCESSING INSTRUCTIONS

{processing_skill}

---

# CURRENT USER STATE
File: {user_path}

{user_state}

---

# CURRENT MEMORIES
File: {memories_path}

{memories}

---

# SESSION TRANSCRIPT

{transcript}

---

Write the updated files now using your Write tool.
You must write both files with their full absolute paths:
- {user_path}
- {memories_path}
"""

    result = subprocess.run(
        [
            claude_bin,
            "-p", prompt,
            "--allowedTools", "Write,Read",
            "--allow-dangerously-skip-permissions",
            "--add-dir", str(MUSUBI_DIR),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[musubi] Processing agent exited with code {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"[musubi] stderr: {result.stderr[:500]}", file=sys.stderr)
        return

    # Verify both files were written
    missing = [p for p in (user_file, memories_file) if not p.exists()]
    if missing:
        print(f"[musubi] Warning: processing agent did not write: {missing}", file=sys.stderr)
