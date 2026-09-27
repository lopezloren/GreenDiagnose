"""
rule_engine.py - GreenDiagnose's forward-chaining, certainty-factor inference engine.

This is real, runnable logic - not a stub. It works as soon as your
disease/symptom/disease_symptom_rule tables have real data in them
(from your team's rule-drafting + horticulturist validation work).

Core idea (certainty-factor model, same lineage as Shortliffe & Buchanan's
MYCIN - see your Chapter 1 RRL, reference [26]):
  - Each disease has a set of symptoms, each with a certainty_weight (0.0-1.0)
    representing how strongly a "yes" answer indicates that disease.
  - A disease's rule-based score = sum of certainty_weight for every
    symptom the user answered "yes" to.
  - The CNN's prediction is treated as an additional weighted input,
    not a separate parallel answer - this is the "sequential staging"
    design from your Chapter 2 architecture.
"""

from db import fetch_all

# How much weight the CNN's own confidence carries in the final score,
# relative to the summed rule-based symptom score. Tune this during
# your Sprint 4 (Expert Validation) based on real test cases - document
# whatever value you land on, and why, in your Chapter 3 methodology.
CNN_WEIGHT = 0.5
RULE_WEIGHT = 0.5

# Below this combined confidence, the UI should show the result as
# "low confidence" per your Scope's fallback-handling design.
LOW_CONFIDENCE_THRESHOLD = 0.4


def get_questions_for_species(species_id):
    """
    Returns the guided questionnaire questions for this species,
    ordered for display. Used by the /api/session/<id>/questions route.
    """
    query = """
        SELECT id, question_text, answer_type, display_order
        FROM symptom
        WHERE species_id = %s
        ORDER BY display_order ASC
    """
    return fetch_all(query, (species_id,))


def compute_diagnosis(species_id, predicted_disease_id, cnn_confidence, answers):
    """
    Combines the CNN's prediction with questionnaire answers to produce
    a ranked list of candidate diagnoses for this species.

    Args:
        species_id: int
        predicted_disease_id: int or None - the CNN's top guess
        cnn_confidence: float (0.0-1.0) or None
        answers: list of dicts like [{"symptom_id": 3, "answer_value": "yes"}, ...]

    Returns:
        list of dicts, sorted by score descending:
        [{"disease_id": ..., "disease_name": ..., "confidence": ..., "treatment": ...}, ...]
    """
    # Only "yes" answers contribute positive certainty in this basic model.
    # Extend this if your team wants "no" answers to count as negative
    # evidence against a disease - a reasonable Sprint 3/4 refinement.
    yes_symptom_ids = [
        a["symptom_id"] for a in answers if a.get("answer_value") == "yes"
    ]

    # Pull every disease for this species, along with the sum of
    # certainty_weight for any of its rules that matched a "yes" answer.
    query = """
        SELECT
            d.id AS disease_id,
            d.name AS disease_name,
            COALESCE(SUM(
                CASE WHEN dsr.symptom_id IN ({placeholders})
                     THEN dsr.certainty_weight ELSE 0 END
            ), 0) AS rule_score
        FROM disease d
        LEFT JOIN disease_symptom_rule dsr ON dsr.disease_id = d.id
        WHERE d.species_id = %s
        GROUP BY d.id, d.name
    """
    if yes_symptom_ids:
        placeholders = ",".join(["%s"] * len(yes_symptom_ids))
        query = query.format(placeholders=placeholders)
        params = tuple(yes_symptom_ids) + (species_id,)
    else:
        # No symptoms answered "yes" - still return diseases with 0 rule_score
        query = query.format(placeholders="NULL")
        params = (species_id,)

    candidates = fetch_all(query, params)

    # Normalize rule_score to 0-1 range relative to the highest-scoring
    # candidate, so it's comparable to the CNN's 0-1 confidence.
    max_rule_score = max((c["rule_score"] for c in candidates), default=0) or 1

    results = []
    for c in candidates:
        normalized_rule_score = float(c["rule_score"]) / float(max_rule_score)

        # If this disease is the CNN's predicted one, blend both signals.
        # Otherwise, it's scored on rule evidence alone.
        if predicted_disease_id and int(c["disease_id"]) == int(predicted_disease_id) and cnn_confidence:
            combined_score = (CNN_WEIGHT * float(cnn_confidence)) + (RULE_WEIGHT * normalized_rule_score)
        else:
            combined_score = RULE_WEIGHT * normalized_rule_score

        results.append({
            "disease_id": c["disease_id"],
            "disease_name": c["disease_name"],
            "confidence": round(combined_score, 4)
        })

    results.sort(key=lambda r: r["confidence"], reverse=True)

    print(f"DEBUG: Final candidate scores: {results}")
    # Attach treatment text and a low-confidence flag to the top result
    if results:
        results[0]["is_low_confidence"] = results[0]["confidence"] < LOW_CONFIDENCE_THRESHOLD
        results[0]["treatment"] = get_treatment(results[0]["disease_id"])

    return results


def get_treatment(disease_id):
    """Fetches the care/treatment recommendation text for a diagnosed disease."""
    query = "SELECT recommendation_text FROM treatment WHERE disease_id = %s LIMIT 1"
    rows = fetch_all(query, (disease_id,))
    return rows[0]["recommendation_text"] if rows else "No treatment recorded for this condition yet."
