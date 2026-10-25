"""Check that every species has a model, a valid class map, and matching DB IDs."""
import json
from pathlib import Path

from db import fetch_all

BASE_DIR = Path(__file__).resolve().parent
MODELS = BASE_DIR / "models"

species_rows = fetch_all("SELECT id, common_name FROM plant_species ORDER BY id")
problems = 0

for sp in species_rows:
    sid, name = sp["id"], sp["common_name"]
    h5 = MODELS / f"{sid}.h5"
    js = MODELS / f"{sid}_classes.json"

    if not h5.is_file() or not js.is_file():
        print(f"[FAIL] {sid} {name}: missing {'.h5' if not h5.is_file() else ''} {'json' if not js.is_file() else ''}")
        problems += 1
        continue

    with open(js, encoding="utf-8") as f:
        raw = json.load(f)

    try:
        mapping = {int(k): int(v) for k, v in raw.items()}
    except ValueError:
        print(f"[FAIL] {sid} {name}: keys or values are not integers (folder names, not index->ID?)")
        problems += 1
        continue

    db_ids = {r["id"] for r in fetch_all(
        "SELECT id FROM disease WHERE species_id = %s", (sid,))}

    expected_indices = set(range(len(mapping)))
    bad_ids = [v for v in mapping.values() if v not in db_ids]
    dup_ids = len(mapping.values()) != len(set(mapping.values()))
    missing_diseases = db_ids - set(mapping.values())

    if set(mapping.keys()) != expected_indices or bad_ids or dup_ids or missing_diseases:
        print(f"[FAIL] {sid} {name}: bad_ids={bad_ids} dup={dup_ids} "
              f"not_in_mapping={sorted(missing_diseases)}")
        problems += 1
    else:
        print(f"[OK]   {sid} {name}: {len(mapping)} classes, all IDs valid")

print(f"\n{problems} problem(s) found." if problems else "\nAll species passed.")