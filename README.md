# Musubi (結び)

A context-layer architecture for persistent AI agent personas with genuine relationship modeling.

Musubi gives any Claude-based agent harness five things it doesn't have by default:

- A **stable identity** — beliefs, interests, values that persist across every conversation
- **Per-user memory** — what this agent knows about this specific person, accumulated over time
- **Relationship state** — trust, warmth, and friction as slow-moving values that shift based on what actually happens between them
- **In-session behavioral policy** — how the agent's current relationship state actually changes what it says and how
- **Background processing** — a separate agent pass after each session that does the heavy work of updating state, so the conversational agent stays focused

The name comes from the Shinto concept of *musubi* (結び): the binding force behind how relationships between people come into being.

---

## Architecture in brief

Musubi uses two agents with strictly separated jobs:

**Talking agent** — the foreground agent the user converses with. Loads persona + user context at session start. Talks. Writes nothing.

**Processing agent** — a headless session launched after the conversation ends. Reads the full transcript, evaluates what shifted in the relationship, and rewrites the state files for next time.

The shared state lives in three files per user:

| File | What it holds | Who writes it |
|---|---|---|
| `persona.md` | Agent identity — beliefs, values, hard floor | You (design-time), agent (slow self-edits) |
| `data/users/{id}.md` | Facts about this person + current relationship state | Processing agent |
| `data/memories/{id}.md` | Compressed episodic history with this person | Processing agent |

---

## File structure

```
musubi/
├── persona.md                  # The agent's core identity — customize this
├── skills/
│   ├── talking.md              # Loaded into the conversational agent at session start
│   └── processing.md           # Loaded into the background processing agent at session end
├── templates/
│   ├── user.md                 # Template for data/users/{id}.md
│   └── memories.md             # Template for data/memories/{id}.md
├── data/                       # Runtime state — gitignored
│   ├── users/
│   └── memories/
├── trigger/
│   └── contract.md             # Harness-agnostic interface specification
└── harnesses/
    └── hermes/                 # Full wiring for the Hermes agent harness
```

---

## Supported harnesses

### Hermes

Full integration using Hermes's native hook system. One install script wires everything in.

```bash
./harnesses/hermes/install.sh
hermes gateway restart
```

See [`harnesses/hermes/README.md`](harnesses/hermes/README.md) for the full walkthrough.

**How it works:**
- `session:start` hook assembles persona + user context and injects it into the system prompt via Hermes's memory directory
- `session:end` hook pulls the transcript from Hermes's SQLite store, runs the Musubi processing agent via the Anthropic API, and writes updated state files
- User ID is derived automatically as `{platform}_{user_id}` — separate state per platform with no configuration

### Other harnesses

See `trigger/contract.md` for the harness-agnostic interface specification — what any implementation must supply to the processing agent and what it will receive back. The Hermes implementation (`harnesses/hermes/`) is a complete reference for how to implement this for another harness.

---

## Customization

Everything lives in `persona.md`. That's the one file you author for your specific agent. The skills and templates are designed to work with any persona that follows the schema defined in `persona.md`.

See `templates/user.md` and `templates/memories.md` for the data file schemas.

---

## Prior art and design decisions

The research dossier (`musubi_research_dossier.md`) documents the full prior art landscape this architecture draws from: BDI agent theory, OCC appraisal models, MemGPT/Letta's memory block design, Generative Agents, and the SillyTavern companion ecosystem. Read it before making significant changes to the architecture.
