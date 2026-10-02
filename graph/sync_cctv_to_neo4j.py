from database.connection import SessionLocal
from database.models import CCTVObservation
from database.neo4j_connection import driver


def normalize_canonical_id(value):
    """
    Normalize PostgreSQL canonical IDs so they match Neo4j.

    Example:
        person:Ravi                  -> person:ravi
        vehicle:DL01AB1001           -> vehicle:dl01ab1001
        location:Connaught Place     -> location:connaught place
    """
    if not value:
        return None

    return value.strip().lower()


def sync_cctv_to_neo4j():

    db = SessionLocal()

    try:
        observations = db.query(CCTVObservation).all()

        print(f"✅ CCTV records found: {len(observations)}")

        synced = 0
        skipped = 0

        with driver.session() as session:

            for observation in observations:

                # --------------------------------------------------
                # Normalize PostgreSQL IDs
                # --------------------------------------------------

                entity_id = normalize_canonical_id(
                    observation.entity_id
                )

                vehicle_id = normalize_canonical_id(
                    observation.vehicle_id
                )

                location_id = normalize_canonical_id(
                    observation.location_id
                )

                case_id = observation.case_id.strip() if observation.case_id else None
                evidence_id = observation.evidence_id.strip() if observation.evidence_id else None
                # --------------------------------------------------
                # Match nodes in Neo4j
                # --------------------------------------------------

                query = """
                MATCH (person:Person {
                    canonical_id: $entity_id
                })

                MATCH (vehicle:Vehicle {
                    canonical_id: $vehicle_id
                })

                MATCH (location:Location {
                    canonical_id: $location_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                RETURN person,
                       vehicle,
                       location,
                       case_node,
                       evidence
                """

                result = session.run(
                    query,
                    entity_id=entity_id,
                    vehicle_id=vehicle_id,
                    location_id=location_id,
                    case_id=case_id,
                    evidence_id=evidence_id
                )

                record = result.single()

                if not record:
                    print(
                        f"⚠️ Skipping CCTV observation: "
                        f"{observation.id}"
                    )

                    print(
                        f"   Person   : {entity_id}"
                    )
                    print(
                        f"   Vehicle  : {vehicle_id}"
                    )
                    print(
                        f"   Location : {location_id}"
                    )
                    print(
                        f"   Case     : {case_id}"
                    )
                    print(
                        f"   Evidence : {evidence_id}"
                    )

                    skipped += 1
                    continue

                # --------------------------------------------------
                # Create CCTV observation relationships
                # --------------------------------------------------

                relationship_query = """
                MATCH (person:Person {
                    canonical_id: $entity_id
                })

                MATCH (vehicle:Vehicle {
                    canonical_id: $vehicle_id
                })

                MATCH (location:Location {
                    canonical_id: $location_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                // ----------------------------------------------
                // Person -> Location
                // ----------------------------------------------

                MERGE (
                    person
                )-[r:RELATED {
                    relationship_id: $observation_id
                }]->(
                    location
                )

                SET
                    r.relationship_type = "CCTV_OBSERVED_AT",
                    r.source_layer = "CCTV",
                    r.timestamp = $timestamp,
                    r.camera_id = $camera_id,
                    r.event_type = $event_type,
                    r.confidence = $confidence,
                    r.case_id = $case_id,
                    r.evidence_id = $evidence_id

                // ----------------------------------------------
                // Person -> Vehicle
                // ----------------------------------------------

                MERGE (
                    person
                )-[v:RELATED {
                    relationship_id: $vehicle_relationship_id
                }]->(
                    vehicle
                )

                SET
                    v.relationship_type = "CCTV_ASSOCIATED_VEHICLE",
                    v.source_layer = "CCTV",
                    v.timestamp = $timestamp,
                    v.camera_id = $camera_id,
                    v.event_type = $event_type,
                    v.confidence = $confidence,
                    v.case_id = $case_id,
                    v.evidence_id = $evidence_id

                // ----------------------------------------------
                // Person -> Evidence
                // ----------------------------------------------

                MERGE (
                    person
                )-[pe:CCTV_RECORDED_IN {
                    observation_id: $observation_id
                }]->(
                    evidence
                )

                SET
                    pe.timestamp = $timestamp,
                    pe.camera_id = $camera_id,
                    pe.confidence = $confidence

                // ----------------------------------------------
                // Vehicle -> Evidence
                // ----------------------------------------------

                MERGE (
                    vehicle
                )-[ve:CCTV_RECORDED_IN {
                    observation_id: $observation_id
                }]->(
                    evidence
                )

                SET
                    ve.timestamp = $timestamp,
                    ve.camera_id = $camera_id,
                    ve.confidence = $confidence

                // ----------------------------------------------
                // Location -> Evidence
                // ----------------------------------------------

                MERGE (
                    location
                )-[le:CCTV_RECORDED_IN {
                    observation_id: $observation_id
                }]->(
                    evidence
                )

                SET
                    le.timestamp = $timestamp,
                    le.camera_id = $camera_id,
                    le.confidence = $confidence

                // ----------------------------------------------
                // Evidence -> Case
                // ----------------------------------------------

                MERGE (
                    evidence
                )-[:BELONGS_TO]->(
                    case_node
                )

                RETURN person,
                       vehicle,
                       location,
                       evidence,
                       case_node
                """

                session.run(
                    relationship_query,
                    entity_id=entity_id,
                    vehicle_id=vehicle_id,
                    location_id=location_id,
                    case_id=case_id,
                    evidence_id=evidence_id,

                    observation_id=observation.id,

                    vehicle_relationship_id=(
                        f"{observation.id}:VEHICLE"
                    ),

                    timestamp=observation.timestamp,
                    camera_id=observation.camera_id,
                    event_type=observation.event_type,
                    confidence=observation.confidence
                )

                synced += 1

        print()
        print("================================")
        print(" CCTV → Neo4j Sync Complete")
        print("================================")
        print(f"✅ CCTV records synced : {synced}")
        print(f"⚠️ CCTV records skipped: {skipped}")
        print(f"📊 Total records       : {len(observations)}")

    except Exception as e:

        print()
        print("❌ CCTV sync failed")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    try:
        sync_cctv_to_neo4j()
    finally:
        driver.close()