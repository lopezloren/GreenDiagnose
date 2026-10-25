"""
cnn_classifier.py - Species-specific CNN image classification for GreenDiagnose.

Assumes one fine-tuned model per species (the "one model per species" option
from your kickoff plan's Step 1 decision).

Expects trained models saved as:
    models/<species_id>.h5
And a matching class-index mapping saved as:
    models/<species_id>_classes.json
    e.g. {"0": 12, "1": 15, "2": 9}   -> maps model output index to disease_id in your DB

Training notes (run separately in Google Colab, not here):
    Save each species model with model.save(f"models/{species_id}.h5") and
    save its class_index -> disease_id mapping as {species_id}_classes.json.
    Keep the per-species held-out test metrics (accuracy, precision, recall,
    confusion matrix) with your Chapter 4 notebook.
"""

import json
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.preprocessing import image as keras_image

IMG_SIZE = (224, 224)  # standard MobileNetV2 input size

# Resolve paths relative to this file, not the current working directory.
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# Cache so each species model is loaded once, not on every request.
_model_cache = {}
_class_map_cache = {}


def _load_model_for_species(species_id):
    if species_id not in _model_cache:
        model_path = MODELS_DIR / f"{species_id}.h5"
        mapping_path = MODELS_DIR / f"{species_id}_classes.json"

        _model_cache[species_id] = keras_load_model(model_path)

        with open(mapping_path, encoding="utf-8") as f:
            raw_map = json.load(f)

        # JSON keys are strings; store {output_index: disease_id} as ints.
        _class_map_cache[species_id] = {
            int(index): int(disease_id)
            for index, disease_id in raw_map.items()
        }

    return _model_cache[species_id], _class_map_cache[species_id]


def _preprocess_image(image_path):
    img = keras_image.load_img(image_path, target_size=IMG_SIZE)
    arr = keras_image.img_to_array(img)
    arr = arr / 255.0  # must match the normalization used during training
    arr = np.expand_dims(arr, axis=0)
    return arr


def classify_image(image_path, species_id):
    """
    Runs inference on the uploaded photo using the model trained for
    this specific species.

    Returns:
        (top_disease_id: int,
         top_confidence: float,
         cnn_scores: dict of {disease_id: probability} for every class)
    """
    model, class_map = _load_model_for_species(species_id)
    processed = _preprocess_image(image_path)

    predictions = model.predict(processed, verbose=0)[0]
    probabilities = [float(p) for p in predictions]


    # Fail clearly if the model and mapping disagree.
    if len(probabilities) != len(class_map):
        raise ValueError(
            f"Species {species_id}: model has {len(probabilities)} outputs "
            f"but the class mapping has {len(class_map)} entries."
        )

    cnn_scores = {
        class_map[index]: probability
        for index, probability in enumerate(probabilities)
    }

    top_index = int(np.argmax(probabilities))
    top_disease_id = class_map[top_index]
    top_confidence = probabilities[top_index]

    return top_disease_id, top_confidence, cnn_scores