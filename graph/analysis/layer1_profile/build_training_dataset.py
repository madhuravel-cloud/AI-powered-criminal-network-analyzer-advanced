import pandas as pd

from graph.analysis.layer1_profile.features import get_profile_features


INPUT_PATH = "data/layer1_profile_manual_training_data.csv"
OUTPUT_PATH = "data/layer1_profile_training_data.csv"


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


def main():

    print("=" * 70)
    print("BUILDING LAYER 1 TRAINING DATASET")
    print("=" * 70)

    df = pd.read_csv(INPUT_PATH)

    print(f"Manual rows : {len(df)}")

    for index, row in df.iterrows():

        print(
            f"[{index + 1}/{len(df)}] "
            f"{row['fir_number']} -> {row['person_name']}"
        )

        features = get_profile_features(
            row["person_id"],
            row["case_id"]
        )

        for feature in FEATURE_COLUMNS:
            df.loc[index, feature] = features.get(
                feature,
                0
            )

    # Convert feature columns to numeric
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Check for missing values
    missing = df[FEATURE_COLUMNS].isnull().sum()

    missing = missing[missing > 0]

    if len(missing) > 0:

        print("\n❌ Missing feature values:")
        print(missing)

        raise ValueError(
            "Training dataset still contains missing features."
        )

    # Save actual ML dataset
    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("=" * 70)
    print("TRAINING DATASET CREATED")
    print("=" * 70)

    print(f"Rows     : {len(df)}")
    print(f"Features : {len(FEATURE_COLUMNS)}")
    print(f"Columns  : {len(df.columns)}")

    print()
    print("Label distribution:")
    print(
        df["relevance_label"]
        .value_counts()
        .sort_index()
    )

    print()
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()