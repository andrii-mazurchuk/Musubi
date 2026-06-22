# Trigger Contract

This document defines the interface between your agent harness and the Musubi
processing agent. The implementation differs by harness; the contract is always the same.

---

## When to trigger

Fire the processing agent after every session — after the user's last message and the
talking agent's last response, before the session context is discarded.

Do not trigger mid-session. The processing agent needs the full transcript to do accurate
appraisal. Mid-session snapshots produce noisy, inconsistent relationship updates.

---

## What the trigger must supply

The processing agent needs five things, in any order:

| Input | Source | Notes |
|---|---|---|
| Session transcript | Saved by harness at session end | See Transcript Format below |
| `persona.md` | Project root | Always the same file |
| `skills/processing.md` | Project root | Always the same file |
| `data/users/{id}.md` | Runtime data directory | Current state, before this session's updates |
| `data/memories/{id}.md` | Runtime data directory | Current state, before this session's updates |

If `data/users/{id}.md` or `data/memories/{id}.md` don't exist yet (first session with
this user), copy from `templates/user.md` and `templates/memories.md` respectively.
The `{id}` must match what you used when loading context into the talking agent.

---

## What the processing agent produces

Two file writes:
- `data/users/{id}.md` — overwritten with updated relationship state and facts
- `data/memories/{id}.md` — overwritten with new session entry prepended

Nothing else. The processing agent produces no output for the user.

**The processing agent must have write access to the `data/` directory.**

In Claude Code harness: built-in Write/Edit tools provide this automatically.
In direct API calls: you must supply a `write_file` tool. See `api.py`.

---

## Transcript format

Save transcripts as plain markdown. The processing agent can read any readable format,
but consistency matters for its appraisal accuracy. Use this structure:

```markdown
# Session Transcript

**User ID:** {id}
**Date:** {YYYY-MM-DD}
**Session number:** {N}

---

**User:** {first message}

**Agent:** {first response}

**User:** {second message}

**Agent:** {second response}

...
```

Keep the full transcript — every turn, both sides, in order. Do not summarize or truncate
before passing to the processing agent. The appraisal depends on reading the actual exchange.

---

## Error handling

If the processing agent fails or produces malformed output:
- Log the failure
- Do not write partial updates to either data file
- Keep the previous versions of both files intact
- The next session will load the last-good state — one failed update is not catastrophic

Do not retry automatically in a tight loop. If the processing agent fails consistently,
inspect the transcript and data files for the source of the problem.

---

## Implementation notes for specific harnesses

See the reference implementations in this directory:

- `claude-code.sh` — for Claude Code headless sessions. The model writes files directly
  using its built-in Write tool. Simplest path if your harness is Claude Code.

- `api.py` — for direct Anthropic API calls. Supplies a `write_file` tool so the model
  can write the two output files. Use this if your harness calls the API directly.

If your harness is neither, use this contract as the spec and implement accordingly.
The invariants: processing agent receives all five inputs, has write access to `data/`,
and fires once per session at session end.
