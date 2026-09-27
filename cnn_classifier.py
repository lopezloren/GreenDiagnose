"""
cnn_classifier.py - Species-specific CNN image classification for GreenDiagnose.

Assumes one fine-tuned model per species (the "one model per species" option
from your kickoff plan's Step 1 decision). If your team instead chooses a
single shared model with species-filtered output, swap load_model() and
classify_image() accordingly - the route in app.py doesn't need to change.

Expects trained models saved as:
    models/<species_id>.h5
And a matching class-index mapping saved as:
    models/<species_id>_classes.json
    e.g. {"0": 12, "1": 15, "2": 9}   -> maps model output index to disease_id in your DB

You'll generate both of these files at the end of your Sprint 3/4 model
training work in Colab - see the training script skeleton note at the
bottom of this file.
"""

import json
import numpy as np
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.preprocessing import image as keras_image

IMG_SIZE = (224, 224)  # standard MobileNetV2 input size

# Simple in-memory cache so each species model is loaded from disk once,
# not on every single request - loading a Keras model repeatedly is slow.
_model_cache = {}
_class_map_cache = {}


def _load_model_for_species(species_id):
    if species_id not in _model_cache:
        model_path = f"models/{species_id}.h5"
        _model_cache[species_id] = keras_load_model(model_path)

        with open(f"models/{species_id}_classes.json") as f:
            _class_map_cache[species_id] = json.load(f)

    return _model_cache[species_id], _class_map_cache[species_id]


def _preprocess_image(image_path):
    img = keras_image.load_img(image_path, target_size=IMG_SIZE)
    arr = keras_image.img_to_array(img)
    arr = arr / 255.0  # match whatever normalization you used during training
    arr = np.expand_dims(arr, axis=0)
    return arr


def classify_image(image_path, species_id):
    """
    Runs inference on the uploaded photo using the model trained for
    this specific species.

    Returns:
        (disease_id: int, confidence: float)
    """
    model, class_map = _load_model_for_species(species_id)
    processed = _preprocess_image(image_path)

    predictions = model.predict(processed)[0]  # array of probabilities per class
    print(f"DEBUG: Raw model predictions: {predictions}")
    top_index = int(np.argmax(predictions))
    confidence = float(predictions[top_index])

    disease_id = class_map[str(top_index)]

    return disease_id, confidence


# ==============================================================
# Training script skeleton (run separately in Google Colab, not here)
# ==============================================================
"""
Rough shape of your Sprint 3/4 training notebook, per species:

    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
    from tensorflow.keras.models import Model

    base_model = MobileNetV2(input_shape=(224,224,3), include_top=False, weights='imagenet')
    base_model.trainable = False  # freeze for initial transfer learning pass

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(NUM_CLASSES_FOR_THIS_SPECIES, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # train on your prepared, species-specific dataset with data augmentation
    # (rotation, brightness variation) to make the most of a smaller dataset

    model.save(f"models/{species_id}.h5")
    # also save your class_index -> disease_id mapping as {species_id}_classes.json

Report accuracy, precision, recall, and a confusion matrix on a held-out
test set per species for your Chapter 4 results - keep this evaluation
code and output alongside your training notebook.
"""
