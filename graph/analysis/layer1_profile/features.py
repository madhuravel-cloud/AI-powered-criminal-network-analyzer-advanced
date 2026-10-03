from database.neo4j_connection import driver


def get_profile_features(canonical_id):
    """
    Extract Layer 1 - Target/Profile features for a person
    from the Neo4j Master Temporal Multilayer Graph.

    The features represent investigation-specific graph relevance,
    not criminality or guilt.
    """

    with driver.session() as session:

        # =========================================================
        # 1. GET TARGET PERSON
        # =========================================================

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

        if not target:
            raise ValueError(
                f"Target entity not found: {canonical_id}"
            )

        target_info = {
            "canonical_id": target["canonical_id"],
            "name": target["name"],
            "entity_type": target["entity_type"],
            "labels": target["labels"],
        }

        # =========================================================
        # 2. BASIC GRAPH CONNECTION FEATURES
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH (p)-[r]-(neighbor)

            RETURN
                count(DISTINCT neighbor) AS unique_connections,
                count(r) AS total_relationships,
                count(DISTINCT neighbor) AS degree
            """,
            canonical_id=canonical_id
        )

        graph_stats = result.single()

        unique_connections = graph_stats["unique_connections"] or 0
        total_relationships = graph_stats["total_relationships"] or 0

# Degree = actual number of relationship edges
        degree = total_relationships

        # =========================================================
        # 3. CONNECTED ENTITY TYPES
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH (p)--(person:Person)
            OPTIONAL MATCH (p)--(phone:Phone)
            OPTIONAL MATCH (p)--(vehicle:Vehicle)
            OPTIONAL MATCH (p)--(location:Location)
            OPTIONAL MATCH (p)--(account:Account)
            OPTIONAL MATCH (p)--(court:CourtCase)

            RETURN
                count(DISTINCT person) AS connected_people,
                count(DISTINCT phone) AS connected_phones,
                count(DISTINCT vehicle) AS connected_vehicles,
                count(DISTINCT location) AS connected_locations,
                count(DISTINCT account) AS connected_accounts,
                count(DISTINCT court) AS court_cases
            """,
            canonical_id=canonical_id
        )

        entity_stats = result.single()

        connected_people = entity_stats["connected_people"] or 0
        connected_phones = entity_stats["connected_phones"] or 0
        connected_vehicles = entity_stats["connected_vehicles"] or 0
        connected_locations = entity_stats["connected_locations"] or 0
        connected_accounts = entity_stats["connected_accounts"] or 0
        court_cases = entity_stats["court_cases"] or 0

        # =========================================================
        # 4. DIRECT EVIDENCE + CDR EVIDENCE
        # =========================================================
        #
        # Most evidence is directly connected:
        #
        # Person → Evidence
        #
        # CDR is different:
        #
        # Person
        #    ↓
        # Phone
        #    ↓
        # CDR_CALL
        #    ↓
        # Phone
        #
        # The CDR relationship stores evidence_id.
        #
        # Therefore CDR evidence must be discovered through
        # the person's phone relationship.
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH (p)--(e:Evidence)

            WITH
                p,
                collect(DISTINCT e) AS direct_evidence

            OPTIONAL MATCH (p)--(phone:Phone)
            OPTIONAL MATCH (phone)-[cdr:RELATED]-(other:Phone)

            WITH
                direct_evidence,
                collect(DISTINCT cdr.evidence_id) AS cdr_evidence_ids

            RETURN

                size(direct_evidence) AS evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type = "FIR_DOCUMENT"
                ]) AS fir_evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type = "CCTV_VIDEO"
                ]) AS cctv_evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type = "VEHICLE_RECORD"
                ]) AS vehicle_evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type = "COURT_DOCUMENT"
                ]) AS court_evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type IN [
                        "BANK_TRANSACTION_FILE",
                        "FINANCIAL_TRANSACTION_FILE"
                    ]
                ]) AS financial_evidence_count,

                size([
                    e IN direct_evidence
                    WHERE e.evidence_type = "LOCATION_RECORD"
                ]) AS location_evidence_count,

                size([
                    x IN cdr_evidence_ids
                    WHERE x IS NOT NULL
                ]) AS cdr_evidence_count
            """,
            canonical_id=canonical_id
        )

        evidence_stats = result.single()

        evidence_count = evidence_stats["evidence_count"] or 0
        fir_evidence_count = evidence_stats["fir_evidence_count"] or 0
        cdr_evidence_count = evidence_stats["cdr_evidence_count"] or 0
        cctv_evidence_count = evidence_stats["cctv_evidence_count"] or 0
        vehicle_evidence_count = evidence_stats["vehicle_evidence_count"] or 0
        court_evidence_count = evidence_stats["court_evidence_count"] or 0
        financial_evidence_count = (
            evidence_stats["financial_evidence_count"] or 0
        )
        location_evidence_count = (
            evidence_stats["location_evidence_count"] or 0
        )

        # =========================================================
        # 5. SOURCE LAYERS
        # =========================================================
        #
        # Collect source layers directly from relationships and
        # evidence types.
        #
        # Expected source domains:
        #
        # FIR
        # COURT
        # CDR
        # VEHICLE
        # CCTV
        # FINANCIAL
        # LOCATION
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH (p)-[r]-(neighbor)

            WITH
                collect(DISTINCT r.source_layer) AS relationship_layers

            RETURN relationship_layers
            """,
            canonical_id=canonical_id
        )

        layer_record = result.single()

        relationship_layers = (
            layer_record["relationship_layers"]
            if layer_record
            else []
        )

        source_layers = set()

        for layer in relationship_layers:
            if layer:
                source_layers.add(layer)

        # Add source layers inferred from evidence types
        if fir_evidence_count > 0:
            source_layers.add("FIR")

        if cdr_evidence_count > 0:
            source_layers.add("CDR")

        if cctv_evidence_count > 0:
            source_layers.add("CCTV")

        if vehicle_evidence_count > 0:
            source_layers.add("VEHICLE")

        if court_evidence_count > 0:
            source_layers.add("COURT")

        if financial_evidence_count > 0:
            source_layers.add("FINANCIAL")

        if location_evidence_count > 0:
            source_layers.add("LOCATION")

        source_layers = sorted(source_layers)

        source_layer_count = len(source_layers)

        # =========================================================
        # 6. RELATIONSHIP TYPE COUNT
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})
            OPTIONAL MATCH (p)-[r]-(neighbor)

            RETURN count(DISTINCT r.relationship_type)
                AS relationship_type_count
            """,
            canonical_id=canonical_id
        )

        relationship_stats = result.single()

        relationship_type_count = (
            relationship_stats["relationship_type_count"] or 0
        )

        # =========================================================
        # 7. BUILD FINAL FEATURE VECTOR
        # =========================================================

        features = {
            # Graph structure
            "unique_connections": unique_connections,
            "total_relationships": total_relationships,
            "degree": degree,

            # Entity connectivity
            "connected_people": connected_people,
            "connected_phones": connected_phones,
            "connected_vehicles": connected_vehicles,
            "connected_locations": connected_locations,
            "connected_accounts": connected_accounts,

            # Case / court
            "connected_cases": 0,
            "court_cases": court_cases,

            # Evidence
            "evidence_count": evidence_count,

            # Source-specific evidence
            "fir_evidence_count": fir_evidence_count,
            "cdr_evidence_count": cdr_evidence_count,
            "cctv_evidence_count": cctv_evidence_count,
            "vehicle_evidence_count": vehicle_evidence_count,
            "court_evidence_count": court_evidence_count,
            "financial_evidence_count": financial_evidence_count,
            "location_evidence_count": location_evidence_count,

            # Source diversity
            "source_layer_count": source_layer_count,

            # Relationship diversity
            "relationship_type_count": relationship_type_count,
        }

        # =========================================================
        # 8. FIND CONNECTED CASES
        # =========================================================

        result = session.run(
            """
            MATCH (p {canonical_id: $canonical_id})

            OPTIONAL MATCH (p)--(e:Evidence)--(c:Case)

            RETURN count(DISTINCT c) AS connected_cases
            """,
            canonical_id=canonical_id
        )

        case_record = result.single()

        connected_cases = (
            case_record["connected_cases"]
            if case_record
            else 0
        )

        features["connected_cases"] = connected_cases

        # =========================================================
        # 9. RETURN RESULT
        # =========================================================

        return {
            "target": target_info,
            "features": features,
            "source_layers": source_layers,
        }


# =============================================================
# TEST / CLI
# =============================================================

if __name__ == "__main__":

    # Test target
    TARGET_ID = "person:ravi"

    try:

        result = get_profile_features(TARGET_ID)

        print("\n" + "=" * 60)
        print("LAYER 1 — TARGET / PROFILE FEATURE EXTRACTION")
        print("=" * 60)

        print("\nTarget:")
        print(result["target"])

        print("\nFeatures:")

        for key, value in result["features"].items():
            print(f"  {key:30} {value}")

        print("\nSource Layers:")
        print(result["source_layers"])

        print("\n" + "=" * 60)
        print("✅ Layer 1 feature extraction completed")
        print("=" * 60)

    except Exception as e:

        print("\n❌ Layer 1 feature extraction failed")
        print(e)

    finally:

        driver.close()