from database.connection import SessionLocal
from database.models import Relationship
from database.neo4j_connection import driver


def sync_relationships():

    db = SessionLocal()

    try:
        relationships = db.query(Relationship).all()

        with driver.session() as session:

            for rel in relationships:

                query = """
                MATCH (source {entity_id: $source_id})
                MATCH (target {entity_id: $target_id})

                MERGE (source)-[r:RELATED {
                    relationship_id: $relationship_id
                }]->(target)

                SET r.relationship_type = $relationship_type,
                    r.layer_id = $layer_id,
                    r.case_id = $case_id,
                    r.timestamp = $timestamp,
                    r.confidence = $confidence,
                    r.evidence_id = $evidence_id,
                    r.created_at = $created_at
                """

                session.run(
                    query,
                    relationship_id=rel.id,
                    source_id=rel.source_entity_id,
                    target_id=rel.target_entity_id,
                    relationship_type=rel.relationship_type,
                    layer_id=rel.layer_id,
                    case_id=rel.case_id,
                    timestamp=(
                        rel.timestamp.isoformat()
                        if rel.timestamp
                        else None
                    ),
                    confidence=rel.confidence,
                    evidence_id=rel.evidence_id,
                    created_at=(
                        rel.created_at.isoformat()
                        if rel.created_at
                        else None
                    )
                )

        print(f"✅ Synced {len(relationships)} relationships")

    finally:
        db.close()


def main():

    print("\n================================")
    print(" PostgreSQL → Neo4j Relationships")
    print("================================\n")

    sync_relationships()

    print("\n✅ Relationship sync completed")


if __name__ == "__main__":

    try:
        main()

    finally:
        driver.close()