"""Renders the French voice packs into src/Sounds/<pack>/.

The spell lists, the file naming and the rendering pipeline all belong to MiniAuras, so this
imports its generator from the sibling checkout rather than restating any of it. What lives here
is the French side: which voices, what they say, and the check that the clip names still match
the packs MiniAuras ships.

Run from the repo root with the ELEVENLABS_API_KEY environment variable set:
    python scripts/GenerateVoicePack.py [--force] [--allow-english]

Existing clips are skipped unless --force is given. A spell with no French name stops the run,
because a pack that announces one spell in English is worse than one that was never built;
--allow-english renders it in English anyway.
"""

import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
# MiniAuras is expected beside this repo. Nothing is copied out of it: the spell lists and the
# clip names have one owner, and a stale duplicate here would ship a pack that plays nothing.
MINIAURAS = REPO.parent / "MiniAuras"

if not MINIAURAS.is_dir():
    sys.exit(f"MiniAuras checkout not found at {MINIAURAS}")

sys.path.insert(0, str(MINIAURAS / "scripts"))

import GenerateTtsAudio as base  # noqa: E402

VOICES = {
    "Nicolas": "aQROLel5sQbj1vuIVi6B",
    "Adina": "FvmvwvObRqIHojkEGh5N",
}
# Multilingual v2 reads French the most steadily.
MODEL_ID = "eleven_multilingual_v2"

NAMES = pathlib.Path(__file__).resolve().parent / "SpellNamesFrFR.json"
OUT_DIR = REPO / "src" / "Sounds"
# The pack every generated clip name is checked against.
REFERENCE_PACK = MINIAURAS / "src" / "Sounds" / "TTS" / "David"

PREVIEWS = {
    "PreviewImportant": "Important",
    "PreviewDefensive": "Défensif",
    "PreviewEnemyDebuff": "Affaiblissement ennemi",
}
# Spoken when the pack is picked in the dropdown. A real announcement, long enough to judge the
# voice by.
PREVIEW_VOICE_TEXT = "Grâce du marcheur des esprits"

# English spell name -> what the French voices say instead of the client's name for it. Most
# entries cut a long name down to the part a player reacts to. The rest correct a name the
# client gets wrong for us, because our spell id is the aura and the aura carries another
# ability's name.
SHORT_NAMES = {
    "Arcane Surge": "Éruption",
    "Aspect of the Turtle": "Tortue",
    "Blessing of Freedom": "Liberté",
    "Blessing of Protection": "Protection",
    "Blessing of Sacrifice": "Sacrifice",
    "Blessing of Sanctuary": "Sanctuaire",
    "Blessing of Spellwarding": "Protection des sorts",
    "Celestial Alignment": "Incarnation",
    "Cloak of Shadows": "Cape",
    "Colossus Smash": "Colosse",
    "Dark Simulacrum": "Simulacre",
    "Emerald Communion": "Communion",
    "Enraged Regeneration": "Régénération",
    "Greater Invisibility": "Invisibilité",
    # The aura is Divine Shield's, so the client name is Bouclier divin.
    "Guardian of the Forgotten Queen": "Reine oubliée",
    "Incarnation: Avatar of Ashamane": "Incarnation",
    "Incarnation: Chosen of Elune": "Incarnation",
    "Incarnation: Guardian of Ursoc": "Incarnation",
    # The aura drops the form, so the client name is a bare Incarnation.
    "Incarnation: Tree of Life": "Incarnation",
    "Invoke Chi-Ji, the Red Crane": "Chi Ji",
    "Invoke Niuzao, the Black Ox": "Niuzao",
    # The aura is Yu'lon's Blessing, so the client name is Bénédiction de Yu'lon.
    "Invoke Yu'lon, the Jade Serpent": "Yu'lon",
    "Life Cocoon": "Cocon",
    "Nullifying Shroud": "Voile",
    "Obsidian Scales": "Écailles",
    "Rallying Cry": "Ralliement",
    # The aura is Amplified Refraction, so the client name is Réfraction amplifiée.
    "Refractive Images": "Images réfractives",
    # The aura is Mortal Strike's, so the client name is Frappe mortelle.
    "Sharpen Blade": "Affûtage",
    "Shield Wall": "Mur",
    "Spell Reflection": "Renvoi",
    # The aura belongs to the totem, so the client name is Totem de lien d'esprit.
    "Spirit Link": "Lien d'esprit",
    "Survival Instincts": "Instincts",
    "Touch of Karma": "Karma",
    "Unending Resolve": "Résolution",
    "Void Metamorphosis": "Métamorphose",
}


def build_texts(categories, names):
    """File stem -> the French text that stem's clip speaks, and the names with no French."""
    texts = {}
    untranslated = []

    for ids in categories.values():
        for name in ids.values():
            text = base.spoken_text(name)
            spoken = SHORT_NAMES.get(text) or names.get(text)

            if not spoken:
                untranslated.append(text)

            texts[base.slug(text)] = spoken or text

    texts.update(PREVIEWS)
    texts["PreviewVoice"] = PREVIEW_VOICE_TEXT

    return texts, sorted(set(untranslated))


def check_against_shipped(stems):
    """A pack whose file names drift from MiniAuras' own plays nothing for the clips that
    differ, and says so nowhere, so the mismatch is caught here instead."""
    if not REFERENCE_PACK.is_dir():
        sys.exit(f"reference pack not found at {REFERENCE_PACK}")

    shipped = {path.stem for path in REFERENCE_PACK.glob("*.ogg")}
    missing = sorted(shipped - stems)
    extra = sorted(stems - shipped)

    if missing or extra:
        sys.exit(f"clip names do not match {REFERENCE_PACK.name}: missing {missing}, extra {extra}")

    print(f"clip names match {REFERENCE_PACK.name}: {len(stems)} checked")


def main():
    api_key = os.environ.get("ELEVENLABS_API_KEY")

    if not api_key:
        sys.exit("set ELEVENLABS_API_KEY")

    force = "--force" in sys.argv

    names = json.loads(NAMES.read_text(encoding="utf-8"))
    texts, untranslated = build_texts(base.parse_categories(), names)

    if untranslated and "--allow-english" not in sys.argv:
        listed = "\n  ".join(untranslated)
        sys.exit(
            f"no French name for:\n  {listed}\n"
            "re-run scripts/FetchSpellNamesFrFR.py, or pass --allow-english to speak these in English"
        )

    for name in untranslated:
        print(f"WARNING: no French name for '{name}', speaking English")

    check_against_shipped(set(texts))

    rendered, reused = 0, 0

    for pack, voice_id in VOICES.items():
        pack_dir = OUT_DIR / pack
        pack_dir.mkdir(parents=True, exist_ok=True)

        for file_stem in sorted(texts):
            path = pack_dir / f"{file_stem}.ogg"

            if path.exists() and not force:
                reused += 1
                continue

            base.render(api_key, voice_id, texts[file_stem], path, 0.0, MODEL_ID)
            rendered += 1
            print(f"rendered {pack}/{path.name}")

    print(f"{rendered} clip(s) rendered, {reused} reused")


if __name__ == "__main__":
    main()
