# Voice Model Research

Research into TTS platforms for anime character voices. Started for Asuka Langley (Tsundere persona) but applies broadly.

---

## Current integration (as of 2026-06)

**Platform:** ElevenLabs v3 (`eleven_v3` model)
**Integration point:** Hermes `tts.provider: elevenlabs` in `~/.hermes/config.yaml`
**Delivery:** `gateway_voice_mode.json` routes the active Telegram chat to `voice_only` —
every agent response is converted to a voice note before delivery.

The `eleven_v3` model natively interprets expression brackets embedded in text.
These are vocal performance instructions — not spoken aloud, just shape the delivery:

```
[sighs]          [scoffs]         [angry]          [building rage]
[voice cracking] [shouting]       [defensive]      [sudden venom]
[quietly, hollow][exhausted, defeated][final defiant whisper]
[laughs softly]  [laughs]         [whispers]       [bitter]
[firmly]         [clicks tongue]  [breaking down]  [sobbing]
```

The agent embeds these in its text output. The gateway passes text directly to ElevenLabs —
no pre-processing needed. Brackets are processed on the API side and do not appear in the
displayed text (voice_only mode means text is not separately delivered).

**Persona voice configuration:** each persona directory can contain a `voice.yaml` with the
provider, voice ID, model, and character-specific expression set. See `personas/AUTHORING.md`
§Voice and TTS for the full format. The active expression set is also documented in
`skills/talking.md` under "Voice Delivery."

**Asuka voice ID:** `DODLEQrClDo8wCz460ld`

---

## Platform research (pre-2026-06)

## Option 1 — Fish Audio (cloud API)

**Best for:** quick integration into an existing cloud-based voice pipeline.

- Pre-built Asuka Langley community model: `fish.audio/m/47793977b3a2427a86ec9e7cfcaec2bf/`
- Second Asuka model: `fish.audio/m/c25fae7c07b749af9c90bea87d18a654/`
- REST/WebSocket API, voice selected by reference ID
- Output formats: `pcm`, `opus`, `mp3`, `wav`
- Model: `s2-pro` — supports emotional/tone markers
- Low latency, designed for conversational AI
- Has a Pipecat integration: https://docs.pipecat.ai/server/services/tts/fish
- Home Assistant integration: https://www.home-assistant.io/integrations/fish_audio/
- Developer guide: https://fish.audio/blog/text-to-speech-api-developer-guide/
- Main site: https://fish.audio/

**Trade-offs:** cloud dependency, per-character cost, quality varies by community model.

---

## Option 2 — RVC / Ultimate RVC (self-hosted)

**Best for:** self-hosted setup, maximum community model coverage.

How it works: two-pass pipeline. Any TTS engine generates audio → RVC converts it to the character's voice. Community has produced thousands of anime character models.

- Ultimate RVC (self-hosted app): https://github.com/JackismyShephard/ultimate-rvc
  - Supports Windows and Ubuntu 22.04/24.04
  - Has TTS→RVC pipeline built in
  - Can generate audiobooks/speech in any RVC voice
- Hugging Face RVC model hub: https://huggingface.co/spaces/zomehwh/rvc-models
- 101soundboards model library (18,000+ RVCv2 files): https://www.101soundboards.com/boards/tts/models
- GenAnime browser-based RVC (low commitment test): https://genanime.art/tools/anime-voice-changer
- SillyTavern RVC docs (good integration reference): https://docs.sillytavern.app/extensions/rvc/

**Trade-offs:** more setup, quality depends on which community model you find, no official Asuka model but community ones exist.

---

## Option 3 — Style-Bert-VITS2 (self-hosted, highest ceiling)

**Best for:** highest quality character voice if willing to fine-tune on source audio.

- GitHub: https://github.com/litagin02/Style-Bert-VITS2
- Install: `pip install style-bert-vits2` — includes an API server
- Designed specifically for expressive anime/character TTS
- English docs: https://github.com/litagin02/Style-Bert-VITS2/blob/master/docs/Style-Bert-VITS2_en.md
- Primarily Japanese but has English and Chinese support
- 2025 benchmark paper comparing VITS vs Style-Bert-VITS2 for character voices: https://arxiv.org/html/2505.17320v1
- Example: Hololive character implementation (JP + EN): https://github.com/zsxkib/hololive-style-bert-vits2

**Trade-offs:** no pre-built Asuka model — requires fine-tuning on her audio. Higher quality ceiling but requires source material and training time.

---

## Notes

- **Language:** Asuka has both a Japanese VA (Yuko Miyamura) and English VAs (Tiffany Grant, Stephanie McKeon). Decision on language affects which models are usable.
- **RVC vs VITS:** RVC is a voice conversion layer on top of TTS; Style-Bert-VITS2 is an end-to-end character TTS. RVC is easier to plug in, VITS produces more natural character voice if trained properly.
- **To explore next:** find specific Asuka RVC model files on 101soundboards or Hugging Face and evaluate quality before committing to a platform.
