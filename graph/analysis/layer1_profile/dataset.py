import csv
import os

from database.neo4j_connection import driver
from graph.analysis.layer1_profile.features import get_profile_features


OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "layer1_profile_features.csv"
)


def get_all_people():
    """
    Retrieve every Person node from the Neo4j master graph.
    """

    with driver.session() as session:

        result = session.run(
            """
            MATCH (p:Person)
            RETURN p.canonical_id AS canonical_id
            ORDER BY p.canonical_id
            """
        )

        return [
            record["canonical_id"]
            for record in result
        ]


def build_dataset():

    people = get_all_people()

    if not people:
        raise RuntimeError(
            "No Person nodes found in Neo4j."
        )

    print("=" * 60)
    print("LAYER 1 — PROFILE FEATURE DATASET GENERATOR")
    print("=" * 60)

    print(f"\nPeople found: {len(people)}")

    rows = []

    for index, person_id in enumerate(people, start=1):

        try:

            result = get_profile_features(person_id)

            target = result["target"]
            features = result["features"]

            row = {
                "canonical_id": target["canonical_id"],
                "name": target["name"],
                "entity_type": target["entity_type"],

                "unique_connections":
                    features["unique_connections"],

                "total_relationships":
                    features["total_relationships"],

                "degree":
                    features["degree"],

                "connected_people":
                    features["connected_people"],

                "connected_phones":
                    features["connected_phones"],

                "connected_vehicles":
                    features["connected_vehicles"],

                "connected_locations":
                    features["connected_locations"],

                "connected_accounts":
                    features["connected_accounts"],

                "connected_cases":
                    features["connected_cases"],

                "court_cases":
                    features["court_cases"],

                "evidence_count":
                    features["evidence_count"],

                "fir_evidence_count":
                    features["fir_evidence_count"],

                "cdr_evidence_count":
                    features["cdr_evidence_count"],

                "cctv_evidence_count":
                    features["cctv_evidence_count"],

                "vehicle_evidence_count":
                    features["vehicle_evidence_count"],

                "court_evidence_count":
                    features["court_evidence_count"],

                "financial_evidence_count":
                    features["financial_evidence_count"],

                "location_evidence_count":
                    features["location_evidence_count"],

                "source_layer_count":
                    features["source_layer_count"],

                "relationship_type_count":
                    features["relationship_type_count"],
            }

            rows.append(row)

            print(
                f"[{index:02}/{len(people)}] "
                f"{target['name']:15} "
                f"✓"
            )

        except Exception as e:

            print(
                f"[{index:02}/{len(people)}] "
                f"{person_id:25} "
                f"❌ {e}"
            )

    if not rows:
        raise RuntimeError(
            "No feature rows were generated."
        )

    # =========================================================
    # CREATE OUTPUT DIRECTORY
    # =========================================================

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # =========================================================
    # CSV COLUMNS
    # =========================================================

    fieldnames = [
        "canonical_id",
        "name",
        "entity_type",

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
    ]

    # =========================================================
    # WRITE CSV
    # =========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    # =========================================================
    # SUMMARY
    # =========================================================

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)

    print(f"\nRows generated : {len(rows)}")
    print(f"Features       : {len(fieldnames) - 3}")
    print(f"Output file    : {OUTPUT_FILE}")

    print("\nFeature columns:")

    for column in fieldnames[3:]:
        print(f"  • {column}")

    print("\n✅ Layer 1 feature dataset created")


if __name__ == "__main__":

    try:
        build_dataset()

    finally:
        driver.close()