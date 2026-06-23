"""
Musubi — session:start hook for Hermes.

Writes Musubi's per-persona user state directly into Hermes's native memory files:
  - data/users/{persona}/{id}.md  →  ~/.hermes/memories/USER.md  (full replace)
  - data/memories/{persona}/{id}.md  →  MEMORY.md Musubi section  (delimited replace)

SOUL.md is written by the /persona switch command, not here.
This hook only handles per-session user context and episodic memories.

Context keys expected from Hermes:
    platform  — string identifier of the originating platform
    user_id   — platform-native user identifier
"""

import re
import sys
import time
from datetime import date
from pathlib import Path

LOCK_STALE_SECONDS = 300  # locks older than 5 minutes are considered stale

HERMES_DIR = Path.home() / ".hermes"
MUSUBI_DIR = HERMES_DIR / "musubi"
MEMORIES_DIR = HERMES_DIR / "memories"

# Delimiters for the Musubi section inside MEMORY.md
_MUSUBI_START = "<!-- musubi:start -->"
_MUSUBI_END = "<!-- musubi:end -->"


def _active_persona() -> tuple[str | None, Path]:
    active_file = MUSUBI_DIR / "active_persona"
    if active_file.exists():
        name = active_file.read_text().strip()
        if name:
            persona_file = MUSUBI_DIR / "personas" / name / "persona.md"
            if persona_file.exists():
                return name, persona_file
            print(
                f"[musubi] Persona '{name}' not found — falling back to default.",
                file=sys.stderr,
            )
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


def _write_locked(path: Path, content: str) -> None:
    """Write a file respecting Hermes's .lock convention."""
    lock = path.with_suffix(path.suffix + ".lock")
    if lock.exists():
        age = time.time() - lock.stat().st_mtime
        if age < LOCK_STALE_SECONDS:
            print(f"[musubi] Lock exists for {path.name} ({age:.0f}s old) — skipping write.", file=sys.stderr)
            return
        print(f"[musubi] Removing stale lock for {path.name} ({age:.0f}s old).", file=sys.stderr)
        lock.unlink(missing_ok=True)
    lock.touch()
    try:
        path.write_text(content)
    finally:
        lock.unlink(missing_ok=True)


def _update_memory_section(memories_content: str) -> None:
    """
    Insert or replace the Musubi section in MEMORY.md.
    Operational content outside the delimiters is preserved.
    """
    memory_path = MEMORIES_DIR / "MEMORY.md"
    current = memory_path.read_text() if memory_path.exists() else ""

    block = f"{_MUSUBI_START}\n{memories_content.strip()}\n{_MUSUBI_END}"

    if _MUSUBI_START in current:
        updated = re.sub(
            f"{re.escape(_MUSUBI_START)}.*?{re.escape(_MUSUBI_END)}",
            block,
            current,
            flags=re.DOTALL,
        )
    else:
        updated = current.rstrip() + f"\n\n{block}\n"

    _write_locked(memory_path, updated)


async def handle(event_type: str, context: dict) -> None:
    platform = context.get("platform", "unknown")
    user_id = context.get("user_id", "default")
    musubi_id = f"{platform}_{user_id}"

    persona_name, _ = _active_persona()
    user_file, memories_file = _data_paths(persona_name, musubi_id)

    # Initialize state files for first-time users / first time with this persona
    if not user_file.exists():
        user_file.parent.mkdir(parents=True, exist_ok=True)
        template = (MUSUBI_DIR / "templates" / "user.md").read_text()
        user_file.write_text(
            template
            .replace("{id}", musubi_id)
            .replace("{YYYY-MM-DD}", date.today().isoformat())
        )

    if not memories_file.exists():
        memories_file.parent.mkdir(parents=True, exist_ok=True)
        template = (MUSUBI_DIR / "templates" / "memories.md").read_text()
        memories_file.write_text(template.replace("{id}", musubi_id))

    # Write user state → USER.md (full replace — this is the active user for this session)
    user_md = MEMORIES_DIR / "USER.md"
    user_content = user_file.read_text()

    # Append switch notice if pending
    notice_file = MUSUBI_DIR / "pending_switch_notice"
    if notice_file.exists():
        notice = notice_file.read_text().strip()
        user_content = user_content.rstrip() + f"\n\n**Note:** {notice}\n"
        notice_file.unlink()

    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    _write_locked(user_md, user_content)

    # Write episodic memories → MEMORY.md Musubi section
    _update_memory_section(memories_file.read_text())
