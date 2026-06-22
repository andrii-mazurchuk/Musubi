#!/usr/bin/env bash
# harnesses/hermes/switch-persona.sh
#
# CLI fallback for switching Musubi personas without a Hermes command.
# Use this if /persona switch is not available in your Hermes version,
# or when you want to switch from the terminal.
#
# Usage:
#   ./harnesses/hermes/switch-persona.sh <name>
#   ./harnesses/hermes/switch-persona.sh              # show current + list

set -euo pipefail

MUSUBI_DIR="${HOME}/.hermes/musubi"
PERSONAS_DIR="$MUSUBI_DIR/personas"
ACTIVE_FILE="$MUSUBI_DIR/active_persona"

current() {
  if [[ -f "$ACTIVE_FILE" ]]; then
    cat "$ACTIVE_FILE"
  else
    echo "(none — using default persona.md)"
  fi
}

list_personas() {
  if [[ ! -d "$PERSONAS_DIR" ]]; then
    echo "No personas directory found at $PERSONAS_DIR"
    return
  fi
  local current_name
  current_name=$(current)
  echo "Available personas:"
  for dir in "$PERSONAS_DIR"/*/; do
    [[ -f "$dir/persona.md" ]] || continue
    name="$(basename "$dir")"
    if [[ "$name" == "$current_name" ]]; then
      echo "  $name  ← active"
    else
      echo "  $name"
    fi
  done
}

if [[ -z "${1:-}" ]]; then
  echo "Current persona: $(current)"
  echo ""
  list_personas
  echo ""
  echo "Usage: $0 <name>"
  exit 0
fi

NAME="$1"
PERSONA_FILE="$PERSONAS_DIR/$NAME/persona.md"

if [[ ! -f "$PERSONA_FILE" ]]; then
  echo "Error: persona '$NAME' not found at $PERSONA_FILE" >&2
  echo ""
  list_personas
  exit 1
fi

echo "$NAME" > "$ACTIVE_FILE"
echo "Switched to persona: $NAME"
echo "Takes effect on the next session."
