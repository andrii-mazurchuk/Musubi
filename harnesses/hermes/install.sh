#!/usr/bin/env bash
# harnesses/hermes/install.sh
#
# Installs Musubi into a running Hermes setup.
#
# What it does:
#   1. Creates ~/.hermes/musubi/ as the Musubi data directory
#   2. Symlinks persona.md, skills/, and templates/ into that directory
#      so Hermes reads from the repo — pull updates, they take effect immediately
#   3. Symlinks the two Musubi hooks into ~/.hermes/hooks/
#
# Usage:
#   ./harnesses/hermes/install.sh
#
# Options:
#   HERMES_DIR  Override Hermes home (default: ~/.hermes)
#
# After install:
#   1. Fill in persona.md with your agent's identity
#   2. Restart the Hermes gateway: hermes gateway restart

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERMES_DIR="${HERMES_DIR:-$HOME/.hermes}"
MUSUBI_INSTALL="$HERMES_DIR/musubi"
HOOKS_DIR="$HERMES_DIR/hooks"

# --- Validate Hermes installation ---
if [[ ! -d "$HERMES_DIR" ]]; then
  echo "Error: Hermes directory not found at $HERMES_DIR" >&2
  echo "Set HERMES_DIR if your Hermes is installed elsewhere, e.g.:" >&2
  echo "  HERMES_DIR=/path/to/hermes ./harnesses/hermes/install.sh" >&2
  exit 1
fi

echo "Installing Musubi into Hermes at: $HERMES_DIR"
echo "Musubi repo: $REPO_DIR"
echo ""

# --- Create Musubi data directory (not symlinked — this holds live user data) ---
mkdir -p "$MUSUBI_INSTALL/data/users"
mkdir -p "$MUSUBI_INSTALL/data/memories"
echo "  Created: $MUSUBI_INSTALL/data/"

# --- Symlink repo files into the Musubi install directory ---
for target in persona.md skills templates; do
  link="$MUSUBI_INSTALL/$target"
  src="$REPO_DIR/$target"

  if [[ ! -e "$src" ]]; then
    echo "  Warning: $src not found — skipping" >&2
    continue
  fi

  if [[ -L "$link" ]]; then
    rm "$link"
  elif [[ -e "$link" ]]; then
    echo "  Warning: $link already exists and is not a symlink — skipping" >&2
    continue
  fi

  ln -s "$src" "$link"
  echo "  Linked: $link"
done

# --- Install hooks ---
mkdir -p "$HOOKS_DIR"

for hook in musubi-session-start musubi-session-end; do
  src="$REPO_DIR/harnesses/hermes/hooks/$hook"
  link="$HOOKS_DIR/$hook"

  if [[ -L "$link" ]]; then
    rm "$link"
  elif [[ -d "$link" ]]; then
    echo "  Warning: $link exists and is not a symlink — skipping" >&2
    continue
  fi

  ln -s "$src" "$link"
  echo "  Linked hook: $hook"
done

# --- Dependency check ---
echo ""
echo "Checking dependencies..."
CLAUDE_BIN="${HOME}/.local/bin/claude"
if [[ ! -x "$CLAUDE_BIN" ]]; then
  CLAUDE_BIN=$(command -v claude 2>/dev/null || true)
fi
if [[ -z "$CLAUDE_BIN" ]]; then
  echo "  Warning: claude CLI not found — install Claude Code before using Musubi"
else
  echo "  claude: $CLAUDE_BIN"
fi

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Edit $MUSUBI_INSTALL/persona.md with your agent's identity"
echo "  2. Restart the gateway: hermes gateway restart"
echo "  3. Send a message to your agent and check $MUSUBI_INSTALL/data/users/ after the session"
