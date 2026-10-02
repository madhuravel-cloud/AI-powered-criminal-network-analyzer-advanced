import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def test_neo4j_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()

            if record["test"] == 1:
                print("✅ Neo4j connection successful")
                return True

        return False

    except Exception as e:
        print("❌ Neo4j connection failed")
        print(e)
        return False


if __name__ == "__main__":
    test_neo4j_connection()