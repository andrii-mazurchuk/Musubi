"""
Musubi — session:start hook for Hermes.

Assembles persona + user relationship state + memory into a single context
block and writes it to Hermes's memory injection directory, where it gets
automatically loaded into the agent's system prompt for this session.

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


async def handle(event_type: str, context: dict) -> None:
    platform = context.get("platform", "unknown")
    user_id = context.get("user_id", "default")
    musubi_id = f"{platform}_{user_id}"

    user_file = MUSUBI_DIR / "data" / "users" / f"{musubi_id}.md"
    memories_file = MUSUBI_DIR / "data" / "memories" / f"{musubi_id}.md"

    # Initialize state files for first-time users
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

    # Assemble context block from all three Musubi files
    try:
        persona = (MUSUBI_DIR / "persona.md").read_text()
        user_state = user_file.read_text()
        memories = memories_file.read_text()
    except FileNotFoundError as e:
        print(f"[musubi] Missing file: {e}", file=sys.stderr)
        return

    context_block = f"""# Musubi: Persistent Persona Context

{persona}

---

{user_state}

---

{memories}
"""

    # Write to Hermes memory injection directory
    INJECT_DIR.mkdir(parents=True, exist_ok=True)
    (INJECT_DIR / f"musubi_{musubi_id}.md").write_text(context_block)
