import json
from pathlib import Path

import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array

BASE_DIR = Path(__file__).resolve().parent
CENTROID_FILE = BASE_DIR / "models" / "species_centroids.json"

with open(CENTROID_FILE, encoding="utf-8") as f:
    _data = json.load(f)

THRESHOLD = float(_data["threshold"])
_CENTROIDS = {int(k): np.array(v) for k, v in _data["centroids"].items()}

_feat = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
    pooling="avg",
)


def looks_like_species(image_path, species_id):
    """Return (ok, similarity) for the selected species."""
    x = img_to_array(load_img(image_path, target_size=(224, 224)))
    v = _feat.predict(preprocess_input(np.expand_dims(x, 0)), verbose=0)[0]
    v = v / np.linalg.norm(v)
    sim = float(v @ _CENTROIDS[species_id])
    return sim >= THRESHOLD, sim