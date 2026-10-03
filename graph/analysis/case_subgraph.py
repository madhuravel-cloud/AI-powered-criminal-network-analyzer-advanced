import networkx as nx

from database.neo4j_connection import driver


def get_case_subgraph(case_id: str) -> nx.MultiDiGraph:
    """
    Extract an investigation-focused subgraph for one case
    from the Neo4j Master Temporal Multilayer Graph.
    """

    graph = nx.MultiDiGraph()

    with driver.session() as session:

        # ---------------------------------------------------------
        # 1. Add the Case node
        # ---------------------------------------------------------
        case_result = session.run(
            """
            MATCH (c:Case {id: $case_id})
            RETURN c
            """,
            case_id=case_id
        )

        case_record = case_result.single()

        if not case_record:
            raise ValueError(f"Case not found: {case_id}")

        case_node = case_record["c"]

        graph.add_node(
            case_node.element_id,
            labels=list(case_node.labels),
            **dict(case_node)
        )

        # ---------------------------------------------------------
        # 2. Get all relationships explicitly associated
        #    with this case
        # ---------------------------------------------------------
        relationship_result = session.run(
            """
            MATCH (a)-[r]->(b)
            WHERE r.case_id = $case_id
            RETURN a, r, b
            """,
            case_id=case_id
        )

        for record in relationship_result:

            source = record["a"]
            relationship = record["r"]
            target = record["b"]

            source_id = source.element_id
            target_id = target.element_id

            # Add source node
            graph.add_node(
                source_id,
                labels=list(source.labels),
                **dict(source)
            )

            # Add target node
            graph.add_node(
                target_id,
                labels=list(target.labels),
                **dict(target)
            )

            # Add relationship
            relationship_properties = dict(relationship)

            graph.add_edge(
                source_id,
                target_id,
                key=relationship.element_id,
                neo4j_type=relationship.type,
                **relationship_properties
            )

        # ---------------------------------------------------------
        # 3. Add evidence → Case relationships
        # ---------------------------------------------------------
        evidence_result = session.run(
            """
            MATCH (e:Evidence)-[r:BELONGS_TO]->(c:Case {id: $case_id})
            RETURN e, r, c
            """,
            case_id=case_id
        )

        for record in evidence_result:

            evidence = record["e"]
            relationship = record["r"]
            case = record["c"]

            evidence_id = evidence.element_id
            case_node_id = case.element_id

            graph.add_node(
                evidence_id,
                labels=list(evidence.labels),
                **dict(evidence)
            )

            graph.add_node(
                case_node_id,
                labels=list(case.labels),
                **dict(case)
            )

            graph.add_edge(
                evidence_id,
                case_node_id,
                key=relationship.element_id,
                neo4j_type=relationship.type,
                **dict(relationship)
            )

        # ---------------------------------------------------------
        # 4. Add evidence-linked relationships
        #
        # This captures things such as:
        #
        # Person → Evidence
        # Vehicle → Evidence
        # Location → Evidence
        # CourtCase → Evidence
        # ---------------------------------------------------------
        evidence_links_result = session.run(
            """
            MATCH (entity)-[r]->(e:Evidence)
            MATCH (e)-[:BELONGS_TO]->(c:Case {id: $case_id})
            RETURN entity, r, e
            """,
            case_id=case_id
        )

        for record in evidence_links_result:

            entity = record["entity"]
            relationship = record["r"]
            evidence = record["e"]

            entity_id = entity.element_id
            evidence_id = evidence.element_id

            graph.add_node(
                entity_id,
                labels=list(entity.labels),
                **dict(entity)
            )

            graph.add_node(
                evidence_id,
                labels=list(evidence.labels),
                **dict(evidence)
            )

            graph.add_edge(
                entity_id,
                evidence_id,
                key=relationship.element_id,
                neo4j_type=relationship.type,
                **dict(relationship)
            )

    return graph


def print_subgraph_summary(graph: nx.MultiDiGraph):
    """Print a readable summary of the extracted investigation graph."""

    print()
    print("========================================")
    print(" CASE SUBGRAPH")
    print("========================================")

    print(f"Nodes         : {graph.number_of_nodes()}")
    print(f"Relationships : {graph.number_of_edges()}")

    print()
    print("Node types:")

    node_type_counts = {}

    for _, data in graph.nodes(data=True):

        labels = data.get("labels", [])

        for label in labels:
            node_type_counts[label] = (
                node_type_counts.get(label, 0) + 1
            )

    for node_type, count in sorted(node_type_counts.items()):
        print(f"  {node_type:<15} {count}")

    print()
    print("Relationship types:")

    relationship_counts = {}

    for _, _, data in graph.edges(data=True):

        relationship_type = data.get(
            "relationship_type",
            data.get("neo4j_type", "UNKNOWN")
        )

        relationship_counts[relationship_type] = (
            relationship_counts.get(relationship_type, 0) + 1
        )

    for relationship_type, count in sorted(
        relationship_counts.items()
    ):
        print(f"  {relationship_type:<30} {count}")


if __name__ == "__main__":

    CASE_ID = "case:FIR-101-2025"

    print(f"Extracting case subgraph: {CASE_ID}")

    graph = get_case_subgraph(CASE_ID)

    print_subgraph_summary(graph)

    driver.close()