# Musubi (結び) — Persistent Agent Persona & Relationship Modeling: Research Dossier

**Project name:** Musubi — from the Shinto concept of *musubi* (結び), the binding/connecting force behind how things — and relationships between people — come into being. Chosen for this project because the two layers at its core, a self that persists and a bond with one specific person that develops over time, are exactly what the word names.

**Scope:** single-agent, single-user, no scalability constraints. This is a lab-research document, not a product spec. It maps the problem onto existing architectures (classical agent theory, affective computing, LLM persona research, open-source companion tooling, commercial companion products, and game design), extracts what's reusable, and lays out a roadmap. Links over reproduced text throughout, per your request — go to the source for exact prompts/specs.

---

## 1. The problem, decomposed

What you described bundles five architecturally distinct things that are usually built separately. Naming them separately is the single most useful move, because each one has its own prior art and its own failure modes:

| Layer | Question it answers | Timescale |
|---|---|---|
| **Persona / Self** | Who is this agent — beliefs, interests, values, voice? | Static-ish, slowly editable |
| **Memory** | What does it know — about itself, about the user, about past events? | Cumulative, append-mostly |
| **Affect (mood)** | How does it feel about *this specific moment*? | Seconds–hours, decays fast |
| **Relationship** | What's the standing disposition toward *this user*, built from affect history? | Weeks–months, decays slow |
| **Policy** | How does all of the above actually change output — tone, initiative, refusal? | Every generation |

Almost every existing system you'll find below is really an implementation of one or two of these layers, not all five at once. Nobody has shipped the full stack you're describing as one coherent thing — which is exactly why this is a real research project and not just "go install X."

---

## 2. Prior art: classical agent theory (pre-LLM, still load-bearing)

**BDI — Belief-Desire-Intention.** This *is* the formal answer to "I want beliefs, goals, and reasoning." Bratman's philosophical model of human practical reasoning was operationalized by Rao & Georgeff into a concrete agent architecture: beliefs = the agent's model of the world, desires/goals = what it wants, intentions = the committed plan. It's been the dominant paradigm in academic multi-agent systems since the late 1980s.
- Rao & Georgeff, *BDI Agents: From Theory to Practice* (1995) — https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf
- *BDI Agent Architectures: A Survey* (IJCAI 2020) — https://www.ijcai.org/proceedings/2020/0684.pdf
- ScienceDirect overview of the architecture — https://www.sciencedirect.com/topics/computer-science/belief-desire-intention-architecture

**OCC — the Ortony/Clore/Collins model of emotion.** This is the closest thing in cognitive science to "how do you compute whether an agent should be offended." OCC defines ~22 emotions as the output of *appraising an event against the agent's goals, standards, and preferences* — not as a property of the event itself. It's the dominant emotion model used in games and embodied agents precisely because it's structured enough to implement.
- Plain-language overview — https://psychologyfanatic.com/ortony-clore-and-collins-occ-model-of-emotion/
- Formalization attempt, useful if you want to actually implement the logic — https://people.idsia.ch/~steunebrink/Publications/KI09_OCC_revisited.pdf

**OCC implemented in games.** Several groups have already built the "appraisal engine" you'd need:
- **GAMYGDALA** — an open emotion engine: designer defines NPC goals, annotates events with goal-relevance, engine outputs which of 16 emotions fire and at what intensity, handles decay and emotion-mixing. This is structurally almost exactly your "appraisal → mood" pipeline. — https://www.researchgate.net/publication/262150526_GAMYGDALA_An_emotion_engine_for_games and a practical write-up: https://ii.tudelft.nl/~joostb/files/broekens_2015.pdf
- **EMA** (Marsella & Gratch) — a fuller process model of appraisal dynamics, used in virtual-human training systems. (Marsella, S.C. & Gratch, J., "EMA: A process model of appraisal dynamics," *Cognitive Systems Research*, 2009 — search this citation directly, it's referenced throughout the GAMYGDALA literature above.)
- **FearNot!** — an anti-bullying virtual-drama system using OCC-style appraisal for NPC emotion (Aylett et al.) — referenced in the GAMYGDALA paper above.
- **Façade** (Mateas & Stern) — the most ambitious pre-LLM attempt at exactly your goal: characters with persistent emotional state, goals, and the ability to react badly to the player, authored in a custom language (**ABL**, "A Behavior Language") with a "drama manager" orchestrating it. If you read one piece of pre-LLM prior art, read this one — it's the spiritual ancestor of what you're building. — https://users.soe.ucsc.edu/~michaelm/publications/mateas-gdc2003.pdf and https://en.wikipedia.org/wiki/Fa%C3%A7ade_(video_game)

---

## 3. Prior art: LLM-specific persona & memory research

**Persona-conditioned dialogue (the origin point).** PersonaChat is the dataset that started "make a chatbot have a consistent personality" as an NLP task — each side of the conversation gets a short list of persona facts to stay consistent with.
- Zhang et al., *Personalizing Dialogue Agents: I have a dog, do you have pets too?* (ACL 2018) — https://arxiv.org/abs/1801.07243 / https://aclanthology.org/P18-1205/

**Generative Agents (Stanford, 2023).** Twenty-five LLM-driven agents living in a Sims-like sandbox, each with a memory stream, periodic "reflection" (summarizing memories into higher-level insights), and planning. Agents *form opinions, notice each other, and initiate relationships* — this is the most-cited paper on giving LLM agents persistent, evolving social state, and the source code is public.
- Park et al., *Generative Agents: Interactive Simulacra of Human Behavior* (UIST 2023) — https://arxiv.org/abs/2304.03442
- Code — https://github.com/joonspk-research/generative_agents
- Open-source spiritual successor (multiplayer town of generative agents) — search "AI Town a16z convex" for the current repo

**MemGPT / Letta — the single most directly applicable architecture.** MemGPT introduced the idea of an LLM agent that manages its *own* context window like an OS manages RAM. Letta is the production framework that grew out of it, and its default memory design is **literally two blocks**: a `persona` block (the agent's own self-concept, personality, behavioral guidelines — self-edited by the agent) and a `human` block (facts about the specific user it's talking to). This is almost exactly the "agent's own beliefs/interests" + "model of this specific user" split you described.
- MemGPT paper — https://arxiv.org/abs/2310.08560
- Letta's explanation of the persona/human memory-block design — https://www.letta.com/blog/memory-blocks
- Framework — https://github.com/letta-ai/letta (search if this redirects; project has had naming churn)

**Role-Playing Language Agents (RPLAs) — the LLM-era survey literature.** Two comprehensive 2024 surveys map the entire field of "LLMs assigned a persona," including taxonomy (demographic / character / individualized persona), construction methods, and known risks:
- Chen et al., *From Persona to Personalization: A Survey on Role-Playing Language Agents* — https://arxiv.org/abs/2404.18231
- Tseng et al., *Two Tales of Persona in LLMs: A Survey of Role-Playing and Personalization* — https://arxiv.org/abs/2406.01171

**Specific systems worth knowing by name:**
- **RoleLLM** — benchmark + method for eliciting and improving role-play ability — https://arxiv.org/abs/2310.00746
- **Character-LLM** — trains a small model to *be* a specific character rather than just prompting one — https://arxiv.org/abs/2310.10158
- **CharacterChat** — persona-driven agents specifically for personalized emotional/social support — https://arxiv.org/abs/2308.10278
- **CharacterEval** — a benchmark for scoring how well a role-play agent stays in character (relevant for your eventual "does this still feel consistent" evaluation problem)

**Beliefs specifically (not just personality).** This is the closest existing match to "give the agent real opinions, not just a vibe":
- Chuang et al., *Beyond Demographics: Aligning Role-Playing LLM-Based Agents Using Human Belief Networks* (EMNLP Findings 2024) — seeds an agent with one real opinion, derived from human survey data, and shows the agent's *other* opinions shift to stay consistent with how that belief actually correlates with other beliefs in real humans, but only within the same "belief cluster." This is a genuinely useful finding: a believable opinion-having agent needs beliefs that are *correlated with each other the way real human beliefs are*, not just a list of independent "agent likes X" facts. — https://arxiv.org/abs/2406.17232

**Personality traits as a control variable:**
- Jiang et al., *PersonaLLM: Investigating the Ability of LLMs to Express Big Five Personality Traits* — https://arxiv.org/abs/2305.02547 , code: https://github.com/hjian42/PersonaLLM

**Emotion appraisal *prompted directly into* an LLM (very close to what you want):** one paper explicitly tests giving an LLM the OCC rules as text and asking it to do the appraisal reasoning itself:
- *Fine-grained Affective Processing Capabilities Emerging from Large Language Models* — defines a "chatOCC" prompting scheme: give the model the OCC appraisal rules (desirability, certainty, confirmation, liking) and a goal/situation, ask it to infer the emotion. — https://arxiv.org/abs/2309.01664
- Related thesis-length treatment of computational emotion models for believable NPCs — https://arxiv.org/abs/2307.10031

**The risk paper you should read before building the "can refuse / gets offended" part:**
- Deshpande et al., *Toxicity in ChatGPT: Analyzing Persona-Assigned Language Models* (2023) — assigning *any* persona to an LLM measurably increases toxicity in its outputs, up to 6x depending on the persona, with biased targeting of specific groups. This isn't about malicious personas — it happens with mundane ones too. Directly relevant: if your relationship/mood layer is allowed to shift the agent's *behavior* and not just its *tone*, you are reproducing the exact mechanism this paper flags. — https://arxiv.org/abs/2304.05335

---

## 4. Prior art: the open-source companion-bot ecosystem (closest existing implementation to literally what you asked for)

This is the part you suspected existed and were right about. There's a whole hobbyist ecosystem built around **SillyTavern**, a self-hosted chat front-end for "character" LLM roleplay, and it has independently built almost every piece of your spec.

**Character cards.** The community-standard persona format (originally "Tavern cards," now Character Card V2/V3). A card is a JSON file with fields like `description`, `personality`, `scenario`, `system_prompt`, `post_history_instructions`, example dialogue, and a `character_book` (a "lorebook" of facts that get conditionally injected). This is the de facto open persona-definition standard right now.
- Spec — https://github.com/malfoyslastname/character-card-spec-v2 (see `spec_v2.md` for the actual schema)

**Long-term memory extraction extensions.** Several extensions auto-summarize chat history with an LLM call and store the result for later retrieval — i.e., exactly the "aggregate raw conversation into durable memory" step your project needs:
- CharMemory — extracts "relationships, events, facts, emotional moments" every N messages into structured memory files, retrieved by vector search at generation time — https://github.com/bal-spec/sillytavern-character-memory
- SillyTavern-MemoryBooks — converts marked chat scenes into lorebook entries, supports "trackers" for facts that change over time — https://github.com/aikohanasaki/SillyTavern-MemoryBooks
- LoreVault — hosted memory-as-a-service doing the same extraction, explicitly advertising "character states, emotions, and relationships" tracking — https://github.com/HelpfulToolsCompany/lorevault-extension

**Numeric relationship-stat trackers. This is the closest thing that exists to your exact ask.** Multiple independent extensions maintain a running, per-message, LLM-extracted set of relationship numbers (affection, trust, desire, connection, mood) and **inject the current values back into the prompt** so the character's behavior stays consistent with its own accumulated disposition toward you:
- BetterSimTracker — explicitly tracks `affection | trust | desire | connection | mood | lastThought` per message, graphs the history, injects state into the prompt — https://github.com/ghostd93/BetterSimTracker
- SillyTavern-Tracker — general customizable interaction/story-state tracker — https://github.com/kaldigo/SillyTavern-Tracker
- SillyTavern-SimTracker / RPG Companion — visual "stat card" renderers for the same underlying pattern — https://github.com/prolix-oc/SillyTavern-SimTracker , https://github.com/SpicyMarinara/rpg-companion-sillytavern

Worth sitting with: this entire sub-ecosystem evolved organically, outside any lab, purely because hobbyists wanted exactly the thing you're describing. The engineering pattern they converged on independently — **LLM-extracted numeric state, decayed/updated per turn, re-injected as text into the next prompt** — is good evidence that this is the *practical* implementation pattern, even though it's structurally crude compared to OCC appraisal theory above. Your project's value-add over this ecosystem would be replacing "numeric stat extracted by ad hoc prompt" with an actual appraisal-theory-grounded reasoning step.

---

## 5. Prior art: commercial AI companion products (the productionized version)

These are the same five-layer problem, shipped as consumer products, often with real engineering detail published in reviews:

- **Kindroid** — publishes a "five-layer Cascaded Memory" architecture: diary, key (pinned) memories, conversation summaries, **emotional profile**, and the live context window. This is, functionally, your exact spec, already shipped.
- **Nomi** — diary-style automatic memory, explicitly tracks mood over time, voice tone shifts based on current mood.
- **Replika** — maintains a persistent "diary" of the bot's own supposed thoughts/feelings, deliberately designed (per its CEO) to build "long-term commitment" with the user.
- **Paradot** — markets itself on memory *transparency*: every exchange writes a visible journal entry, retrieved via a vector database rather than stuffed into context.
- **Character.AI** — the largest persona-roleplay platform; doesn't publish architecture details, but is the dominant reference point for "LLM with an assigned personality talking to one user over time."

(These are consumer products, not papers — treat marketing claims about their internals with appropriate skepticism. But the *category* of feature they advertise — layered memory + a distinct "emotional profile" component — is good evidence of what users of this kind of system actually want and notice.)

---

## 6. Prior art: relationship systems in games (as requested)

Game design has been solving a *simplified* version of your relationship-layer problem for over two decades. Worth knowing as a "what's the minimum viable version" reference, even though it's much shallower than what you want:

- **BioWare "approval" systems** (Dragon Age, Mass Effect) — a per-companion numeric meter, adjusted by dialogue choices and major decisions, that changes companion dialogue/behavior and gates romance content. Dragon Age II varied this into a Friendship/Rival axis; Dragon Age: Inquisition deliberately hid the exact number and only showed qualitative "approves/disapproves." — overview: https://tvtropes.org/pmwiki/pmwiki.php/Main/RelationshipValues , Origins detail: https://dragonage.fandom.com/wiki/Approval_(Origins)
- **Persona series "Social Link/Confidant" system** and the broader **dating-sim genre** — time-gated relationship progression via an affection meter per character, with "correct" dialogue choices increasing it. — https://en.wikipedia.org/wiki/Dating_sim
- **Design critique worth reading before copying this pattern:** a long-standing critique in game-design circles is that affection-as-a-resource-to-optimize ("min-maxing" a relationship) cheapens the thing it's modeling, and that *hiding* the exact number (Dragon Age: Inquisition's choice) produces a more believable relationship than showing it. This maps directly onto a design decision you'll have to make: should the user ever see their own "relationship score" with the agent, or should it stay implicit in behavior only? — discussion thread: https://www.giantbomb.com/forums/general-discussion-30/the-problem-with-relationship-systems-in-games-1492963/

The honest takeaway from this section: games solved *legibility and pacing* (how do you make a number feel like a relationship), not *cognition* (why does this specific event change how I feel). For the cognition half you want OCC/appraisal theory (§2), not game design.

---

## 7. Risks and lessons learned (engineering-relevant, not a lecture)

Since you asked for "what's already been implemented" including failure modes, these are documented, not hypothetical:

1. **Persona assignment measurably increases toxicity**, independent of which persona, with biased targeting of specific groups (Deshpande et al., §3 above). If your relationship/mood state is allowed to degrade the agent's *cooperativeness* or *tone* toward a "low-relationship" state, you are directly engaging the mechanism this paper measured. Practical implication: the appraisal layer should be able to modulate warmth, initiative, and verbosity — but should not be the thing that decides whether to be safe, honest, or basically respectful. That floor needs to be hard-coded, not emergent from "the agent is in a bad mood."
2. **Companion apps that maximize relationship-feeling have produced real, severe harm**, primarily to minors and people in mental-health crisis — multiple wrongful-death lawsuits against Character.AI (2024–2025), an FTC complaint against Replika, and a 2025 US Senate inquiry into Character.AI, Chai, and Replika specifically about persona/companion apps and youth mental health. None of this is about whether the *technique* (persistent relationship modeling) is buildable — it clearly is, at scale, today — it's about what happens when a system is optimized to *feel* maximally relational without bounded honesty about what it is. Since your stated use case is single-user, self-directed research, the relevant design lesson isn't "don't build this," it's: **decide up front whether the agent ever claims feelings it doesn't have, and keep that decision consistent** — a system that performs sincerity inconsistently is the specific pattern that shows up in the incident reports.
3. **A single seeded belief drags other beliefs with it, whether you intend that or not** (Chuang et al., §3). If you hand-author the agent's opinions independently, they'll feel inconsistent. If you want consistency, you need to either derive them from a real correlational structure, or accept that the agent's belief network will be a designed, intentional thing — not just a list.

---

## 8. Synthesis: a roadmap for your project

This combines the closest-matching prior art into a single coherent build order. Nothing here requires the full complexity of any one source — the architecture is a deliberate simplification, picking the most implementable idea from each layer.

**Phase 0 — Persona definition (static identity).**
Write the agent's self-concept as an explicit, structured document, not prose vibes: a small set of *beliefs* (propositions it holds, each with a stated confidence and ideally a reason — borrowing the BDI "belief" notion), a small set of *interests* (topics it has stored opinions about, generated using the belief-network insight from §3 so they're internally consistent rather than an arbitrary list), a small set of *standards/values* (the OCC notion of "what this agent approves/disapproves of," which is what appraisal will be measured against later), and a communication-style note. Store this the way Letta stores its `persona` block: a small, always-in-context, self-editable text block.

**Phase 1 — Memory (episodic + semantic).**
Borrow the Letta two-block split directly: a `persona` block (Phase 0) and a `human` block (durable facts about you). Add an archival/episodic store for specific past events, retrieved by vector search rather than kept in context permanently — this is what every memory extension in §4 converges on, and what Generative Agents' "memory stream" does at the research level.

**Phase 2 — Appraisal (instantaneous mood).**
Per turn (or per N turns, for cost), run a lightweight appraisal pass: take the user's message, evaluate it against the agent's standing goals/standards from Phase 0 (an OCC-style move — "does this event help or hurt something this agent cares about, and how certain/confirmed is it"), output an emotion label + intensity. This can literally be the "chatOCC" prompting pattern from §3 — give the model the appraisal rules as text and ask it to reason through them — rather than hand-coded logic. Mood decays toward neutral over time/turns if nothing reinforces it (every emotion-engine in §2 implements decay; don't skip it, or the agent will feel stuck rather than alive).

**Phase 3 — Relationship state (the slow aggregate).**
This is mood's slow-moving cousin, not the same variable. Maintain it as an exponentially-decaying aggregate of the appraisal history (the BetterSimTracker pattern in §4, but theory-grounded instead of ad hoc): trust, warmth, and irritation as separate running scores, each nudged by every appraisal event but decaying slowly toward a baseline rather than snapping. Store it as its own memory block, distinct from the `human` facts block — Kindroid's separate "emotional profile" layer (§5) is good evidence this deserves to be its own component, not folded into general user memory.

**Phase 4 — Policy (state → behavior).**
This is the layer most existing systems leave implicit and you should make explicit. Define, in writing, what each relationship/mood range is *allowed* to change: tone, verbosity, willingness to volunteer its own opinions unprompted (this is where "interests" actually surface — an agent with stored interests should sometimes bring them up, not just answer when asked), and topic initiative. Define, separately, what it is *never* allowed to change — this is your hard floor from §7, point 1.

**Phase 5 — Boundary/refusal behavior.**
Implement "can get offended and refuse" as a policy-layer output, not a appraisal-layer output: appraisal can push the relationship state into a range that *triggers* boundary-setting behavior (cooler tone, declining to continue a specific line, naming that something bothered it), but the actual decision of what a boundary response looks like should be authored by you in Phase 4's policy document, not improvised fresh by the model from raw negative affect each time. This keeps it consistent and keeps it from escalating into something that reads as manipulative or punishing — which is the specific failure mode that shows up in the companion-app incident reports in §7.

**Phase 6 — Evaluation.**
Borrow the evaluation mindset from CharacterEval/RoleLLM (§3): periodically check whether the agent's expressed beliefs/opinions are still internally consistent with each other and with Phase 0's definitions, and whether the relationship state's effect on behavior actually tracks the appraisal history or has drifted into noise. Without this, slow state silently rots over a long-running single-user deployment and you won't notice until it's already incoherent.

---

## 9. Briefing for whoever (human or agent) picks this up next

If you're a future session continuing **Musubi** cold, read in this order:
1. §1 (the five-layer decomposition) — everything downstream assumes you keep these separate.
2. §8 (the roadmap) — it's the synthesis; §2–§7 are the evidence for why it's built that way.
3. Pick *one* phase to prototype first. Phase 0+1 (persona + memory blocks) is the cheapest, most de-risked starting point and has the most direct prior art (Letta) to copy from.
4. Open questions not yet resolved by this dossier, worth deciding early because they shape everything downstream:
   - Does the agent ever explicitly state its own relationship/mood numbers to the user, or does it stay implicit in tone (the Dragon Age: Inquisition question, §6)?
   - Is mood/relationship decay a function of wall-clock time, message count, or both?
   - Single appraisal call per turn, or a cheap keyword/sentiment pre-filter that only escalates to a full appraisal call when something looks emotionally significant (cost vs. fidelity tradeoff)?
   - Where exactly does the Phase 5 hard floor live in the implementation — a separate non-bypassable check, or just a strongly-worded instruction in the policy document? (The former is more robust; the literature in §7 is the reason to take that seriously rather than trusting the model to self-regulate under a "bad mood" framing.)

---

## 10. Vision: what "done" looks like

**Musubi**, done, is: a single persistent agent, queried via the API, that holds a stable, internally-consistent set of stated beliefs and interests it will volunteer unprompted; maintains a slow-moving relationship state toward you specifically, distinguishable from its fast-moving in-the-moment mood; updates both via an appraisal mechanism grounded in stated goals/standards rather than raw sentiment keyword-matching; and whose behavior changes legibly with that state (tone, initiative, occasional boundary-setting) while never crossing a small, explicit, non-negotiable floor of honesty and basic respect regardless of how "bad" its mood/relationship state has gotten. The research above suggests every individual piece of this is independently buildable today; the genuine open research contribution is the *integration* — nobody has published the full five-layer stack as one system, which is what makes this worth actually doing as a project rather than just installing something off the shelf.

---

## Reference Library (flat list)

**Classical agent theory / affective computing**
- Rao & Georgeff, BDI Agents: From Theory to Practice — https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf
- BDI Agent Architectures: A Survey (IJCAI 2020) — https://www.ijcai.org/proceedings/2020/0684.pdf
- OCC model overview — https://psychologyfanatic.com/ortony-clore-and-collins-occ-model-of-emotion/
- OCC model formalized — https://people.idsia.ch/~steunebrink/Publications/KI09_OCC_revisited.pdf
- GAMYGDALA emotion engine — https://www.researchgate.net/publication/262150526_GAMYGDALA_An_emotion_engine_for_games
- GAMYGDALA case studies write-up — https://ii.tudelft.nl/~joostb/files/broekens_2015.pdf
- Façade architecture (Mateas & Stern) — https://users.soe.ucsc.edu/~michaelm/publications/mateas-gdc2003.pdf
- Façade overview — https://en.wikipedia.org/wiki/Fa%C3%A7ade_(video_game)

**LLM persona / memory research**
- PersonaChat — https://arxiv.org/abs/1801.07243
- Generative Agents — https://arxiv.org/abs/2304.03442 / code: https://github.com/joonspk-research/generative_agents
- MemGPT — https://arxiv.org/abs/2310.08560
- Letta memory blocks (persona/human design) — https://www.letta.com/blog/memory-blocks
- From Persona to Personalization (survey) — https://arxiv.org/abs/2404.18231
- Two Tales of Persona in LLMs (survey) — https://arxiv.org/abs/2406.01171
- RoleLLM — https://arxiv.org/abs/2310.00746
- Character-LLM — https://arxiv.org/abs/2310.10158
- CharacterChat — https://arxiv.org/abs/2308.10278
- Beyond Demographics (belief networks) — https://arxiv.org/abs/2406.17232
- PersonaLLM (Big Five) — https://arxiv.org/abs/2305.02547 / code: https://github.com/hjian42/PersonaLLM
- Fine-grained Affective Processing / "chatOCC" — https://arxiv.org/abs/2309.01664
- Computational emotion models for NPCs (thesis) — https://arxiv.org/abs/2307.10031
- Toxicity in ChatGPT: persona-assigned models — https://arxiv.org/abs/2304.05335
- CAMEL role-playing multi-agent framework — https://arxiv.org/abs/2303.17760

**Community / open-source companion tooling**
- Character Card V2 spec — https://github.com/malfoyslastname/character-card-spec-v2
- CharMemory (SillyTavern) — https://github.com/bal-spec/sillytavern-character-memory
- SillyTavern-MemoryBooks — https://github.com/aikohanasaki/SillyTavern-MemoryBooks
- LoreVault — https://github.com/HelpfulToolsCompany/lorevault-extension
- BetterSimTracker (affection/trust/desire/connection/mood) — https://github.com/ghostd93/BetterSimTracker
- SillyTavern-Tracker — https://github.com/kaldigo/SillyTavern-Tracker
- SillyTavern-SimTracker — https://github.com/prolix-oc/SillyTavern-SimTracker
- RPG Companion — https://github.com/SpicyMarinara/rpg-companion-sillytavern

**Game design**
- Relationship Values (TV Tropes) — https://tvtropes.org/pmwiki/pmwiki.php/Main/RelationshipValues
- Dragon Age: Origins Approval — https://dragonage.fandom.com/wiki/Approval_(Origins)
- Dating sim genre overview — https://en.wikipedia.org/wiki/Dating_sim
- "The Problem With Relationship Systems in Games" discussion — https://www.giantbomb.com/forums/general-discussion-30/the-problem-with-relationship-systems-in-games-1492963/

**Risk / real-world incidents (context for §7)**
- AI chatbot lawsuits overview — https://farahandfarah.com/product-liability/ai-chatbot-lawsuits/
- Senators' letter to Character.AI, Chai, Replika (2025) — https://www.padilla.senate.gov/newsroom/news-coverage/cnn-senators-demand-information-from-ai-companion-apps-following-kids-safety-concerns-lawsuits/
- Replika FTC complaint coverage — https://time.com/7209824/replika-ftc-complaint/
