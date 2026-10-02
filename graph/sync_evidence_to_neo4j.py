from database.connection import SessionLocal
from database.models import Evidence, EntityEvidence
from database.neo4j_connection import driver


def sync_evidence():

    db = SessionLocal()

    try:
        evidence_records = db.query(Evidence).all()

        with driver.session() as session:

            for evidence in evidence_records:

                query = """
                MERGE (e:Evidence {
                    id: $id
                })

                SET e.case_id = $case_id,
                    e.layer_id = $layer_id,
                    e.evidence_type = $evidence_type,
                    e.source = $source,
                    e.storage_path = $storage_path,
                    e.file_hash = $file_hash,
                    e.extracted_text = $extracted_text,
                    e.created_at = $created_at
                """

                session.run(
                    query,
                    id=evidence.id,
                    case_id=evidence.case_id,
                    layer_id=evidence.layer_id,
                    evidence_type=evidence.evidence_type,
                    source=evidence.source,
                    storage_path=evidence.storage_path,
                    file_hash=evidence.file_hash,
                    extracted_text=evidence.extracted_text,
                    created_at=(
                        evidence.created_at.isoformat()
                        if evidence.created_at
                        else None
                    )
                )

        print(f"✅ Synced {len(evidence_records)} evidence records")

    finally:
        db.close()


def sync_entity_evidence():

    db = SessionLocal()

    try:
        links = db.query(EntityEvidence).all()

        with driver.session() as session:

            for link in links:

                query = """
                MATCH (entity {entity_id: $entity_id})
                MATCH (e:Evidence {id: $evidence_id})

                MERGE (entity)-[r:SUPPORTED_BY {
                    link_id: $link_id
                }]->(e)

                SET r.mention_type = $mention_type,
                    r.confidence = $confidence
                """

                session.run(
                    query,
                    entity_id=link.entity_id,
                    evidence_id=link.evidence_id,
                    link_id=link.id,
                    mention_type=link.mention_type,
                    confidence=link.confidence
                )

        print(f"✅ Synced {len(links)} entity-evidence links")

    finally:
        db.close()


def main():

    print("\n================================")
    print(" PostgreSQL → Neo4j Evidence Sync")
    print("================================\n")

    sync_evidence()
    sync_entity_evidence()

    print("\n✅ Evidence sync completed")


if __name__ == "__main__":

    try:
        main()

    finally:
        driver.close()