from database.connection import SessionLocal
from database.models import Relationship
from database.neo4j_connection import driver


def normalize_entity_id(value):
    """
    PostgreSQL:
        person:Ravi
        vehicle:DL01AB1001

    Neo4j canonical_id:
        person:ravi
        vehicle:dl01ab1001
    """
    if not value:
        return None

    return value.strip().lower()


def sync_vehicle_to_neo4j():

    db = SessionLocal()

    try:

        relationships = (
            db.query(Relationship)
            .filter(
                Relationship.relationship_type
                == "ASSOCIATED_WITH_VEHICLE"
            )
            .all()
        )

        print(
            f"✅ Vehicle relationships found: "
            f"{len(relationships)}"
        )

        synced = 0
        skipped = 0

        with driver.session() as session:

            for relationship in relationships:

                # ---------------------------------------------
                # Normalize entity IDs
                # ---------------------------------------------

                person_id = normalize_entity_id(
                    relationship.source_entity_id
                )

                vehicle_id = normalize_entity_id(
                    relationship.target_entity_id
                )

                # IMPORTANT:
                # Case and Evidence IDs preserve their original
                # capitalization.
                case_id = (
                    relationship.case_id.strip()
                    if relationship.case_id
                    else None
                )

                evidence_id = (
                    relationship.evidence_id.strip()
                    if relationship.evidence_id
                    else None
                )

                # ---------------------------------------------
                # Check required Neo4j nodes
                # ---------------------------------------------

                check_query = """
                MATCH (person:Person {
                    canonical_id: $person_id
                })

                MATCH (vehicle:Vehicle {
                    canonical_id: $vehicle_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                RETURN person, vehicle, case_node, evidence
                """

                result = session.run(
                    check_query,
                    person_id=person_id,
                    vehicle_id=vehicle_id,
                    case_id=case_id,
                    evidence_id=evidence_id
                )

                record = result.single()

                if not record:

                    print(
                        f"⚠️ Skipping vehicle relationship: "
                        f"{relationship.id}"
                    )

                    print(
                        f"   Person   : {person_id}"
                    )

                    print(
                        f"   Vehicle  : {vehicle_id}"
                    )

                    print(
                        f"   Case     : {case_id}"
                    )

                    print(
                        f"   Evidence : {evidence_id}"
                    )

                    skipped += 1
                    continue

                # ---------------------------------------------
                # Create Vehicle relationships
                # ---------------------------------------------

                sync_query = """

                MATCH (person:Person {
                    canonical_id: $person_id
                })

                MATCH (vehicle:Vehicle {
                    canonical_id: $vehicle_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                // -----------------------------------------
                // Person → Vehicle
                // -----------------------------------------

                MERGE (
                    person
                )-[r:RELATED {
                    relationship_id: $relationship_id
                }]->(
                    vehicle
                )

                SET
                    r.relationship_type =
                        "ASSOCIATED_WITH_VEHICLE",

                    r.source_layer = "VEHICLE",

                    r.layer_id = $layer_id,

                    r.case_id = $case_id,

                    r.timestamp = $timestamp,

                    r.confidence = $confidence,

                    r.evidence_id = $evidence_id

                // -----------------------------------------
                // Vehicle → Evidence
                // -----------------------------------------

                MERGE (
                    vehicle
                )-[ve:VEHICLE_RECORDED_IN {
                    relationship_id: $relationship_id
                }]->(
                    evidence
                )

                SET
                    ve.source_layer = "VEHICLE",

                    ve.case_id = $case_id,

                    ve.timestamp = $timestamp,

                    ve.confidence = $confidence

                // -----------------------------------------
                // Person → Evidence
                // -----------------------------------------

                MERGE (
                    person
                )-[pe:VEHICLE_RECORDED_IN {
                    relationship_id: $relationship_id
                }]->(
                    evidence
                )

                SET
                    pe.source_layer = "VEHICLE",

                    pe.case_id = $case_id,

                    pe.timestamp = $timestamp,

                    pe.confidence = $confidence

                // -----------------------------------------
                // Evidence → Case
                // -----------------------------------------

                MERGE (
                    evidence
                )-[:BELONGS_TO]->(
                    case_node
                )

                RETURN person, vehicle, evidence, case_node
                """

                session.run(
                    sync_query,

                    person_id=person_id,

                    vehicle_id=vehicle_id,

                    case_id=case_id,

                    evidence_id=evidence_id,

                    relationship_id=(
                        f"vehicle-rel:{relationship.id}"
                    ),

                    layer_id=relationship.layer_id,

                    timestamp=relationship.timestamp,

                    confidence=relationship.confidence
                )

                synced += 1

        print()
        print("================================")
        print(" VEHICLE → Neo4j Sync Complete")
        print("================================")

        print(
            f"✅ Vehicle relationships synced : {synced}"
        )

        print(
            f"⚠️ Vehicle relationships skipped: {skipped}"
        )

        print(
            f"📊 Total relationships          : "
            f"{len(relationships)}"
        )

    except Exception as e:

        print()
        print("❌ Vehicle sync failed")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":

    try:
        sync_vehicle_to_neo4j()

    finally:
        driver.close()