from database.connection import SessionLocal
from database.models import Entity, Case
from database.neo4j_connection import driver


def sync_entities():
    db = SessionLocal()

    try:
        entities = db.query(Entity).all()

        with driver.session() as session:
            for entity in entities:

                label_map = {
                    "PERSON": "Person",
                    "PHONE": "Phone",
                    "VEHICLE": "Vehicle",
                    "LOCATION": "Location",
                    "ORGANIZATION": "Organization",
                    "BANK_ACCOUNT": "Account",
                    "ACCOUNT": "Account",
                    "DEVICE": "Device",
                }

                label = label_map.get(
                    entity.entity_type.upper(),
                    "Entity"
                )
                query = f"""
                MERGE (n:{label} {{
                    canonical_id: $canonical_id
                }})

                SET n.entity_id = $entity_id,
                    n.name = $name,
                    n.entity_type = $entity_type,
                    n.created_at = $created_at
                """

                session.run(
                    query,
                    canonical_id=entity.canonical_id,
                    entity_id=entity.id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                    created_at=(
                        entity.created_at.isoformat()
                        if entity.created_at
                        else None
                    )
                )

        print(f"✅ Synced {len(entities)} entities")

    finally:
        db.close()


def sync_cases():
    db = SessionLocal()

    try:
        cases = db.query(Case).all()

        with driver.session() as session:
            for case in cases:

                query = """
                MERGE (c:Case {
                    id: $id
                })

                SET c.fir_number = $fir_number,
                    c.case_type = $case_type,
                    c.police_station = $police_station,
                    c.incident_date = $incident_date,
                    c.registered_date = $registered_date,
                    c.status = $status,
                    c.created_at = $created_at,
                    c.source_layer = "FIR"
                """

                session.run(
                    query,
                    id=case.id,
                    fir_number=case.fir_number,
                    case_type=case.case_type,
                    police_station=case.police_station,
                    incident_date=(
                        case.incident_date.isoformat()
                        if case.incident_date
                        else None
                    ),
                    registered_date=(
                        case.registered_date.isoformat()
                        if case.registered_date
                        else None
                    ),
                    status=case.status,
                    created_at=(
                        case.created_at.isoformat()
                        if case.created_at
                        else None
                    )
                )

        print(f"✅ Synced {len(cases)} cases")

    finally:
        db.close()


def main():
    print("\n================================")
    print(" PostgreSQL → Neo4j Sync")
    print("================================\n")

    sync_entities()
    sync_cases()

    print("\n✅ Entity + Case sync completed")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.close()