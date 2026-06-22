# Musubi for Hermes

This directory wires Musubi into the [Hermes](https://github.com/NousResearch/hermes-agent)
agent harness using Hermes's native hook system.

---

## Security notice

The `session:end` hook spawns a headless Claude Code session using the
`--allow-dangerously-skip-permissions` flag. **Understand what this means before installing.**

This flag disables all permission prompts for that Claude session. The processing agent
runs unattended after every conversation, with no human in the loop, and can write to
any file path it is instructed to reach. There is no sandbox.

The risk is constrained in practice by two things: the prompt only instructs the agent to
write two specific files inside `~/.hermes/musubi/data/`, and the agent is only given
`Write` and `Read` tools. But these are soft constraints — they rely on the model following
instructions, not on OS-level enforcement. A maliciously crafted conversation transcript
could theoretically influence what the processing agent writes.

**Do not install Musubi on a machine where:**
- The `~/.hermes/` directory contains files you cannot afford to have modified
- Conversations may include untrusted content from third parties at scale
- You are not comfortable with headless agent writes running after every session

If you need harder isolation, the correct fix is to replace `--allow-dangerously-skip-permissions`
with an explicit allowlist of permitted write paths, if and when the `claude` CLI supports
path-scoped permissions. Until then, treat this as a trusted-environment-only tool.

---

## How it works

Hermes fires lifecycle events (`session:start`, `session:end`) that hooks in
`~/.hermes/hooks/` can subscribe to. Musubi uses two hooks:

**`musubi-session-start`** — runs when a session opens
- Reads the current user's `persona.md`, `user_{id}.md`, and `memories_{id}.md`
- Writes them as a single combined block to `~/.hermes/memories/musubi_{id}.md`
- Hermes's existing memory injection picks this up and loads it into the system prompt
- Initializes state files from templates if this user has never had a session before

**`musubi-session-end`** — runs when a session closes
- Removes the injected context file
- Queries `~/.hermes/hermes_state.db` (Hermes's SQLite store) for the full transcript
- Spawns a headless `claude -p` session (same pattern as Hermes's own agent infrastructure)
- Processing agent writes updated `user_{id}.md` and `memories_{id}.md` via its Write tool

The user ID Musubi uses is `{platform}_{user_id}` — e.g., `telegram_943887846`.
This keeps per-user state separate across platforms automatically.

---

## Prerequisites

- Hermes installed and gateway running
- `claude` CLI installed and authenticated (same binary Hermes uses — if your gateway runs, this is already satisfied)

---

## Install

From the repository root:

```bash
./harnesses/hermes/install.sh
```

This will:
1. Create `~/.hermes/musubi/` as the Musubi data directory
2. Symlink `persona.md`, `skills/`, and `templates/` from the repo into that directory
3. Symlink the two hooks into `~/.hermes/hooks/`

Then restart the gateway:

```bash
hermes gateway restart
```

To verify the hooks are loaded:

```bash
hermes gateway status
# or check the gateway log:
tail -f ~/.hermes/logs/gateway.log | grep musubi
```

---

## After install

**The only file you need to edit is `persona.md`** in the repo root. Fill in your
agent's identity — beliefs, interests, values, hard floor. See the schema in the file.

The first time a user sends a message, Musubi will:
1. Create `~/.hermes/musubi/data/users/{platform}_{user_id}.md` from the template
2. Create `~/.hermes/musubi/data/memories/{platform}_{user_id}.md` from the template
3. Inject defaults (trust: 0.5, warmth: 0.5, friction: 0.0) into the session

After the session ends, the processing agent will update both files with the first
real relationship state based on what happened in the conversation.

---

## File locations after install

```
~/.hermes/musubi/
├── persona.md          → symlink to repo/persona.md
├── skills/             → symlink to repo/skills/
├── templates/          → symlink to repo/templates/
└── data/
    ├── users/          live data — one file per user
    └── memories/       live data — one file per user

~/.hermes/hooks/
├── musubi-session-start/   → symlink to repo/harnesses/hermes/hooks/musubi-session-start/
└── musubi-session-end/     → symlink to repo/harnesses/hermes/hooks/musubi-session-end/

~/.hermes/memories/
└── musubi_{id}.md      written at session start, deleted at session end
```

---

## DB schema note

The `session:end` hook queries Hermes's SQLite DB for the transcript. The query
targets the most common Hermes schema:

```sql
SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC
```

If your Hermes version uses a different schema, edit the `queries` list in
`hooks/musubi-session-end/handler.py` → `_get_transcript()`.

---

## Uninstall

```bash
rm ~/.hermes/hooks/musubi-session-start
rm ~/.hermes/hooks/musubi-session-end
rm -rf ~/.hermes/musubi
hermes gateway restart
```

User data in `~/.hermes/musubi/data/` is removed with the above. Back it up first
if you want to keep relationship history.
