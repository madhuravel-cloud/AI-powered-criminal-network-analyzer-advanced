import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ============================================================
# PATHS
# ============================================================

DATA_PATH = "data/layer1_profile_training_data.csv"
MODEL_PATH = "graph/analysis/layer1_profile/layer1_profile_model.pkl"


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "unique_connections",
    "total_relationships",
    "degree",
    "connected_people",
    "connected_phones",
    "connected_vehicles",
    "connected_locations",
    "connected_accounts",
    "connected_cases",
    "court_cases",
    "evidence_count",
    "fir_evidence_count",
    "cdr_evidence_count",
    "cctv_evidence_count",
    "vehicle_evidence_count",
    "court_evidence_count",
    "financial_evidence_count",
    "location_evidence_count",
    "source_layer_count",
    "relationship_type_count",
    "case_relationship_count",
    "cross_case_connections",
    "cdr_call_count",
    "cdr_unique_contacts",
    "cdr_total_duration",
    "cctv_observation_count",
    "cctv_unique_locations",
    "cctv_vehicle_links",
    "vehicle_links",
    "unique_vehicles",
    "location_links",
    "unique_locations",
    "financial_transaction_count",
    "financial_total_amount",
    "temporal_span_days",
]

TARGET_COLUMN = "relevance_label"


# ============================================================
# LOAD DATA
# ============================================================

def load_training_data():

    print("=" * 70)
    print("LOADING LAYER 1 TRAINING DATA")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    # Check required columns
    missing = [
        column
        for column in FEATURE_COLUMNS + [TARGET_COLUMN]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Convert features to numeric
    X = df[FEATURE_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce"
    )

    y = pd.to_numeric(
        df[TARGET_COLUMN],
        errors="coerce"
    )

    # Check missing values
    if X.isnull().any().any():
        missing_columns = X.columns[
            X.isnull().any()
        ].tolist()

        raise ValueError(
            f"Missing feature values in: {missing_columns}"
        )

    if y.isnull().any():
        raise ValueError(
            "Missing values found in relevance_label"
        )

    return X, y


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    X, y = load_training_data()

    print()
    print("Feature matrix:")
    print(f"X shape : {X.shape}")

    print()
    print("Label distribution:")
    print(y.value_counts().sort_index())

    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print()
    print("Dataset split:")
    print(f"Training : {len(X_train)}")
    print(f"Testing  : {len(X_test)}")

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        class_weight="balanced"
    )

    print()
    print("Training Layer 1 model...")

    model.fit(
        X_train,
        y_train
    )

    print("✅ Model training completed")

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print()
    print("=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)

    print(f"Accuracy : {accuracy:.4f}")

    print()
    print("Classification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # --------------------------------------------------------
    # Feature Importance
    # --------------------------------------------------------

    importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print()
    print("=" * 70)
    print("TOP FEATURE IMPORTANCE")
    print("=" * 70)

    print(
        importance.head(10).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Save Model
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(MODEL_PATH),
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "features": FEATURE_COLUMNS
        },
        MODEL_PATH
    )

    print()
    print("=" * 70)
    print("MODEL SAVED")
    print("=" * 70)

    print(
        f"Path : {MODEL_PATH}"
    )

    return model


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    train_model()