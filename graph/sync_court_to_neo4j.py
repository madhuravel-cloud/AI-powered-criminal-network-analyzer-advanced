from database.connection import SessionLocal
from database.models import CourtRecord
from database.neo4j_connection import driver


def normalize_entity_id(value):
    """
    Normalize entity canonical IDs.

    PostgreSQL:
        person:Ravi

    Neo4j:
        person:ravi
    """
    if not value:
        return None

    return value.strip().lower()


def sync_court_to_neo4j():

    db = SessionLocal()

    try:
        records = db.query(CourtRecord).all()

        print(f"✅ Court records found: {len(records)}")

        synced = 0
        skipped = 0

        with driver.session() as session:

            for record in records:

                # ---------------------------------------------
                # IMPORTANT:
                # Entity IDs are lowercase in Neo4j.
                # Case and Evidence IDs preserve their case.
                # ---------------------------------------------

                entity_id = normalize_entity_id(
                    record.entity_id
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

                # ---------------------------------------------
                # Check required nodes
                # ---------------------------------------------

                check_query = """
                MATCH (person:Person {
                    canonical_id: $entity_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                RETURN person, case_node, evidence
                """

                result = session.run(
                    check_query,
                    entity_id=entity_id,
                    case_id=case_id,
                    evidence_id=evidence_id
                )

                existing = result.single()

                if not existing:

                    print(
                        f"⚠️ Skipping court record: {record.id}"
                    )

                    print(
                        f"   Person   : {entity_id}"
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
                # Create Court Case node + relationships
                # ---------------------------------------------

                court_query = """

                MATCH (person:Person {
                    canonical_id: $entity_id
                })

                MATCH (case_node:Case {
                    id: $case_id
                })

                MATCH (evidence:Evidence {
                    id: $evidence_id
                })

                // -----------------------------------------
                // Court Case node
                // -----------------------------------------

                MERGE (court:CourtCase {
                    id: $court_case_id
                })

                SET
                    court.court_case_number = $court_case_number,
                    court.court_name = $court_name,
                    court.hearing_date = $hearing_date

                // -----------------------------------------
                // Person → Court Case
                // -----------------------------------------

                MERGE (
                    person
                )-[r:RELATED {
                    relationship_id: $record_id
                }]->(
                    court
                )

                SET
                    r.relationship_type = "COURT_PARTY",
                    r.source_layer = "COURT",
                    r.role = $role,
                    r.status = $status,
                    r.hearing_date = $hearing_date,
                    r.case_id = $case_id,
                    r.evidence_id = $evidence_id

                // -----------------------------------------
                // Court Case → Main Case
                // -----------------------------------------

                MERGE (
                    court
                )-[cr:RELATED {
                    relationship_id: $record_id + ":CASE"
                }]->(
                    case_node
                )

                SET
                    cr.relationship_type = "COURT_CASE_FOR",
                    cr.source_layer = "COURT",
                    cr.evidence_id = $evidence_id

                // -----------------------------------------
                // Person → Evidence
                // -----------------------------------------

                MERGE (
                    person
                )-[pe:COURT_RECORDED_IN {
                    record_id: $record_id
                }]->(
                    evidence
                )

                SET
                    pe.role = $role,
                    pe.status = $status,
                    pe.hearing_date = $hearing_date

                // -----------------------------------------
                // Court Case → Evidence
                // -----------------------------------------

                MERGE (
                    court
                )-[ce:COURT_RECORDED_IN {
                    record_id: $record_id
                }]->(
                    evidence
                )

                SET
                    ce.hearing_date = $hearing_date

                // -----------------------------------------
                // Evidence → Case
                // -----------------------------------------

                MERGE (
                    evidence
                )-[:BELONGS_TO]->(
                    case_node
                )

                RETURN person, court, case_node, evidence
                """

                session.run(
                    court_query,

                    entity_id=entity_id,

                    case_id=case_id,

                    evidence_id=evidence_id,

                    record_id=record.id,

                    court_case_id=record.court_case_number,

                    court_case_number=record.court_case_number,

                    court_name=record.court_name,

                    hearing_date=record.hearing_date,

                    role=record.role,

                    status=record.status
                )

                synced += 1

        print()
        print("================================")
        print(" COURT → Neo4j Sync Complete")
        print("================================")

        print(
            f"✅ Court records synced : {synced}"
        )

        print(
            f"⚠️ Court records skipped: {skipped}"
        )

        print(
            f"📊 Total records       : {len(records)}"
        )

    except Exception as e:

        print()
        print("❌ Court sync failed")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":

    try:
        sync_court_to_neo4j()

    finally:
        driver.close()