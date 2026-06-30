# Personas

Each subdirectory here is a named persona. The name of the directory is what you use
to switch to it: `/persona switch asuka`, `/persona switch steward`, etc.

Each persona directory contains at minimum:

```
personas/
└── asuka/
    ├── persona.md      ← the agent's identity (becomes SOUL.md on activation)
    └── voice.yaml      ← TTS provider, voice ID, and expression bracket set
```

`persona.md` in each directory follows the compressed schema defined in the root `persona.md`.
**Before writing a persona, read `AUTHORING.md` in this directory.** It documents the rules
behind the schema — what each section does, why section order matters, how to write voice
directives correctly, and the failure modes to avoid.

## Adding a persona

1. Create a directory: `personas/<name>/`
2. Copy the template: `cp persona.md personas/<name>/persona.md`
3. Fill it in — read `AUTHORING.md` first, refer to `asuka/persona.md` as a worked example
4. Create `personas/<name>/voice.yaml` with TTS config and expression bracket set
5. Switch to it: `/persona switch <name>`

## Isolation

Each persona maintains completely separate state per user. Persona A's version of a
user and Persona B's version of that same user share nothing — different facts,
different relationship state, different memory. They do not know about each other.

## Shared infrastructure

Skills (`skills/talking.md`, `skills/processing.md`) and templates are shared across
all personas. Only `persona.md` and `voice.yaml` differ per persona. The skills
reference the persona schema — they adapt to whatever identity is active.

## Reference

| File | What it does |
|---|---|
| `AUTHORING.md` | Authoring guide — schema rules, section order, sizing, failure modes |
| `../persona.md` | Template — copy this when creating a new persona |
| `asuka/persona.md` | Worked example of the compressed schema |
| `asuka/voice.yaml` | Worked example of TTS voice configuration |
| `../voice-research.md` | ElevenLabs v3 integration details and platform research |
