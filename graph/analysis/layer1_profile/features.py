from database.neo4j_connection import driver


# ============================================================
# LAYER 1 — PROFILE FEATURE EXTRACTION
# ============================================================
#
# Purpose:
#   Extract investigation-specific profile features for a person
#   from the Neo4j Master Temporal Multilayer Graph.
#
# Important:
#   These scores/features represent INVESTIGATION RELEVANCE.
#   They do NOT represent guilt or criminality.
#
# Case-aware:
#   When case_id is supplied, relationship/evidence features are
#   calculated primarily from that investigation context.
#
# Global:
#   Some profile features such as connected_cases and historical
#   cross-case connections use the complete graph.
# ============================================================


def _safe_int(value):
    """Convert Neo4j numeric result to int safely."""
    return int(value or 0)


def _safe_float(value):
    """Convert Neo4j numeric result to float safely."""
    return float(value or 0.0)


def get_profile_features(canonical_id, case_id=None):

    with driver.session() as session:

        # ====================================================
        # 1. TARGET ENTITY
        # ====================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            RETURN
                p.canonical_id AS canonical_id,
                p.name AS name,
                p.entity_type AS entity_type,
                labels(p) AS labels
            """,
            canonical_id=canonical_id
        )

        target = result.single()

        if target is None:
            raise ValueError(
                f"Entity not found in Neo4j: {canonical_id}"
            )

        # ====================================================
        # 2. RELATIONSHIP FEATURES
        # ====================================================

        if case_id:

            result = session.run(
                """
                MATCH (p {canonical_id: $canonical_id})

                OPTIONAL MATCH
                    (p)-[r:RELATED]-(x)

                WHERE
                    r.case_id = $case_id

                RETURN
                    count(r) AS total_relationships,

                    count(DISTINCT x)
                        AS unique_connections,

                    count(
                        DISTINCT CASE
                            WHEN x:Person THEN x
                        END
                    ) AS connected_people,

                    count(
                        DISTINCT CASE
                            WHEN x:Phone THEN x
                        END
                    ) AS connected_phones,

                    count(
                        DISTINCT CASE
                            WHEN x:Vehicle THEN x
                        END
                    ) AS connected_vehicles,

                    count(
                        DISTINCT CASE
                            WHEN x:Location THEN x
                        END
                    ) AS connected_locations,

                    count(
                        DISTINCT CASE
                            WHEN x:Account THEN x
                        END
                    ) AS connected_accounts
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH (p {canonical_id: $canonical_id})

                OPTIONAL MATCH
                    (p)-[r:RELATED]-(x)

                RETURN
                    count(r) AS total_relationships,

                    count(DISTINCT x)
                        AS unique_connections,

                    count(
                        DISTINCT CASE
                            WHEN x:Person THEN x
                        END
                    ) AS connected_people,

                    count(
                        DISTINCT CASE
                            WHEN x:Phone THEN x
                        END
                    ) AS connected_phones,

                    count(
                        DISTINCT CASE
                            WHEN x:Vehicle THEN x
                        END
                    ) AS connected_vehicles,

                    count(
                        DISTINCT CASE
                            WHEN x:Location THEN x
                        END
                    ) AS connected_locations,

                    count(
                        DISTINCT CASE
                            WHEN x:Account THEN x
                        END
                    ) AS connected_accounts
                """,
                canonical_id=canonical_id
            )

        stats = result.single()

        if stats is None:
            raise ValueError(
                f"Could not calculate relationship statistics "
                f"for {canonical_id}"
            )

        total_relationships = _safe_int(
            stats["total_relationships"]
        )

        unique_connections = _safe_int(
            stats["unique_connections"]
        )

        connected_people = _safe_int(
            stats["connected_people"]
        )

        connected_phones = _safe_int(
            stats["connected_phones"]
        )

        connected_vehicles = _safe_int(
            stats["connected_vehicles"]
        )

        connected_locations = _safe_int(
            stats["connected_locations"]
        )

        connected_accounts = _safe_int(
            stats["connected_accounts"]
        )

        degree = total_relationships

        # ====================================================
        # 3. CONNECTED CASES
        # ====================================================
        #
        # A person can be connected to a case directly OR through
        # Evidence.
        # ====================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH
                (p)-[]-(direct_case:Case)

            WITH
                p,
                collect(DISTINCT direct_case) AS direct_cases

            OPTIONAL MATCH
                (p)-[]-(e:Evidence)-[]-(evidence_case:Case)

            WITH
                direct_cases,
                collect(DISTINCT evidence_case)
                    AS evidence_cases

            UNWIND
                (direct_cases + evidence_cases)
                AS c

            WITH DISTINCT c

            WHERE c IS NOT NULL

            RETURN
                count(c) AS connected_cases
            """,
            canonical_id=canonical_id
        )

        row = result.single()

        connected_cases = (
            _safe_int(row["connected_cases"])
            if row is not None
            else 0
        )

        # ====================================================
        # 4. COURT CASES
        # ====================================================

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (cc:CourtCase)

                WHERE
                    r.case_id = $case_id

                RETURN
                    count(DISTINCT cc)
                        AS court_cases
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (cc:CourtCase)

                RETURN
                    count(DISTINCT cc)
                        AS court_cases
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        court_cases = (
            _safe_int(row["court_cases"])
            if row is not None
            else 0
        )

        # ====================================================
        # 5. TARGET-SPECIFIC EVIDENCE
        # ====================================================

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[]-
                    (e:Evidence)
                    -[]-
                    (c:Case)

                WHERE
                    c.id = $case_id

                RETURN
                    count(DISTINCT e) AS evidence_count
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[]-
                    (e:Evidence)

                RETURN
                    count(DISTINCT e) AS evidence_count
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        evidence_count = (
            _safe_int(row["evidence_count"])
            if row is not None
            else 0
        )

        # ====================================================
        # 6. SOURCE-SPECIFIC EVIDENCE
        # ====================================================
        #
        # Evidence is counted using evidence_type.
        # This is more reliable than assuming every Evidence
        # relationship contains source_layer.
        # ====================================================

        evidence_counts = {
            "FIR_DOCUMENT": 0,
            "CDR_FILE": 0,
            "CCTV_VIDEO": 0,
            "VEHICLE_RECORD": 0,
            "COURT_DOCUMENT": 0,
            "BANK_TRANSACTION_FILE": 0,
            "LOCATION_RECORD": 0,
        }

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[]-
                    (e:Evidence)
                    -[]-
                    (c:Case)

                WHERE
                    c.id = $case_id

                RETURN DISTINCT
                    e.id AS evidence_id,
                    e.evidence_type AS evidence_type
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[]-
                    (e:Evidence)

                RETURN DISTINCT
                    e.id AS evidence_id,
                    e.evidence_type AS evidence_type
                """,
                canonical_id=canonical_id
            )

        seen_evidence = set()

        for record in result:

            evidence_id = record["evidence_id"]
            evidence_type = record["evidence_type"]

            if evidence_id in seen_evidence:
                continue

            seen_evidence.add(evidence_id)

            if evidence_type in evidence_counts:
                evidence_counts[evidence_type] += 1

        fir_evidence_count = evidence_counts["FIR_DOCUMENT"]
        cdr_evidence_count = evidence_counts["CDR_FILE"]
        cctv_evidence_count = evidence_counts["CCTV_VIDEO"]
        vehicle_evidence_count = evidence_counts["VEHICLE_RECORD"]
        court_evidence_count = evidence_counts["COURT_DOCUMENT"]
        financial_evidence_count = evidence_counts[
            "BANK_TRANSACTION_FILE"
        ]
        location_evidence_count = evidence_counts[
            "LOCATION_RECORD"
        ]

        # ====================================================
        # 7. SOURCE LAYER COUNT
        # ====================================================

        source_layers = set()

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id
                    AND r.source_layer IS NOT NULL

                RETURN DISTINCT
                    r.source_layer AS source_layer
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.source_layer IS NOT NULL

                RETURN DISTINCT
                    r.source_layer AS source_layer
                """,
                canonical_id=canonical_id
            )

        for record in result:

            source_layer = record["source_layer"]

            if source_layer:
                source_layers.add(source_layer)

        # Also include source layers represented by evidence.
        evidence_layer_map = {
            "FIR_DOCUMENT": "FIR",
            "CDR_FILE": "CDR",
            "CCTV_VIDEO": "CCTV",
            "VEHICLE_RECORD": "VEHICLE",
            "COURT_DOCUMENT": "COURT",
            "BANK_TRANSACTION_FILE": "FINANCIAL",
            "LOCATION_RECORD": "LOCATION",
        }

        for evidence_type, count in evidence_counts.items():

            if count > 0:
                source_layer = evidence_layer_map.get(
                    evidence_type
                )

                if source_layer:
                    source_layers.add(source_layer)

        source_layer_count = len(source_layers)

        # ====================================================
        # 8. RELATIONSHIP TYPE COUNT
        # ====================================================

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id
                    AND r.relationship_type IS NOT NULL

                RETURN DISTINCT
                    r.relationship_type AS relationship_type
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.relationship_type IS NOT NULL

                RETURN DISTINCT
                    r.relationship_type AS relationship_type
                """,
                canonical_id=canonical_id
            )

        relationship_types = set()

        for record in result:

            relationship_type = record["relationship_type"]

            if relationship_type:
                relationship_types.add(
                    relationship_type
                )

        relationship_type_count = len(
            relationship_types
        )

        # ====================================================
        # 9. CASE RELATIONSHIP COUNT
        # ====================================================

        case_relationship_count = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id

                RETURN
                    count(r) AS case_relationship_count
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

            row = result.single()

            if row is not None:
                case_relationship_count = _safe_int(
                    row["case_relationship_count"]
                )

        # ====================================================
        # 10. CROSS-CASE CONNECTIONS
        # ====================================================

        cross_case_connections = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id IS NOT NULL
                    AND r.case_id <> $case_id

                RETURN
                    count(DISTINCT x)
                        AS cross_case_connections
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

            row = result.single()

            if row is not None:
                cross_case_connections = _safe_int(
                    row["cross_case_connections"]
                )

        # ====================================================
        # 11. CDR CALL COUNT
        # ====================================================

        cdr_call_count = 0
        cdr_unique_contacts = 0
        cdr_total_duration = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[pr:RELATED]-
                    (phone:Phone)

                WHERE
                    pr.relationship_type = "USES_PHONE"

                MATCH
                    (phone)-[cdr:RELATED]-
                    (other:Phone)

                WHERE
                    cdr.relationship_type = "CDR_CALL"
                    AND cdr.case_id = $case_id

                RETURN
                    count(cdr) AS call_count,

                    count(DISTINCT other)
                        AS unique_contacts,

                    coalesce(
                        sum(cdr.duration_seconds),
                        0
                    ) AS total_duration
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[pr:RELATED]-
                    (phone:Phone)

                WHERE
                    pr.relationship_type = "USES_PHONE"

                MATCH
                    (phone)-[cdr:RELATED]-
                    (other:Phone)

                WHERE
                    cdr.relationship_type = "CDR_CALL"

                RETURN
                    count(cdr) AS call_count,

                    count(DISTINCT other)
                        AS unique_contacts,

                    coalesce(
                        sum(cdr.duration_seconds),
                        0
                    ) AS total_duration
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            cdr_call_count = _safe_int(
                row["call_count"]
            )

            cdr_unique_contacts = _safe_int(
                row["unique_contacts"]
            )

            cdr_total_duration = _safe_int(
                row["total_duration"]
            )

        # ====================================================
        # 12. CCTV OBSERVATIONS
        # ====================================================

        cctv_observation_count = 0
        cctv_unique_locations = 0
        cctv_vehicle_links = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id
                    AND r.relationship_type =
                        "CCTV_OBSERVED_AT"

                RETURN
                    count(r) AS observation_count,

                    count(DISTINCT x)
                        AS unique_locations
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.relationship_type =
                        "CCTV_OBSERVED_AT"

                RETURN
                    count(r) AS observation_count,

                    count(DISTINCT x)
                        AS unique_locations
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            cctv_observation_count = _safe_int(
                row["observation_count"]
            )

            cctv_unique_locations = _safe_int(
                row["unique_locations"]
            )

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (v:Vehicle)

                WHERE
                    r.relationship_type =
                        "CCTV_ASSOCIATED_VEHICLE"
                    AND r.case_id = $case_id

                RETURN
                    count(r) AS vehicle_links
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (v:Vehicle)

                WHERE
                    r.relationship_type =
                        "CCTV_ASSOCIATED_VEHICLE"

                RETURN
                    count(r) AS vehicle_links
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:
            cctv_vehicle_links = _safe_int(
                row["vehicle_links"]
            )

        # ====================================================
        # 13. VEHICLE FEATURES
        # ====================================================

        vehicle_links = 0
        unique_vehicles = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (v:Vehicle)

                WHERE
                    r.case_id = $case_id
                    AND (
                        r.relationship_type =
                            "ASSOCIATED_WITH_VEHICLE"
                        OR
                        r.relationship_type =
                            "CCTV_ASSOCIATED_VEHICLE"
                    )

                RETURN
                    count(r) AS vehicle_links,

                    count(DISTINCT v)
                        AS unique_vehicles
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (v:Vehicle)

                WHERE
                    r.relationship_type =
                        "ASSOCIATED_WITH_VEHICLE"
                    OR
                    r.relationship_type =
                        "CCTV_ASSOCIATED_VEHICLE"

                RETURN
                    count(r) AS vehicle_links,

                    count(DISTINCT v)
                        AS unique_vehicles
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            vehicle_links = _safe_int(
                row["vehicle_links"]
            )

            unique_vehicles = _safe_int(
                row["unique_vehicles"]
            )

        # ====================================================
        # 14. LOCATION FEATURES
        # ====================================================

        location_links = 0
        unique_locations = 0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (l:Location)

                WHERE
                    r.case_id = $case_id

                RETURN
                    count(r) AS location_links,

                    count(DISTINCT l)
                        AS unique_locations
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (l:Location)

                RETURN
                    count(r) AS location_links,

                    count(DISTINCT l)
                        AS unique_locations
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            location_links = _safe_int(
                row["location_links"]
            )

            unique_locations = _safe_int(
                row["unique_locations"]
            )

        # ====================================================
        # 15. FINANCIAL FEATURES
        # ====================================================

        financial_transaction_count = 0
        financial_total_amount = 0.0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id
                    AND r.relationship_type =
                        "FINANCIAL_TRANSFER"

                RETURN
                    count(r)
                        AS transaction_count,

                    coalesce(
                        sum(r.amount),
                        0.0
                    ) AS total_amount
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.relationship_type =
                        "FINANCIAL_TRANSFER"

                RETURN
                    count(r)
                        AS transaction_count,

                    coalesce(
                        sum(r.amount),
                        0.0
                    ) AS total_amount
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            financial_transaction_count = _safe_int(
                row["transaction_count"]
            )

            financial_total_amount = _safe_float(
                row["total_amount"]
            )

        # ====================================================
        # 16. TEMPORAL FEATURES
        # ====================================================

        earliest_timestamp = None
        latest_timestamp = None
        temporal_span_days = 0.0

        if case_id:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.case_id = $case_id
                    AND r.timestamp IS NOT NULL

                RETURN
                    min(r.timestamp) AS earliest,

                    max(r.timestamp) AS latest
                """,
                canonical_id=canonical_id,
                case_id=case_id
            )

        else:

            result = session.run(
                """
                MATCH
                    (p {canonical_id: $canonical_id})
                    -[r:RELATED]-
                    (x)

                WHERE
                    r.timestamp IS NOT NULL

                RETURN
                    min(r.timestamp) AS earliest,

                    max(r.timestamp) AS latest
                """,
                canonical_id=canonical_id
            )

        row = result.single()

        if row is not None:

            earliest_timestamp = row["earliest"]
            latest_timestamp = row["latest"]

            if (
                earliest_timestamp is not None
                and latest_timestamp is not None
            ):

                try:

                    delta = (
                        latest_timestamp
                        - earliest_timestamp
                    )

                    temporal_span_days = max(
                        0.0,
                        delta.total_seconds() / 86400.0
                    )

                except Exception:

                    temporal_span_days = 0.0

        # ====================================================
        # 17. FINAL FEATURE VECTOR
        # ====================================================

        features = {

            # -----------------------------
            # Profile / relationship
            # -----------------------------

            "unique_connections":
                unique_connections,

            "total_relationships":
                total_relationships,

            "degree":
                degree,

            "connected_people":
                connected_people,

            "connected_phones":
                connected_phones,

            "connected_vehicles":
                connected_vehicles,

            "connected_locations":
                connected_locations,

            "connected_accounts":
                connected_accounts,

            "connected_cases":
                connected_cases,

            "court_cases":
                court_cases,

            # -----------------------------
            # Evidence
            # -----------------------------

            "evidence_count":
                evidence_count,

            "fir_evidence_count":
                fir_evidence_count,

            "cdr_evidence_count":
                cdr_evidence_count,

            "cctv_evidence_count":
                cctv_evidence_count,

            "vehicle_evidence_count":
                vehicle_evidence_count,

            "court_evidence_count":
                court_evidence_count,

            "financial_evidence_count":
                financial_evidence_count,

            "location_evidence_count":
                location_evidence_count,

            "source_layer_count":
                source_layer_count,

            "relationship_type_count":
                relationship_type_count,

            # -----------------------------
            # Case context
            # -----------------------------

            "case_relationship_count":
                case_relationship_count,

            "cross_case_connections":
                cross_case_connections,

            # -----------------------------
            # CDR
            # -----------------------------

            "cdr_call_count":
                cdr_call_count,

            "cdr_unique_contacts":
                cdr_unique_contacts,

            "cdr_total_duration":
                cdr_total_duration,

            # -----------------------------
            # CCTV
            # -----------------------------

            "cctv_observation_count":
                cctv_observation_count,

            "cctv_unique_locations":
                cctv_unique_locations,

            "cctv_vehicle_links":
                cctv_vehicle_links,

            # -----------------------------
            # Vehicle
            # -----------------------------

            "vehicle_links":
                vehicle_links,

            "unique_vehicles":
                unique_vehicles,

            # -----------------------------
            # Location
            # -----------------------------

            "location_links":
                location_links,

            "unique_locations":
                unique_locations,

            # -----------------------------
            # Financial
            # -----------------------------

            "financial_transaction_count":
                financial_transaction_count,

            "financial_total_amount":
                financial_total_amount,

            # -----------------------------
            # Temporal
            # -----------------------------

            "temporal_span_days":
                temporal_span_days,
        }

        return features


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    TEST_PERSON = "person:ravi"

    # Use a real FIR case from the current synthetic dataset.
    TEST_CASE = "case:FIR-101-2025"

    try:

        features = get_profile_features(
            TEST_PERSON,
            TEST_CASE
        )

        print()
        print("=" * 60)
        print("LAYER 1 PROFILE FEATURES")
        print("=" * 60)

        print(f"Person : {TEST_PERSON}")
        print(f"Case   : {TEST_CASE}")
        print()

        for key, value in features.items():

            print(
                f"{key:35s}: {value}"
            )

        print()
        print(
            f"Total features: {len(features)}"
        )

        print()
        print("✅ Layer 1 feature extraction successful")

    except Exception as e:

        print()
        print("❌ Layer 1 feature extraction failed")
        print(e)

    finally:

        driver.close()