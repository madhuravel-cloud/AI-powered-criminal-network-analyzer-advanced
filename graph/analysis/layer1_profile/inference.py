import os
import joblib
import pandas as pd

from graph.analysis.layer1_profile.features import get_profile_features


# ============================================================
# PATH
# ============================================================

MODEL_PATH = (
    "graph/analysis/layer1_profile/"
    "layer1_profile_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
FEATURE_COLUMNS = model_data["features"]


# ============================================================
# LAYER 1 INFERENCE
# ============================================================

def analyze_profile(person_id, case_id):
    """
    Run Layer 1 Profile analysis for a person
    within a specific investigation case.

    Returns investigation relevance,
    NOT guilt or criminality.
    """

    # --------------------------------------------------------
    # Get features from Neo4j
    # --------------------------------------------------------

    features = get_profile_features(
        person_id,
        case_id
    )

    # --------------------------------------------------------
    # Create feature vector
    # --------------------------------------------------------

    feature_values = {
        feature: features.get(feature, 0)
        for feature in FEATURE_COLUMNS
    }

    X = pd.DataFrame(
        [feature_values],
        columns=FEATURE_COLUMNS
    )

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.fillna(0)

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(X)[0]

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(X)[0]

    class_probabilities = {
        int(class_label): float(probability)
        for class_label, probability
        in zip(
            model.classes_,
            probabilities
        )
    }

    relevance_score = class_probabilities.get(
        1,
        0.0
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = {
        "person_id": person_id,
        "case_id": case_id,

        "prediction": int(prediction),

        "relevance_score": round(
            relevance_score,
            4
        ),

        "label": (
            "RELEVANT"
            if prediction == 1
            else "LOW_RELEVANCE"
        ),

        "features": feature_values
    }

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    PERSON_ID = "person:ravi"
    CASE_ID = "case:FIR-101-2025"

    result = analyze_profile(
        PERSON_ID,
        CASE_ID
    )

    print("=" * 70)
    print("LAYER 1 PROFILE INFERENCE")
    print("=" * 70)

    print(
        f"Person : {result['person_id']}"
    )

    print(
        f"Case   : {result['case_id']}"
    )

    print(
        f"Prediction : {result['label']}"
    )

    print(
        f"Relevance Score : "
        f"{result['relevance_score']:.4f}"
    )

    print()
    print("Top profile features:")

    for key, value in result["features"].items():
        if value != 0:
            print(
                f"  {key:<30} {value}"
            )