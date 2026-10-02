from database.connection import SessionLocal
from database.models import CDRRecord
from database.neo4j_connection import driver


def sync_cdr_records():
    db = SessionLocal()

    try:
        records = db.query(CDRRecord).all()

        synced = 0
        skipped = 0

        with driver.session() as session:

            for record in records:

                query = """
                MATCH (caller:Phone {
                    canonical_id: $caller_canonical_id
                })

                MATCH (receiver:Phone {
                    canonical_id: $receiver_canonical_id
                })

                MATCH (case:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                MERGE (caller)-[r:RELATED {
                    relationship_id: $relationship_id
                }]->(receiver)

                SET
                    r.relationship_type = "CDR_CALL",
                    r.source_layer = "CDR",
                    r.timestamp = $timestamp,
                    r.duration_seconds = $duration_seconds,
                    r.communication_type = $communication_type,
                    r.case_id = $case_id,
                    r.evidence_id = $evidence_id

                MERGE (caller)-[:CALL_RECORDED_IN {
                    cdr_id: $relationship_id
                }]->(evidence)

                MERGE (receiver)-[:CALL_RECORDED_IN {
                    cdr_id: $relationship_id
                }]->(evidence)

                MERGE (evidence)-[:BELONGS_TO]->(case)

                RETURN r
                """

                result = session.run(
                    query,
                    relationship_id=record.id,

                    # IMPORTANT:
                    # PostgreSQL stores the raw phone number,
                    # Neo4j stores phone:<number>
                    caller_canonical_id=f"phone:{record.caller_phone}",
                    receiver_canonical_id=f"phone:{record.receiver_phone}",

                    case_id=record.case_id,
                    evidence_id=record.evidence_id,
                    timestamp=record.timestamp,
                    duration_seconds=record.duration_seconds,
                    communication_type=record.communication_type,
                )

                if result.single():
                    synced += 1
                else:
                    skipped += 1

        print(f"✅ CDR records found: {len(records)}")
        print(f"✅ CDR records synced: {synced}")
        print(f"⚠️ CDR records skipped: {skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    sync_cdr_records()
    driver.close()