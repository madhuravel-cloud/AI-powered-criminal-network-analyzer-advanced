from database.connection import SessionLocal
from database.models import Relationship
from database.neo4j_connection import driver


def sync_location_relationships():
    db = SessionLocal()

    synced = 0
    skipped = 0

    try:
        records = (
            db.query(Relationship)
            .filter(Relationship.relationship_type == "PRESENT_AT")
            .order_by(Relationship.id)
            .all()
        )

        print(f"✅ Location relationships found: {len(records)}")

        for record in records:
            source_id = (
                record.source_entity_id.strip().lower()
                if record.source_entity_id
                else None
            )

            target_id = (
                record.target_entity_id.strip().lower()
                if record.target_entity_id
                else None
            )

            case_id = (
                record.case_id.strip()
                if record.case_id
                else None
            )

            evidence_id = (
                record.evidence_id.strip()
                if record.evidence_id
                else None
            )

            if not source_id or not target_id:
                skipped += 1
                continue

            with driver.session() as session:

                # -------------------------------------------------
                # Person → Location
                # -------------------------------------------------
                result = session.run(
                    """
                    MATCH (person:Person {canonical_id: $source_id})
                    MATCH (location:Location {canonical_id: $target_id})
                    MERGE (person)-[r:RELATED {
                        relationship_id: $relationship_id
                    }]->(location)

                    SET
                        r.relationship_type = "PRESENT_AT",
                        r.source_layer = "LOCATION",
                        r.layer_id = $layer_id,
                        r.case_id = $case_id,
                        r.timestamp = $timestamp,
                        r.confidence = $confidence,
                        r.evidence_id = $evidence_id

                    RETURN person, location
                    """,
                    source_id=source_id,
                    target_id=target_id,
                    relationship_id=f"location:{record.id}",
                    layer_id=record.layer_id,
                    case_id=case_id,
                    timestamp=record.timestamp.isoformat()
                    if record.timestamp
                    else None,
                    confidence=record.confidence,
                    evidence_id=evidence_id
                )

                if not result.single():
                    skipped += 1
                    continue

                # -------------------------------------------------
                # Person → Evidence
                # -------------------------------------------------
                if evidence_id:
                    session.run(
                        """
                        MATCH (person:Person {canonical_id: $source_id})
                        MATCH (e:Evidence {id: $evidence_id})

                        MERGE (person)-[r:LOCATION_RECORDED_IN {
                            relationship_id: $relationship_id
                        }]->(e)

                        SET
                            r.relationship_type = "LOCATION_RECORDED_IN",
                            r.confidence = $confidence
                        """,
                        source_id=source_id,
                        evidence_id=evidence_id,
                        relationship_id=f"location-evidence:{record.id}",
                        confidence=record.confidence
                    )

                # -------------------------------------------------
                # Location → Evidence
                # -------------------------------------------------
                if evidence_id:
                    session.run(
                        """
                        MATCH (location:Location {canonical_id: $target_id})
                        MATCH (e:Evidence {id: $evidence_id})

                        MERGE (location)-[r:LOCATION_RECORDED_IN {
                            relationship_id: $relationship_id
                        }]->(e)

                        SET
                            r.relationship_type = "LOCATION_RECORDED_IN",
                            r.confidence = $confidence
                        """,
                        target_id=target_id,
                        evidence_id=evidence_id,
                        relationship_id=f"location-evidence-location:{record.id}",
                        confidence=record.confidence
                    )

                # -------------------------------------------------
                # Evidence → Case
                # -------------------------------------------------
                if evidence_id and case_id:
                    session.run(
                        """
                        MATCH (e:Evidence {id: $evidence_id})
                        MATCH (c:Case {id: $case_id})

                        MERGE (e)-[:BELONGS_TO]->(c)
                        """,
                        evidence_id=evidence_id,
                        case_id=case_id
                    )

                synced += 1

        print()
        print("================================")
        print(" LOCATION → Neo4j Sync Complete")
        print("================================")
        print(f"✅ Location relationships synced : {synced}")
        print(f"⚠️ Location relationships skipped: {skipped}")
        print(f"📊 Total records                 : {len(records)}")

    finally:
        db.close()


if __name__ == "__main__":
    sync_location_relationships()
    driver.close()