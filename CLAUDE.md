# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## What This Project Is

Musubi is a **context-layer architecture** for giving a Claude-based agent a persistent persona,
per-user memory, and a slow-moving relationship state — implemented entirely through files and
skills, with no custom infrastructure required. It works with any agent harness that supports
context injection and background sessions.

The design research lives in `musubi_research_dossier.md`. Read §1 and §8 before making
any structural changes to the architecture.

---

## The Two-Agent Model

Every Musubi deployment runs two agents with strictly separated jobs:

**Talking agent** — the foreground agent the user converses with. It reads three files at
session start and talks. It writes nothing during the session.

**Processing agent** — a headless session launched after the conversation ends. It reads
the full transcript plus current state files, evaluates what the session meant for the
relationship, and writes the updated state files for next time.

Never merge these two jobs. The talking agent's ability to stay present depends on not
doing state management mid-conversation. The processing agent's accuracy depends on having
the full session to evaluate, not a stream of mid-conversation snapshots.

---

## File Roles

| File | Loaded by | Written by |
|---|---|---|
| `persona.md` | Talking agent + Processing agent | You (design-time); agent (rare self-edits) |
| `skills/talking.md` | Talking agent | You |
| `skills/processing.md` | Processing agent | You |
| `data/users/{id}.md` | Both agents | Processing agent only |
| `data/memories/{id}.md` | Both agents | Processing agent only |

`data/` is gitignored. It is runtime state, not part of the project.

---

## Integrating Into Your Harness

### Hermes (supported)

Run the install script from the repo root:

```bash
./harnesses/hermes/install.sh
hermes gateway restart
```

This symlinks the two Musubi hooks into `~/.hermes/hooks/` and creates
`~/.hermes/musubi/` as the data directory. Full details in `harnesses/hermes/README.md`.

The Hermes integration uses the native hook system (`session:start` / `session:end`),
reads transcripts from Hermes's SQLite store, and injects context via Hermes's memory
injection directory. No manual wiring required.

### Other harnesses

Read `trigger/contract.md` for the harness-agnostic interface specification, then use
the Hermes implementation as a complete reference. The invariants for any harness:

**Session start** — inject into the talking agent's context:
1. `persona.md`
2. `skills/talking.md`
3. `data/users/{id}.md` — create from `templates/user.md` if first session
4. `data/memories/{id}.md` — create from `templates/memories.md` if first session

**Session end** — launch a background agent with:
1. Full transcript (all turns, both sides)
2. `persona.md`
3. `skills/processing.md`
4. `data/users/{id}.md` (current state, before update)
5. `data/memories/{id}.md` (current state, before update)

The processing agent must have write access to `data/`. It writes both files and
produces no other output. See `trigger/contract.md` for error handling guidance.

The `{id}` is however your harness identifies the current user — it just needs to be
consistent across sessions for the same person.

---

## Customizing the Agent

**The only file you need to author is `persona.md`.** Everything else — the skills,
templates, and data files — is designed to work with any persona that follows the schema.

Read `persona.md` carefully before filling it in. The schema matters:
- Beliefs must be internally consistent (a belief implies things about the others)
- Interests should emerge from beliefs, not be authored independently
- Values/Standards are the appraisal targets — be specific, not generic
- The Hard Floor section is not subject to the policy or relationship layers

The skill files (`skills/talking.md` and `skills/processing.md`) reference the
persona schema directly. If you change the schema, update the skills to match.

---

## Size Caps

Both data files have hard size caps enforced by the processing agent:

- `data/users/{id}.md` — Facts section: ~300 words. Significant Moments: 5 entries max.
  Processing Notes: ~100 words.
- `data/memories/{id}.md` — 10 session entries max.

When a file is at cap, the processing agent drops the oldest/least-load-bearing content
to make room. The caps are intentional — they force the agent to retain what matters.
Tune them by reading the actual files after real sessions and adjusting `skills/processing.md`.

---

## What Not to Change

- **Do not add per-turn state writes to the talking agent.** The two-agent model exists
  precisely to avoid this. Mid-conversation state management is expensive and degrades
  the conversational quality.
- **Do not merge `data/users/{id}.md` relationship state into the facts section.** They
  are different things. Facts are static; relationship state is dynamic. Conflating them
  produces unreliable appraisal.
- **Do not remove the Hard Floor section from `persona.md`.** Persona assignment measurably
  increases toxicity in LLM outputs (Deshpande et al. 2023). The floor must be explicit
  and unconditional.
