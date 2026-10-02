from database.connection import SessionLocal
from graph.fir_graph import build_fir_graph


def main():

    db = SessionLocal()

    try:

        # Simulated entities extracted from NEW FIR
        input_entities = {
            "persons": ["Ravi"],
            "phones": ["9876500001"],
            "locations": ["Connaught Place"],
            "vehicles": [],
            "organizations": [],
            "devices": [],
        }

        result = build_fir_graph(
            db=db,
            input_entities=input_entities,
        )

        graph = result["graph"]

        print("\n================================")
        print("        FIR GRAPH TEST")
        print("================================")

        print("\nMatched Entities:")

        for entity in result["matched_entities"]:
            print(
                f"  {entity['entity_type']}: "
                f"{entity['name']} "
                f"({entity['canonical_id']})"
            )

        print("\nMatched FIR Cases:")

        for case in result["matched_cases"]:
            print(
                f"  {case['id']} "
                f"| FIR: {case['fir_number']}"
            )

        print("\nGraph Statistics:")
        print(
            f"  Nodes: {graph.number_of_nodes()}"
        )
        print(
            f"  Edges: {graph.number_of_edges()}"
        )

        print("\nGraph Nodes:")

        for node, data in graph.nodes(data=True):
            print(
                f"  {node} "
                f"| {data.get('entity_type')}"
                f" | {data.get('name', '')}"
            )

        print("\nGraph Edges:")

        for source, target, data in graph.edges(data=True):

            print(
                f"  {source}"
                f" --[{data.get('relationship_type')}]--> "
                f"{target}"
            )

        print("\n================================")
        print("       FIR GRAPH TEST DONE")
        print("================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()