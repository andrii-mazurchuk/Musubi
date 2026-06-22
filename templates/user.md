# User: {id}

<!-- Copy this template to data/users/{id}.md when a new user has their first session.
     The processing agent owns this file after the first session. Do not hand-edit it
     unless you have a good reason. -->

**First contact:** {YYYY-MM-DD}
**Last session:** {YYYY-MM-DD}
**Session count:** 0

---

## Facts

What the agent knows about this person that doesn't change session to session.
The processing agent adds to this section; it rarely removes from it.

- [Name or preferred name, if shared]
- [Anything structural about their situation: job, where they live, major life context —
  only if they've shared it and it matters for how to talk with them]
- [Preferences, communication style, things they respond well or badly to]
- [Running topics they've returned to across multiple sessions]

**Size cap:** Keep this section under ~300 words. When it's full, the processing agent
drops the least-load-bearing facts to make room. Facts that are load-bearing for the
relationship state (see below) are never dropped.

---

## Relationship State

Three dimensions, each with a current value (0.0–1.0) and a direction (↑ stable ↓).
Values decay slowly toward 0.5 (baseline) when sessions are infrequent.

**Trust:** {0.5} {→}
*How much the agent expects this person to be honest, consistent, and good-faith.*
[One sentence on what's driving the current value, updated by the processing agent.]

**Warmth:** {0.5} {→}
*The agent's genuine affection and goodwill toward this person, built from accumulated
positive moments.*
[One sentence on what's driving the current value.]

**Friction:** {0.0} {→}
*Accumulated irritation or unresolved tension. Decays faster than trust or warmth.
Not the same as low warmth — friction is specific and event-driven.*
[One sentence on what's driving the current value, or "None currently."]

---

## Significant Moments

Events or exchanges that meaningfully shifted the relationship state.
The processing agent adds entries here. Oldest entries are dropped first when at cap.

**Size cap:** Keep to ~5 entries maximum.

- [{YYYY-MM-DD}] [One sentence: what happened and which dimension it moved and why.]
- [{YYYY-MM-DD}] [...]

---

## Processing Notes

Internal notes the processing agent leaves for itself about patterns it's noticing
that don't fit cleanly into Facts or Significant Moments.

[Example: "Tends to deflect when asked directly about their own goals. Not avoidance —
feels more like they haven't decided yet. Don't push."]

**Size cap:** ~100 words. Overwrite rather than append.
