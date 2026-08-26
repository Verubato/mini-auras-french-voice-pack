# MiniAurasVoicePackFrench

French voice packs for [MiniAuras](https://www.curseforge.com/wow/addons/miniauras).

MiniAuras can call out important and defensive cooldowns as they land. This addon adds two
French voices to that list, speaking the French spell names rather than the English ones.

- **Nicolas** — male, a middle-aged Parisian narrator voice, clear and even.
- **Adina** — female, a young French voice, bright and welcoming.

[Discord](https://discord.gg/UruPTPHHxK)

## Install

Install MiniAuras first, then this. The voices appear in **MiniAuras → Alerts → Voice pack**
on a French client; they are hidden on other clients, so pick one from the addon's own list
of English voices there instead.

## Download

Available on [CurseForge](https://www.curseforge.com/wow/addons/miniauras-french-voice-pack).

## Regenerating the clips

The clips are baked audio, one file per announced spell name, rendered with ElevenLabs. Both
scripts expect a MiniAuras checkout beside this one, because the spell lists and the clip file
names belong to it.

```
python scripts/FetchSpellNamesFrFR.py          # after MiniAuras gains or loses a spell
python scripts/GenerateVoicePack.py            # renders whatever is missing
python scripts/GenerateVoicePack.py --force    # re-renders everything
```

`GenerateVoicePack.py` needs `ELEVENLABS_API_KEY` and ffmpeg on the path. It refuses to run if
its clip names have drifted from the packs MiniAuras ships, since a mismatched name is a clip
that silently never plays.

What the voices say is not always the client's name for the spell: `SHORT_NAMES` in
`GenerateVoicePack.py` cuts the long names down to the part a player reacts to, and corrects
the handful of ids whose aura carries another ability's name.
