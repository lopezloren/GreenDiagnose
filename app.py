"""
GreenDiagnose - Flask application.
Species-specific CNN classification with a guided symptom questionnaire.
"""

import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load .env from the same folder as this file.
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_from_directory,
    session,
)

from db import fetch_all
from cnn_classifier import classify_image
from plant_gate import looks_like_species
from rule_engine import (
    get_questions_for_species,
    get_questions_for_diagnosis,
    compute_diagnosis,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        f"SECRET_KEY is missing. Check your .env file at: {ENV_FILE}"
    )

app.config["UPLOAD_FOLDER"] = str(BASE_DIR / "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Uploads are kept here only when the user ticks the consent box.
CONSENTED_FOLDER = BASE_DIR / "uploads" / "consented"

# Disease IDs that mean "Healthy", one per species.
HEALTHY_IDS = {2, 6, 9, 12, 15, 19, 22, 30, 36, 46}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# --- FRONTEND & PWA ROUTES ---


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    species_list = fetch_all(
        "SELECT id, common_name, scientific_name FROM plant_species"
    )
    return render_template("upload.html", species=species_list)


@app.route("/manifest.json")
def serve_manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/sw.js")
def serve_sw():
    return send_from_directory("static", "sw.js")


# --- BACKEND API ROUTES ---


@app.route("/api/species", methods=["GET"])
def get_species():
    species_list = fetch_all(
        "SELECT id, common_name, scientific_name FROM plant_species"
    )
    return jsonify({"species": species_list})


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return "No file uploaded.", 400

    file = request.files["file"]

    if not file.filename:
        return "No file selected.", 400

    if not allowed_file(file.filename):
        return (
            "Invalid file type. Please upload a PNG, JPG, or JPEG image.",
            400,
        )

    try:
        species_id = int(request.form.get("species_id", ""))
    except (TypeError, ValueError):
        return "Invalid plant species.", 400

    species = fetch_all(
        "SELECT id FROM plant_species WHERE id = %s",
        (species_id,),
    )

    if not species:
        return "Selected plant species was not found.", 400

    model_path = BASE_DIR / "models" / f"{species_id}.h5"
    mapping_path = BASE_DIR / "models" / f"{species_id}_classes.json"

    if not model_path.is_file() or not mapping_path.is_file():
        return render_template(
            "error.html",
            message=(
                "The AI model for this species is unavailable. "
                "Please try another species."
            ),
        ), 400

    original_filename = secure_filename(file.filename)

    if not original_filename or "." not in original_filename:
        return "Invalid filename.", 400

    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid4().hex}.{extension}"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        stored_filename,
    )

    # Keep the upload only if the user ticked the consent box.
    # Unticked or missing means the file is deleted after analysis.
    consent = request.form.get("consent_for_training") == "1"

    try:
        file.save(filepath)

        # Reject images that don't resemble the selected species.
        ok, _sim = looks_like_species(filepath, species_id)
        if not ok:
            session.pop("diagnosis", None)
            return render_template(
                "error.html",
                message=(
                    "This image does not look like the selected plant. "
                    "Please check the species and upload a clear leaf photo."
                ),
            ), 400

        # classify_image returns the top disease ID, its confidence,
        # and a {disease_id: probability} dict for every class.
        predicted_disease_id, cnn_confidence, cnn_scores = classify_image(
            filepath,
            species_id,
        )

        disease = fetch_all(
            """
            SELECT id
            FROM disease
            WHERE id = %s AND species_id = %s
            """,
            (predicted_disease_id, species_id),
        )

        if not disease:
            session.pop("diagnosis", None)
            return (
                "The model returned an invalid disease mapping. "
                "Please contact the system administrator.",
                500,
            )

        # Store the CNN prediction and all class probabilities in
        # Flask's signed session. JSON keys become strings.
        session["diagnosis"] = {
            "species_id": species_id,
            "cnn_disease_id": int(predicted_disease_id),
            "cnn_confidence": float(cnn_confidence),
            "cnn_scores": {
                str(int(k)): float(v) for k, v in cnn_scores.items()
            },
            "filename": stored_filename,
        }

        # Healthy or low/moderate confidence: use all species questions.
        # High confidence: prioritize questions for the predicted disease.
        if cnn_confidence < 0.8 or int(predicted_disease_id) in HEALTHY_IDS:
            questions = get_questions_for_species(species_id)
        else:
            questions = get_questions_for_diagnosis(
                species_id,
                predicted_disease_id,
            )

        # Safety fallback for diseases without symptom rules.
        if not questions:
            questions = get_questions_for_species(species_id)

    except Exception:
        app.logger.exception("Image classification failed.")
        session.pop("diagnosis", None)
        return (
            "The image could not be analyzed. Please try another image.",
            500,
        )

    finally:
        # Delete the upload unless the user consented to keep it.
        # The result page does not need the file.
        if os.path.exists(filepath):
            if consent:
                os.makedirs(CONSENTED_FOLDER, exist_ok=True)
                os.replace(
                    filepath,
                    CONSENTED_FOLDER / os.path.basename(filepath),
                )
            else:
                os.remove(filepath)

    return render_template(
        "questionnaire.html",
        species_id=species_id,
        filename=stored_filename,
        questions=questions,
    )


@app.route("/result", methods=["POST"])
def result():
    # Never trust CNN prediction values submitted by the browser.
    diagnosis_session = session.get("diagnosis")

    if not diagnosis_session:
        return (
            "Your diagnosis session has expired. "
            "Please upload your image again.",
            400,
        )

    species_id = diagnosis_session["species_id"]
    cnn_disease_id = diagnosis_session["cnn_disease_id"]
    cnn_confidence = diagnosis_session["cnn_confidence"]

    # Convert stored string keys back to integer disease IDs.
    cnn_scores = {
        int(k): float(v)
        for k, v in diagnosis_session.get("cnn_scores", {}).items()
    }

    # Read and validate questionnaire answers.
    answers = []

    for key, value in request.form.items():
        if not key.startswith("symptom_"):
            continue

        try:
            symptom_id = int(key.split("_", 1)[1])
        except ValueError:
            return "Invalid symptom ID.", 400

        if value not in ("yes", "no"):
            return "Invalid symptom answer.", 400

        answers.append(
            {
                "symptom_id": symptom_id,
                "answer_value": value,
            }
        )

    if not answers:
        return "Please answer the symptom questions.", 400

    try:
        # Ensure submitted symptoms belong to the selected species.
        valid_symptoms = fetch_all(
            "SELECT id FROM symptom WHERE species_id = %s",
            (species_id,),
        )

        valid_symptom_ids = {
            int(row["id"]) for row in valid_symptoms
        }

        if any(
            answer["symptom_id"] not in valid_symptom_ids
            for answer in answers
        ):
            return (
                "A submitted symptom does not belong to this species.",
                400,
            )

        diagnoses = compute_diagnosis(
            species_id,
            cnn_disease_id,
            cnn_confidence,
            answers,
            cnn_scores,
        )

        if not diagnoses:
            return "No diagnoses are available for this species.", 404

        top_result = diagnoses[0]

        # Format each score separately.
        cnn_score_display = f"{top_result['cnn_score'] * 100:.1f}%"
        symptom_score_display = (
            f"{top_result['symptom_score'] * 100:.1f}%"
        )

        combined_score_display = (
            f"{top_result['confidence'] * 100:.1f}%"
        )

        confidence_note = (
            "The image model is not confident about this plant. "
            "Check that the correct species was selected."
            if top_result["cnn_score"] < 0.5
            else (
                "Low combined ranking score. Consider expert review."
                if top_result.get("is_low_confidence")
                else ""
            )
        )

        treatments = [top_result["treatment"]]

        response = render_template(
            "result.html",
            diagnosis=top_result["disease_name"],
            cnn_score=cnn_score_display,
            symptom_score=symptom_score_display,
            confidence=combined_score_display,
            confidence_note=confidence_note,
            treatments=treatments,
        )

        # Clear the stored prediction after a successful result.
        session.pop("diagnosis", None)

        return response

    except Exception:
        app.logger.exception("Diagnosis result generation failed.")
        return (
            "Unable to generate the diagnosis. Please try again.",
            500,
        )


# --- SERVER STARTUP ---


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)