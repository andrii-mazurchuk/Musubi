"""
Musubi — session:end hook for Hermes.

1. Removes the injected Musubi context file from Hermes's memory directory.
2. Pulls the full session transcript from Hermes's SQLite store.
3. Spawns a headless Claude Code session (via the `claude` CLI) to run the
   Musubi processing agent, which writes updated relationship state + memory files
   using its built-in Write tool.

Multi-persona: reads active_persona file so the processing agent writes to the
correct persona-scoped data paths.

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
CLAUDE = Path.home() / ".local" / "bin" / "claude"


def _active_persona() -> tuple[str | None, Path]:
    active_file = MUSUBI_DIR / "active_persona"
    if active_file.exists():
        name = active_file.read_text().strip()
        if name:
            persona_file = MUSUBI_DIR / "personas" / name / "persona.md"
            if persona_file.exists():
                return name, persona_file
    return None, MUSUBI_DIR / "persona.md"


def _data_paths(persona_name: str | None, musubi_id: str) -> tuple[Path, Path]:
    if persona_name:
        base = MUSUBI_DIR / "data"
        return (
            base / "users" / persona_name / f"{musubi_id}.md",
            base / "memories" / persona_name / f"{musubi_id}.md",
        )
    return (
        MUSUBI_DIR / "data" / "users" / f"{musubi_id}.md",
        MUSUBI_DIR / "data" / "memories" / f"{musubi_id}.md",
    )


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
        return

    persona_name, persona_file = _active_persona()
    user_file, memories_file = _data_paths(persona_name, musubi_id)

    _run_processing_agent(persona_file, transcript, user_file, memories_file)


def _get_transcript(session_id: str) -> str:
    import sqlite3

    if not HERMES_DB.exists():
        print(f"[musubi] Hermes DB not found at {HERMES_DB}", file=sys.stderr)
        return ""

    queries = [
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
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
    persona_file: Path,
    transcript: str,
    user_file: Path,
    memories_file: Path,
) -> None:
    claude_bin = str(CLAUDE) if CLAUDE.exists() else shutil.which("claude")
    if not claude_bin:
        print("[musubi] claude CLI not found — cannot run processing agent.", file=sys.stderr)
        return

    persona = persona_file.read_text() if persona_file.exists() else ""
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

    missing = [p for p in (user_file, memories_file) if not p.exists()]
    if missing:
        print(f"[musubi] Warning: processing agent did not write: {missing}", file=sys.stderr)
