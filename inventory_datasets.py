"""
inventory_datasets.py - Run this after organizing your datasets/ folder
to get an honest count of what you actually have per species/class.

Usage: python inventory_datasets.py
Outputs: dataset_inventory.csv - open this in Excel/Sheets to review
"""

import os
import csv

DATASET_ROOT = "datasets"
OUTPUT_CSV = "dataset_inventory.csv"

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

def count_images(folder_path):
    return sum(
        1 for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS
    )

def main():
    rows = []
    for species in sorted(os.listdir(DATASET_ROOT)):
        species_path = os.path.join(DATASET_ROOT, species)
        if not os.path.isdir(species_path):
            continue

        species_total = 0
        for disease_class in sorted(os.listdir(species_path)):
            class_path = os.path.join(species_path, disease_class)
            if not os.path.isdir(class_path):
                continue

            count = count_images(class_path)
            species_total += count
            rows.append({
                "species": species,
                "class": disease_class,
                "image_count": count,
                "flag": "LOW - needs review" if count < 100 else ""
            })

        rows.append({
            "species": species,
            "class": "--- SPECIES TOTAL ---",
            "image_count": species_total,
            "flag": ""
        })

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["species", "class", "image_count", "flag"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print("Open it and check the 'flag' column for any classes under 100 images.")

if __name__ == "__main__":
    main()
