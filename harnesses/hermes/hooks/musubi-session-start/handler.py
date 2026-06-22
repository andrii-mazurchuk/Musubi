"""
Musubi — session:start hook for Hermes.

Assembles persona + user relationship state + memory into a single context
block and writes it to Hermes's memory injection directory, where it gets
automatically loaded into the agent's system prompt for this session.

Multi-persona: reads active_persona file to determine which persona to load.
Data paths are scoped per persona so each persona maintains isolated user state.

Context keys expected from Hermes:
    platform  — string identifier of the originating platform (telegram, discord, etc.)
    user_id   — platform-native user identifier
"""

import sys
from datetime import date
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
MUSUBI_DIR = HERMES_DIR / "musubi"
INJECT_DIR = HERMES_DIR / "memories"


def _active_persona() -> tuple[str | None, Path]:
    """
    Return (persona_name, persona_file).
    Falls back to root persona.md if no active persona is set or the named
    persona file is missing.
    """
    active_file = MUSUBI_DIR / "active_persona"
    if active_file.exists():
        name = active_file.read_text().strip()
        if name:
            persona_file = MUSUBI_DIR / "personas" / name / "persona.md"
            if persona_file.exists():
                return name, persona_file
            print(
                f"[musubi] Persona '{name}' set in active_persona but "
                f"personas/{name}/persona.md not found — falling back to default.",
                file=sys.stderr,
            )
    # Fallback: root persona.md (default / no persona selected)
    return None, MUSUBI_DIR / "persona.md"


def _data_paths(persona_name: str | None, musubi_id: str) -> tuple[Path, Path]:
    """Return (user_file, memories_file) scoped to the active persona."""
    if persona_name:
        base = MUSUBI_DIR / "data"
        return (
            base / "users" / persona_name / f"{musubi_id}.md",
            base / "memories" / persona_name / f"{musubi_id}.md",
        )
    # Legacy / default paths (no persona selected)
    return (
        MUSUBI_DIR / "data" / "users" / f"{musubi_id}.md",
        MUSUBI_DIR / "data" / "memories" / f"{musubi_id}.md",
    )


async def handle(event_type: str, context: dict) -> None:
    platform = context.get("platform", "unknown")
    user_id = context.get("user_id", "default")
    musubi_id = f"{platform}_{user_id}"

    persona_name, persona_file = _active_persona()
    user_file, memories_file = _data_paths(persona_name, musubi_id)

    # Initialize state files for first-time users (or first time with this persona)
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

    # Assemble context block
    try:
        persona = persona_file.read_text()
        user_state = user_file.read_text()
        memories = memories_file.read_text()
    except FileNotFoundError as e:
        print(f"[musubi] Missing file: {e}", file=sys.stderr)
        return

    # Check for a pending persona switch notice (written by /persona switch)
    switch_notice = ""
    notice_file = MUSUBI_DIR / "pending_switch_notice"
    if notice_file.exists():
        switch_notice = f"\n\n---\n\n**SYSTEM NOTE:** {notice_file.read_text().strip()}"
        notice_file.unlink()

    context_block = f"""# Musubi: Persistent Persona Context

{persona}

---

{user_state}

---

{memories}{switch_notice}
"""

    # Write to Hermes memory injection directory
    INJECT_DIR.mkdir(parents=True, exist_ok=True)
    (INJECT_DIR / f"musubi_{musubi_id}.md").write_text(context_block)
