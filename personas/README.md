# Personas

Each subdirectory here is a named persona. The name of the directory is what you use
to switch to it: `/persona switch steward`, `/persona switch coach`, etc.

Each persona directory contains one file:

```
personas/
└── steward/
    └── persona.md      ← the agent's identity when running as "steward"
```

`persona.md` inside each directory follows the same schema as the root `persona.md`.
See the root file for the full schema.

## Adding a persona

1. Create a directory: `personas/<name>/`
2. Copy and fill in: `cp persona.md personas/<name>/persona.md`
3. Edit `personas/<name>/persona.md` with this persona's specific identity
4. Switch to it: `/persona switch <name>`

## Isolation

Each persona maintains completely separate state per user. Persona A's version of a
user and Persona B's version of that same user share nothing — different facts,
different relationship state, different memory. They do not know about each other.

## Shared infrastructure

Skills (`skills/talking.md`, `skills/processing.md`) and templates are shared across
all personas. Only `persona.md` differs. The skills reference the persona schema, so
if you change the schema for one persona, the same skills still work — they adapt to
whatever beliefs/values/standards are defined.
