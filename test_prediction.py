
from pathlib import Path
import sys

from cnn_classifier import classify_image

image_path = Path(
    r"C:\GD datasets\Hibiscus\Hibiscus Leaf Image Dataset High-Resolution Collection of Healthy and Diseased Leaves\Hibiscus_Healthy_Diseased_leaf_Dataset\Healthy_Leaf\1.jpg"
)

species_id = 1

if not image_path.is_file():
    print("ERROR: Image file not found:", image_path)
    sys.exit(1)

try:
    disease_id, confidence = classify_image(str(image_path), species_id)

    print("\n--- Healthy Hibiscus Test ---")
    print("Image:", image_path.name)
    print("Predicted disease ID:", disease_id)
    print("Model score:", f"{confidence:.4f} ({confidence * 100:.2f}%)")

except Exception as error:
    print("\nPREDICTION FAILED")
    print(type(error).__name__ + ":", error)
