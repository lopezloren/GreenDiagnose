"""GreenDiagnose diagnosis and adaptive questionnaire rules."""

import re

from db import fetch_all

CNN_WEIGHT = 0.5
RULE_WEIGHT = 0.5
LOW_CONFIDENCE_THRESHOLD = 0.4

# A disease needs at least this CNN probability to be ranked first.
# Provisional value; confirm after held-out evaluation and expert review.
MIN_CNN_SUPPORT = 0.2

CITE_PATTERN = re.compile(r"\s*\[cite:\s*\d+\]")


def get_questions_for_species(species_id):
    """Fetch all symptom questions for a plant species."""
    query = """
        SELECT id, question_text, answer_type, display_order
        FROM symptom
        WHERE species_id = %s
        ORDER BY display_order, id
    """
    return fetch_all(query, (species_id,))


def get_questions_for_diagnosis(species_id, predicted_disease_id):
    """Return predicted-disease questions first, then alternatives."""
    query = """
        SELECT DISTINCT
            s.id,
            s.question_text,
            s.answer_type,
            s.display_order,
            CASE
                WHEN dsr.disease_id = %s THEN 0
                ELSE 1
            END AS priority
        FROM symptom s
        JOIN disease_symptom_rule dsr
            ON dsr.symptom_id = s.id
        JOIN disease d
            ON d.id = dsr.disease_id
        WHERE s.species_id = %s
          AND d.species_id = %s
        ORDER BY priority, s.display_order, s.id
    """
    return fetch_all(
        query,
        (predicted_disease_id, species_id, species_id),
    )


def get_species_diseases(species_id):
    """Return every disease for a species, including those without rules."""
    return fetch_all(
        "SELECT id, name FROM disease WHERE species_id = %s ORDER BY id",
        (species_id,),
    )


def symptom_scores_for_species(species_id, answers):
    """
    Symptom support per disease, combining Yes answers so the score
    rises with diminishing returns and never exceeds 1.0.
    score = 1 - product(1 - weight) over the Yes answers.
    No answers add no support.
    """
    rules = fetch_all(
        """
        SELECT dsr.disease_id, dsr.symptom_id, dsr.certainty_weight
        FROM disease_symptom_rule dsr
        JOIN disease d ON d.id = dsr.disease_id
        WHERE d.species_id = %s
        """,
        (species_id,),
    )

    yes_ids = {
        int(a["symptom_id"]) for a in answers
        if a.get("answer_value") == "yes"
    }

    remaining = {}  # disease_id -> product of (1 - weight)
    for rule in rules:
        if int(rule["symptom_id"]) not in yes_ids:
            continue
        disease_id = int(rule["disease_id"])
        weight = float(rule["certainty_weight"])
        remaining[disease_id] = remaining.get(disease_id, 1.0) * (1.0 - weight)

    return {
        disease_id: 1.0 - product
        for disease_id, product in remaining.items()
    }


def compute_diagnosis(
    species_id,
    predicted_disease_id,
    cnn_confidence,
    answers,
    cnn_scores=None,
):
    """
    Rank every disease for the species using:
      - CNN probability for each class,
      - per-disease symptom agreement,
    and rank CNN-supported diseases above unsupported ones.
    """
    diseases = get_species_diseases(species_id)

    if not diseases:
        return []

    symptom = symptom_scores_for_species(species_id, answers)

    # Healthy has no symptom rules. Its support is the absence of
    # disease symptoms: 1 minus the strongest disease symptom score.
    healthy_id = next(
        (
            int(d["id"])
            for d in diseases
            if str(d["name"]).strip().lower() == "healthy"
        ),
        None,
    )

    if healthy_id is not None:
        disease_only = [
            score for disease_id, score in symptom.items()
            if disease_id != healthy_id
        ]
        symptom[healthy_id] = 0.5 * (1.0 - max(disease_only, default=0.0))

    # Full probability per class, e.g. {20: 0.076, 22: 0.901, 21: 0.023}.
    all_cnn_scores = {
        int(k): float(v) for k, v in (cnn_scores or {}).items()
    }

    # Fallback for callers that only pass the top class.
    if not all_cnn_scores and predicted_disease_id is not None:
        all_cnn_scores = {
            int(predicted_disease_id): float(cnn_confidence or 0.0)
        }

    results = []

    for disease in diseases:
        disease_id = int(disease["id"])

        symptom_score = max(0.0, min(1.0, symptom.get(disease_id, 0.0)))
        cnn_score = max(
            0.0,
            min(1.0, all_cnn_scores.get(disease_id, 0.0)),
        )

        combined_score = (
            CNN_WEIGHT * cnn_score + RULE_WEIGHT * symptom_score
        )

        results.append({
            "disease_id": disease_id,
            "disease_name": disease["name"],
            "cnn_score": round(cnn_score, 4),
            "symptom_score": round(symptom_score, 4),
            "confidence": round(combined_score, 4),
        })

    # CNN-supported diseases rank above unsupported ones.
    # Within each group, sort by combined score.
    results.sort(
        key=lambda item: (
            item["cnn_score"] >= MIN_CNN_SUPPORT,
            item["confidence"],
        ),
        reverse=True,
    )

    if results:
        results[0]["is_low_confidence"] = (
            results[0]["confidence"] < LOW_CONFIDENCE_THRESHOLD
        )
        results[0]["treatment"] = get_treatment(
            results[0]["disease_id"]
        )

    return results


def get_treatment(disease_id):
    """Fetch the care recommendation, with citation markers removed."""
    rows = fetch_all(
        """
        SELECT recommendation_text
        FROM treatment
        WHERE disease_id = %s
        LIMIT 1
        """,
        (disease_id,),
    )

    if not rows:
        return "No treatment recorded for this condition yet."

    text = CITE_PATTERN.sub("", rows[0]["recommendation_text"]).strip()

    return text or "Source pending expert review."