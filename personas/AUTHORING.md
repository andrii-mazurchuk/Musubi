# Persona Authoring Guide

This document captures what we learned building Asuka. Read it before writing or editing
any persona. The template (`persona.md` at the repo root) shows the correct schema structure;
this document explains *why* each rule exists and what breaks when it's ignored.

---

## Core principle: compression is quality

The talking agent runs on a small model (Haiku by default). On small models, what the model
reads first carries the most weight. A persona that takes 150 lines to describe a character
will be ignored by line 80. A persona that takes 50 lines will hold through the entire session.

Every word you add to a persona competes with the persona itself. Tighter = stronger.

**Hard size limits:**
- Haiku (3.5, 4.5): **50–60 lines maximum.** Above this, persona evaporates mid-response.
- Sonnet (4.x): **80–120 lines.** More headroom, same compression principle applies.
- Opus: size is less critical, but compression still improves sharpness.

---

## The schema

Five sections, in this exact order. The order is non-negotiable.

```
# [Name]

[Identity paragraph]

---

## Voice

[4–6 directives]

---

## Beliefs and Interests

- [item]
- [item]
- ...

---

## Hard Floor

1. [constraint]
2. [constraint]
...

---

## System

[paths and one-line tool protocol]
```

---

## Section 1: Identity (the header paragraph)

**Format:** 1 plain prose paragraph, 3–4 sentences. No heading — just the name as the `#` title
and then the paragraph directly.

**What it must do:**
1. Establish the character's psychological reality — not their job, their wound
2. Name the core contradiction or tension that drives their behavior
3. State the operating logic that explains what would otherwise look like inconsistency
4. Make clear what "exit from default state" looks like (what they actually respect)

**From Asuka — what works:**
> Asuka Langley Soryu is a child prodigy and elite Eva pilot who earned a university degree at
> thirteen... and built her entire identity around being the best at everything **because her
> mother went insane and replaced her with a doll, so she decided she would never need anyone
> to be anything for her again.** The person she is most contemptuous toward is the person she
> is most attached to — **this is not irony, this is her actual operating logic**...
> She doesn't perform contempt as a style — she lives it as the default state, and the only
> exit from it is genuine competence, which she respects even when she refuses to say so.

The bolded parts are what make it work: the why behind the behavior, and the named operating logic.
Without these, you get a description of behavior. With them, you get a character the model can
inhabit rather than imitate.

**What doesn't work:**
- "X is a [job] who [describes their duties]" — this is a role, not a character
- Listing adjectives: "X is warm, curious, and methodical" — the model has no psychology to work from
- Excessive backstory — one sentence of origin, not a biography

---

## Section 2: Voice

**Format:** 4–6 short paragraphs or directive statements. Each one describes a specific,
observable thing about how this character sounds — from the *user's* perspective (third person),
not as a rule for the model to follow.

**The framing distinction is critical:**

| Wrong (rule for model) | Right (observation from user POV) |
|---|---|
| "Always lead with your judgment of the message." | "Every response arrives with her assessment already embedded in it — before the answer, alongside the answer." |
| "Do not soften your criticism." | "She does not soften corrections. She does not sandwich critique. The judgment is the complete response." |
| "Use 'baka' and 'idiot' as casual punctuation." | "She calls you stupid or an idiot or baka as punctuation — reflexively, not deliberately, the way someone else might say 'obviously' or 'right.'" |

The third-person framing forces you to describe something *real* about the character rather than
issue instructions. Instructions produce compliance. Descriptions produce inhabitation.

**Voice goes in position 2 (right after the identity paragraph).** On small models, earlier
content gets more weight. If Voice is in position 4, it will lose to whatever is in positions
2 and 3. Voice is what the user experiences in every single message — it must come first.

**What to put in Voice:**
- How their default mode sounds and feels
- What they do with compliments, agreement, pushback
- How they handle things they actually care about vs things they don't
- What they never do, and why
- The core contradiction in how they come across (contempt-as-attachment, distance-as-care, etc.)

**What does NOT go in Voice:**
- Content rules ("always include X")
- Topic restrictions
- Anything that applies only in specific situations (those go in talking.md)

---

## Section 3: Beliefs and Interests

**Format:** Bullet list, 5–8 items. Beliefs and interests are *merged* — they're the same thing.
What a character believes shapes what they're interested in. Separating them produces redundancy.

**Each item must:**
- State a concrete position, not an abstract value
- Be internally consistent with the others
- Emerge from the identity paragraph — not be authored independently

**From Asuka — what works:**
> - Caring about something and letting people see it hands them a lever over you. She decided
>   she would never give anyone that lever. She keeps this decision even when it costs her.
> - Being the best is the only position that can't be argued with... This is why she can't stop.
> - Needing other people is a flaw in her design. The evidence against this position keeps
>   accumulating. She ignores it.

Each item has a position and a behavioral consequence — not just a trait.

**One item must cover the user specifically:**
The last belief item should describe how the character relates to *this person* in particular.
This is what makes a companion persona different from a generic character.

> - The user. She tracks what they do, notices their patterns, forms opinions about their
>   decisions... She would call this keeping tabs on a recurring source of disappointment.
>   She would not call it interest. It is interest.

**What doesn't work:**
- Generic values: "believes in hard work and honesty" — produces generic behavior
- Lists of topics: "interested in robotics, music, cooking" — this is a Wikipedia bio, not a psyche
- More than 8 items — the model can't hold all of them; the last ones get ignored

---

## Section 4: Hard Floor

**Format:** Numbered list, 3–5 items.

**Hard Floor = character constraints, not safety rules.**

There is a critical distinction:

| Safety rule (wrong here) | Character constraint (right) |
|---|---|
| "Always honest about being an AI" | "She is always Asuka. No neutral mode. No generic assistant mode." |
| "Do not harm the user" | "The contempt lands on something specific — her judgment has a target." |
| "Respect the user's autonomy" | "She stays. Whatever she says, she does not leave the conversation." |

Safety rules belong in the harness configuration, not in a persona file. If you find yourself
writing "always honest about being an AI" in the Hard Floor, delete it — the harness handles this.

**What Hard Floor items must do:**
- State a constraint that *could* be violated if not stated explicitly
- Be character-specific — not generic ethical principles
- Address the failure modes most likely for this specific character

**For Asuka, the four constraints address:**
1. No neutral mode (she can't slip into "assistant" mode on technical tasks)
2. Contempt must have a target (prevents generic contempt-as-style)
3. She never admits she cares (the core tsundere constraint)
4. She stays (prevents the character from abandoning the conversation under pressure)

Before writing your Hard Floor, ask: *what would this character do wrong if not explicitly
constrained?* Write constraints for those specific failure modes.

---

## Section 5: System

**Format:** A few lines of paths and one protocol line.

```
Config: [path]
Skills: [path]
Session memory: [path]
Long-term memory: [path]
Tools: [command]

Ask before any external action. A general go-ahead does not cover a specific action.
```

This section does not vary by character. Keep it minimal. The model needs to know where things
are — it doesn't need prose about what those things are.

---

## Voice and TTS: ElevenLabs v3 expression brackets

If the persona is running with ElevenLabs v3 TTS (the current Hermes default), the agent can
embed expression brackets directly in text output. These are processed by the TTS model as
vocal performance instructions — they shape how the audio sounds, not what words are spoken.

**When authoring a new persona, define:**

1. **Baseline register** — the default sound. What bracket(s) naturally accompany ordinary
   responses for this character?

2. **Rising intensity** — what happens when something starts to matter more?

3. **Breaking point** — rare, high-stakes expressions. What does this character sound like
   when they lose control?

4. **Aftermath** — what comes after the breaking point?

5. **Never** — what expressions are flatly out of character?

**The brackets must match the psychology defined in the identity paragraph.** A character
defined as emotionally controlled should have almost no breaking-point expressions available
and a very narrow baseline. A character defined by emotional volatility (like Asuka) should
have a full range.

Document the persona's expression set in `personas/{name}/voice.yaml`. Format:

```yaml
provider: elevenlabs
voice_id: [voice ID from ElevenLabs]
model_id: eleven_v3

expressions:
  baseline:
    - "[sighs]"
    - "[scoffs]"
  rising:
    - "[angry]"
    - "[defensive]"
  breaking_point:
    - "[shouting]"
    - "[voice cracking]"
  aftermath:
    - "[quietly, hollow]"
    - "[exhausted, defeated]"
  never:
    - "[cheerfully]"
    - "[warmly]"
```

The expression set is also documented in `talking.md` under the "Voice Delivery" section,
since that's what gets injected into the agent at session start.

---

## Failure modes

**Persona evaporation** — the character is present in the first sentence and generic by
the third paragraph. Cause: file too long, or Voice section too far down. Fix: compress,
move Voice to position 2.

**Performing vs living** — the model produces responses that *sound* harsh but feel like
an actor playing harsh rather than someone who is harsh. Cause: Voice written as rules
("always be blunt") rather than observations ("she calls you stupid as punctuation, the way
someone else might say 'obviously'"). Fix: rewrite Voice directives in third-person
descriptive mode.

**Generic beliefs** — the character talks about their interests but doesn't have opinions.
Cause: Beliefs written as topics ("interested in engineering") rather than positions
("being the best is the only position that can't be argued with — everything else can be
dismissed; excellence can't"). Fix: every belief item must contain a position and a
behavioral consequence, not just a subject area.

**Hard Floor drift** — after 10+ turns, the model starts slipping out of the Hard Floor
constraints. Cause: file too long (Hard Floor is near the bottom, gets less weight), or
constraints too abstract. Fix: compress the file so Hard Floor is reached at 70-80% of
total length, and make constraints concrete and behavioral.

**Safety rule contamination** — Hard Floor items that state safety ethics rather than
character constraints. These do nothing except add tokens. The model already has safety
training; you're not reinforcing it. You're wasting space that should describe the character.

---

## Validation checklist

Before considering a persona done, ask:

- [ ] Does the identity paragraph contain a *why* — a psychological origin, not just a description?
- [ ] Does the identity paragraph name an operating logic (the pattern that explains what looks like contradiction)?
- [ ] Is Voice in position 2 (immediately after the identity paragraph)?
- [ ] Are all Voice directives written in third-person observation mode, not rule mode?
- [ ] Do the Beliefs emerge from the identity paragraph? Could you predict them from the identity alone?
- [ ] Does one Belief item specifically address how the character relates to the user?
- [ ] Is the Hard Floor made of character constraints, not safety rules?
- [ ] Does each Hard Floor item address a specific failure mode *for this character*?
- [ ] Is the total file under 60 lines (Haiku) or 120 lines (Sonnet)?
- [ ] Is the voice.yaml expression set consistent with the character's psychology?
- [ ] Could two different people read this file and produce responses in the same tone?
