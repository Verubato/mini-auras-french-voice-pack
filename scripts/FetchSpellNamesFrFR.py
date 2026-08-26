"""Rebuilds scripts/SpellNamesFrFR.json, the French name for every announced spell.

Reads the spell lists from the sibling MiniAuras checkout and asks Wowhead what the French
client calls each id. Run it after MiniAuras gains or loses an announced spell, then re-run
GenerateVoicePack.py to render whatever changed:

    python scripts/FetchSpellNamesFrFR.py

Six ids carry another ability's name, because the id we announce on is the aura rather than the
cast. Those are corrected in GenerateVoicePack.py's SHORT_NAMES, not here, so this file stays a
plain record of what the client says.
"""

import json
import pathlib
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
MINIAURAS = REPO.parent / "MiniAuras"

if not MINIAURAS.is_dir():
    sys.exit(f"MiniAuras checkout not found at {MINIAURAS}")

sys.path.insert(0, str(MINIAURAS / "scripts"))

import GenerateTtsAudio as base  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent / "SpellNamesFrFR.json"
SOURCE = "https://nether.wowhead.com/fr/tooltip/spell/%d"
# The pause is politeness.
PAUSE_SECONDS = 0.15
ATTEMPTS = 5


def fetch(spell_id):
    """A name that comes back empty leaves the spell announcing in English, so a blip is worth
    retrying rather than living with for the life of the pack."""
    request = urllib.request.Request(SOURCE % spell_id, headers={"User-Agent": "Mozilla/5.0"})

    for attempt in range(ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return (json.loads(response.read()).get("name") or "").strip()
        except Exception:
            if attempt == ATTEMPTS - 1:
                raise

            time.sleep(2**attempt)


def main():
    categories = base.parse_categories()
    ids = {}

    for spells in categories.values():
        for spell_id, name in spells.items():
            ids.setdefault(base.spoken_text(name), spell_id)

    names = {}
    failures = []
    unchanged = []

    for name, spell_id in sorted(ids.items()):
        reason = None

        try:
            french = fetch(spell_id)
        except Exception as error:  # noqa: BLE001 - the id is reported either way
            french, reason = None, str(error)

        if french:
            names[name] = french
        else:
            failures.append(f"{name} ({spell_id}): {reason or 'no French name'}")

        # French shares a fair few spell names with English, so an unchanged name is usually real.
        if french == name:
            unchanged.append(f"{name} ({spell_id})")

        time.sleep(PAUSE_SECONDS)

    OUT.write_text(
        json.dumps(names, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"{len(names)} of {len(ids)} names written to {OUT.name}")

    if failures:
        # Not fatal: a missing name falls back to the English one, which is better than no clip.
        print("no French name for:")

        for failure in failures:
            print(f"  {failure}")

    if unchanged:
        print("same as the English name, worth an eye:")

        for name in unchanged:
            print(f"  {name}")


if __name__ == "__main__":
    main()
