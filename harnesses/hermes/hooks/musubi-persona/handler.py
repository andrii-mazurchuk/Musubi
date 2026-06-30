"""
Musubi — /persona command hook for Hermes.

Handles the /persona slash command for switching and inspecting personas.

Usage (sent as a message or slash command via any Hermes platform):
    /persona switch <name>   — activate a named persona for the next session
    /persona list            — list all available personas
    /persona current         — show which persona is currently active

On switch:
  - Writes active_persona file
  - Writes persona.md → ~/.hermes/SOUL.md immediately (takes effect next session)
  - Writes pending_switch_notice so the agent introduces itself in character

Context keys expected from Hermes:
    args  — everything after "/persona" (e.g. "switch steward")
"""

import sys
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
MUSUBI_DIR = HERMES_DIR / "musubi"
ACTIVE_VOICE_FILE = MUSUBI_DIR / "active_voice"


def _available_personas() -> list[str]:
    personas_dir = MUSUBI_DIR / "personas"
    if not personas_dir.exists():
        return []
    return sorted(
        d.name
        for d in personas_dir.iterdir()
        if d.is_dir() and (d / "persona.md").exists()
    )


def _current_persona() -> str | None:
    active_file = MUSUBI_DIR / "active_persona"
    if active_file.exists():
        name = active_file.read_text().strip()
        return name if name else None
    return None


def _apply_voice(persona_name: str) -> str:
    """Read voice.yaml for persona and write active_voice file. Returns a status note."""
    voice_file = MUSUBI_DIR / "personas" / persona_name / "voice.yaml"
    if not voice_file.exists():
        # No voice config — clear any active voice override so we fall back to config default
        ACTIVE_VOICE_FILE.unlink(missing_ok=True)
        return ""

    try:
        import yaml
    except ImportError:
        return "(voice.yaml found but PyYAML not available — voice not applied)"

    try:
        cfg = yaml.safe_load(voice_file.read_text()) or {}
    except Exception as e:
        return f"(voice.yaml parse error: {e})"

    provider = cfg.get("provider", "").strip()
    voice_id = cfg.get("voice_id", "").strip()

    if voice_id:
        ACTIVE_VOICE_FILE.write_text(voice_id)
        return f"Voice: {provider or 'default'} / {voice_id[:8]}…"
    else:
        # Command-type providers have no voice_id — provider identity is fixed in config
        ACTIVE_VOICE_FILE.unlink(missing_ok=True)
        return f"Voice: {provider}" if provider else ""


async def handle(event_type: str, context: dict) -> None:
    args_str = context.get("args", "").strip()
    args = args_str.split()
    subcommand = args[0].lower() if args else "current"

    if subcommand == "switch":
        if len(args) < 2:
            _write_reply(context, "Usage: /persona switch <name>")
            return

        name = args[1].lower()
        persona_file = MUSUBI_DIR / "personas" / name / "persona.md"

        if not persona_file.exists():
            available = _available_personas()
            if available:
                _write_reply(
                    context,
                    f"Persona '{name}' not found.\nAvailable: {', '.join(available)}"
                )
            else:
                _write_reply(
                    context,
                    f"Persona '{name}' not found. No personas defined yet.\n"
                    f"Add one at: {MUSUBI_DIR}/personas/<name>/persona.md"
                )
            return

        # Write active_persona
        (MUSUBI_DIR / "active_persona").write_text(name)

        # Write persona.md → SOUL.md immediately
        # persona.md is a full SOUL.md replacement — personality + operational layers both live in it
        soul_path = HERMES_DIR / "SOUL.md"
        soul_path.write_text(persona_file.read_text())

        # Write switch notice — session:start injects this so the agent introduces itself
        (MUSUBI_DIR / "pending_switch_notice").write_text(
            f"You have just been activated as the '{name}' persona. "
            f"Introduce yourself briefly in character. Do not explain that a switch occurred — "
            f"simply begin as this persona from the first word."
        )

        # Apply voice settings if persona has a voice.yaml
        voice_note = _apply_voice(name)

        reply = f"Switched to persona: {name}\nSOUL.md updated. Takes effect next session."
        if voice_note:
            reply += f"\n{voice_note}"
        _write_reply(context, reply)

    elif subcommand == "list":
        available = _available_personas()
        current = _current_persona()
        if not available:
            _write_reply(
                context,
                f"No personas defined yet.\nAdd one at: {MUSUBI_DIR}/personas/<name>/persona.md"
            )
            return
        lines = ["Available personas:"]
        for p in available:
            marker = " ← active" if p == current else ""
            lines.append(f"  {p}{marker}")
        _write_reply(context, "\n".join(lines))

    elif subcommand == "current":
        current = _current_persona()
        if current:
            _write_reply(context, f"Active persona: {current}")
        else:
            _write_reply(context, "No persona active — using default persona.md")

    else:
        _write_reply(
            context,
            f"Unknown subcommand '{subcommand}'.\n"
            "Usage: /persona switch <name> | /persona list | /persona current"
        )


def _write_reply(context: dict, message: str) -> None:
    reply_fn = context.get("reply")
    if callable(reply_fn):
        try:
            import asyncio
            if asyncio.iscoroutinefunction(reply_fn):
                asyncio.ensure_future(reply_fn(message))
            else:
                reply_fn(message)
            return
        except Exception as e:
            print(f"[musubi] reply callable failed: {e}", file=sys.stderr)

    send_fn = context.get("send")
    if callable(send_fn):
        try:
            send_fn(message)
            return
        except Exception as e:
            print(f"[musubi] send callable failed: {e}", file=sys.stderr)

    print(f"[musubi/persona] {message}", file=sys.stderr)
