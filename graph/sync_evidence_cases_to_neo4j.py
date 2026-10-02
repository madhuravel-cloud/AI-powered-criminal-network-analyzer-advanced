from database.connection import SessionLocal
from database.models import Evidence
from database.neo4j_connection import driver


def sync_evidence_cases():

    db = SessionLocal()

    try:
        evidence_records = db.query(Evidence).all()

        linked = 0
        skipped = 0

        with driver.session() as session:

            for evidence in evidence_records:

                if not evidence.case_id:
                    skipped += 1
                    continue

                query = """
                MATCH (e:Evidence {id: $evidence_id})
                MATCH (c:Case {id: $case_id})

                MERGE (e)-[:BELONGS_TO]->(c)
                """

                result = session.run(
                    query,
                    evidence_id=evidence.id,
                    case_id=evidence.case_id
                )

                result.consume()
                linked += 1

        print(f"✅ Linked {linked} evidence records to cases")

        if skipped:
            print(f"⚠️ Skipped {skipped} evidence records without case_id")

    finally:
        db.close()


def main():

    print("\n================================")
    print(" Evidence → Case Linking")
    print("================================\n")

    sync_evidence_cases()

    print("\n✅ Evidence → Case linking completed")


if __name__ == "__main__":

    try:
        main()
    finally:
        driver.close()