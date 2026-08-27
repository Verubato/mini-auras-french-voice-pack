# MiniAurasVoicePackFrench - bot reference

Version 1.0.1. Interface version 120100. No saved variables, no options UI,
no slash commands.

## What it does

Adds two French voices, **Nicolas** (male) and **Adina** (female), to the
voice pack dropdown in MiniAuras' Alerts settings. They speak the French
spell names for the same announcements the shipped English voices cover:
important cooldowns, defensive cooldowns, and enemy debuffs.

The addon is audio plus one registration call. It draws nothing, stores
nothing, and does not change how or when MiniAuras announces.

## How it works

- Ships one OGG per announced spell name under
  `Sounds\Nicolas\` and `Sounds\Adina\`, using the same file names as
  MiniAuras' own packs.
- Hands both folders to MiniAuras through
  `MiniAurasApi.v1:RegisterVoicePack`, tagged for the `frFR` client locale.
- MiniAuras is an optional dependency, so it normally loads first. If it has
  not, the addon waits on ADDON_LOADED and registers as soon as the API
  appears.

## Settings

None of its own. The voice is picked in MiniAuras under **Alerts → Voice
pack**, and the choice is saved by MiniAuras.

## Troubleshooting

**"The voices are not in the dropdown."** They are offered on French
clients only. On any other client the dropdown shows MiniAuras' English
voices instead. The names stay reserved everywhere, so a saved
setting still means this pack when the player switches back to a French
client.

**"The dropdown is empty of French voices but the addon is enabled."** Check
MiniAuras itself is installed and enabled, and is recent enough to have the
voice pack API (5.2.0 and later).

**"A spell announces in English."** That name had no French entry when the
clips were rendered; the generator falls back to the English name and says
so. Re-running the two scripts fixes it.

**"The announcement is not what my client calls the spell."** Deliberate for
about thirty-five names. Long names are cut down to the part players react
to, and six ids are announced on the aura rather than the cast, so the
client's name for them belongs to a different ability.
