from database.neo4j_connection import driver


CONSTRAINTS = [
    """
    CREATE CONSTRAINT person_canonical_id IF NOT EXISTS
    FOR (n:Person)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT phone_canonical_id IF NOT EXISTS
    FOR (n:Phone)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT vehicle_canonical_id IF NOT EXISTS
    FOR (n:Vehicle)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT location_canonical_id IF NOT EXISTS
    FOR (n:Location)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT organization_canonical_id IF NOT EXISTS
    FOR (n:Organization)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT case_id IF NOT EXISTS
    FOR (n:Case)
    REQUIRE n.id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT evidence_id IF NOT EXISTS
    FOR (n:Evidence)
    REQUIRE n.id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT event_id IF NOT EXISTS
    FOR (n:Event)
    REQUIRE n.id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT account_canonical_id IF NOT EXISTS
    FOR (n:Account)
    REQUIRE n.canonical_id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT court_case_id IF NOT EXISTS
    FOR (n:CourtCase)
    REQUIRE n.id IS UNIQUE
    """
]


def create_schema():
    with driver.session() as session:

        for query in CONSTRAINTS:
            session.run(query)

    print("✅ Neo4j constraints created successfully")


if __name__ == "__main__":
    create_schema()
    driver.close()