from typing import Any, Dict, Optional, Set

from fastapi import APIRouter, HTTPException, Query

from database.neo4j_connection import driver


router = APIRouter(
    prefix="/network",
    tags=["Network"],
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_case_id(case_id: str) -> str:
    if not case_id:
        raise ValueError("case_id is required")

    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


def get_node_id(node: Any) -> Optional[str]:
    labels = set(node.labels)

    if "Case" in labels:
        return node.get("id")

    if "Evidence" in labels:
        return node.get("id")

    if "CourtCase" in labels:
        return node.get("id")

    canonical_id = node.get("canonical_id")
    if canonical_id:
        return canonical_id

    entity_id = node.get("entity_id")
    if entity_id:
        return entity_id

    node_id = node.get("id")
    if node_id:
        return node_id

    return None


def get_node_type(node: Any) -> str:
    labels = set(node.labels)

    priority = [
        "Case",
        "Person",
        "Phone",
        "Vehicle",
        "Location",
        "Account",
        "Organization",
        "CourtCase",
        "Evidence",
    ]

    for label in priority:
        if label in labels:
            return label

    return next(iter(labels), "Unknown")


def get_node_label(node: Any) -> str:
    node_type = get_node_type(node)

    if node_type == "Person":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Person"
        )

    if node_type == "Phone":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Phone"
        )

    if node_type == "Vehicle":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Vehicle"
        )

    if node_type == "Location":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Location"
        )

    if node_type == "Account":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Account"
        )

    if node_type == "Organization":
        return (
            node.get("name")
            or node.get("canonical_id")
            or "Unknown Organization"
        )

    if node_type == "Case":
        return (
            node.get("fir_number")
            or node.get("id")
            or "Unknown Case"
        )

    if node_type == "Evidence":
        return (
            node.get("evidence_type")
            or node.get("id")
            or "Evidence"
        )

    if node_type == "CourtCase":
        return (
            node.get("court_case_number")
            or node.get("court_name")
            or node.get("id")
            or "Court Case"
        )

    return get_node_id(node) or "Unknown"


def serialize_node(node: Any) -> Dict[str, Any]:
    node_id = get_node_id(node)

    return {
        "id": node_id,
        "type": get_node_type(node),
        "label": get_node_label(node),
        "properties": dict(node),
    }


def serialize_edge(
    relationship: Any,
    source_id: str,
    target_id: str,
) -> Dict[str, Any]:
    return {
        "id": str(relationship.id),
        "source": source_id,
        "target": target_id,
        "relationship": relationship.type,
        "properties": dict(relationship),
    }


# ---------------------------------------------------------
# CASE CHECK
# ---------------------------------------------------------

def case_exists(case_id: str) -> bool:
    query = """
    MATCH (c:Case {id: $case_id})
    RETURN c
    LIMIT 1
    """

    with driver.session() as session:
        record = session.run(
            query,
            case_id=case_id,
        ).single()

        return record is not None


# ---------------------------------------------------------
# BUILD LARGE MASTER SUBGRAPH
# ---------------------------------------------------------

def build_case_network(case_id: str):
    """
    Builds a reasonably large investigation graph.

    Case
      ↓
    Evidence
      ↓
    Entities
      ↓
    Related entities

    Everything is still restricted to entities that belong
    to the selected investigation.
    """

    query = """
    MATCH (c:Case {id: $case_id})

    MATCH (c)-[:BELONGS_TO]-(e:Evidence)

    OPTIONAL MATCH path =
        (e)-[*1..2]-(connected)

    WITH c, e, connected

    WHERE connected IS NULL
       OR NOT "Case" IN labels(connected)
       OR connected.id = $case_id

    RETURN c, e, connected
    """

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: Dict[str, Dict[str, Any]] = {}

    with driver.session() as session:
        result = session.run(
            query,
            case_id=case_id,
        )

        for record in result:
            case_node = record["c"]
            evidence_node = record["e"]
            connected_node = record["connected"]

            case_id_value = get_node_id(case_node)
            evidence_id = get_node_id(evidence_node)

            if case_id_value:
                nodes[case_id_value] = serialize_node(case_node)

            if evidence_id:
                nodes[evidence_id] = serialize_node(evidence_node)

            if connected_node is None:
                continue

            connected_id = get_node_id(connected_node)

            if not connected_id:
                continue

            nodes[connected_id] = serialize_node(connected_node)

    # -----------------------------------------------------
    # Get relationships between all discovered nodes
    # -----------------------------------------------------

    discovered_ids = list(nodes.keys())

    if not discovered_ids:
        return {
            "case_id": case_id,
            "nodes": [],
            "edges": [],
        }

    relationship_query = """
    MATCH (a)-[r]-(b)

    WHERE
        (
            ("Case" IN labels(a) AND a.id IN $node_ids)
            OR
            ("Evidence" IN labels(a) AND a.id IN $node_ids)
            OR
            (NOT "Case" IN labels(a)
             AND NOT "Evidence" IN labels(a)
             AND a.canonical_id IN $node_ids)
        )

    AND
        (
            ("Case" IN labels(b) AND b.id IN $node_ids)
            OR
            ("Evidence" IN labels(b) AND b.id IN $node_ids)
            OR
            (NOT "Case" IN labels(b)
             AND NOT "Evidence" IN labels(b)
             AND b.canonical_id IN $node_ids)
        )

    RETURN a, r, b
    """

    with driver.session() as session:
        result = session.run(
            relationship_query,
            node_ids=discovered_ids,
        )

        for record in result:
            a = record["a"]
            relationship = record["r"]
            b = record["b"]

            source_id = get_node_id(a)
            target_id = get_node_id(b)

            if not source_id or not target_id:
                continue

            if source_id not in nodes:
                continue

            if target_id not in nodes:
                continue

            edge_id = str(relationship.id)

            edges[edge_id] = serialize_edge(
                relationship,
                source_id,
                target_id,
            )

    return {
        "case_id": case_id,
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
    }


# ---------------------------------------------------------
# FOCUSED SUBGRAPH
# ---------------------------------------------------------

def build_entity_subgraph(
    entity_id: str,
    case_id: str,
    depth: int = 2,
):
    """
    Generates a larger subgraph around the selected entity.

    Important:
    We only allow nodes that are already part of the selected
    case investigation.
    """

    # First determine all nodes belonging to this investigation.
    allowed_query = """
    MATCH (c:Case {id: $case_id})
    MATCH (c)-[:BELONGS_TO]-(e:Evidence)

    OPTIONAL MATCH (e)-[*1..2]-(entity)

    WITH collect(DISTINCT c) +
         collect(DISTINCT e) +
         collect(DISTINCT entity) AS raw_nodes

    UNWIND raw_nodes AS n

    WITH DISTINCT n
    WHERE n IS NOT NULL

    RETURN
        CASE
            WHEN "Case" IN labels(n) THEN n.id
            WHEN "Evidence" IN labels(n) THEN n.id
            ELSE n.canonical_id
        END AS node_id
    """

    allowed_ids: Set[str] = set()

    with driver.session() as session:
        result = session.run(
            allowed_query,
            case_id=case_id,
        )

        for record in result:
            node_id = record["node_id"]

            if node_id:
                allowed_ids.add(node_id)

    if entity_id not in allowed_ids:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Entity {entity_id} is not part of "
                f"investigation {case_id}"
            ),
        )

    # -----------------------------------------------------
    # Find selected entity and neighbours.
    # -----------------------------------------------------

    query = """
    MATCH (center)

    WHERE
        ("Case" IN labels(center) AND center.id = $entity_id)
        OR
        ("Evidence" IN labels(center) AND center.id = $entity_id)
        OR
        ("CourtCase" IN labels(center) AND center.id = $entity_id)
        OR
        ("Person" IN labels(center) AND center.canonical_id = $entity_id)
        OR
        ("Phone" IN labels(center) AND center.canonical_id = $entity_id)
        OR
        ("Vehicle" IN labels(center) AND center.canonical_id = $entity_id)
        OR
        ("Location" IN labels(center) AND center.canonical_id = $entity_id)
        OR
        ("Account" IN labels(center) AND center.canonical_id = $entity_id)
        OR
        ("Organization" IN labels(center) AND center.canonical_id = $entity_id)

    MATCH path =
        (center)-[*1..2]-(neighbor)

    RETURN center, path, neighbor
    """

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: Dict[str, Dict[str, Any]] = {}

    with driver.session() as session:
        result = session.run(
            query,
            entity_id=entity_id,
        )

        for record in result:
            center = record["center"]
            neighbor = record["neighbor"]
            path = record["path"]

            center_id = get_node_id(center)

            if center_id and center_id in allowed_ids:
                nodes[center_id] = serialize_node(center)

            if neighbor is not None:
                neighbor_id = get_node_id(neighbor)

                if (
                    neighbor_id
                    and neighbor_id in allowed_ids
                ):
                    nodes[neighbor_id] = serialize_node(neighbor)

            if path is None:
                continue

            relationships = list(path.relationships)
            path_nodes = list(path.nodes)

            for index, relationship in enumerate(relationships):
                source = path_nodes[index]
                target = path_nodes[index + 1]

                source_id = get_node_id(source)
                target_id = get_node_id(target)

                if not source_id or not target_id:
                    continue

                if source_id not in allowed_ids:
                    continue

                if target_id not in allowed_ids:
                    continue

                edges[str(relationship.id)] = serialize_edge(
                    relationship,
                    source_id,
                    target_id,
                )

    return {
        "case_id": case_id,
        "focused_entity": entity_id,
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
    }


# ---------------------------------------------------------
# MASTER NETWORK
# ---------------------------------------------------------

@router.get("")
def get_network(
    case_id: str = Query(...),
):
    try:
        normalized_case_id = normalize_case_id(case_id)

        if not case_exists(normalized_case_id):
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Investigation "
                    f"{normalized_case_id} not found"
                ),
            )

        network = build_case_network(
            normalized_case_id
        )

        return {
            "status": "success",
            "network": network,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print("NETWORK ERROR:", exc)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to build network: {exc}",
        )


# ---------------------------------------------------------
# ENTITY SUBGRAPH
# ---------------------------------------------------------

@router.get("/entity/{entity_id:path}")
def get_entity_network(
    entity_id: str,
    case_id: str = Query(...),
):
    try:
        normalized_case_id = normalize_case_id(case_id)

        network = build_entity_subgraph(
            entity_id=entity_id,
            case_id=normalized_case_id,
        )

        return {
            "status": "success",
            "network": network,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print("ENTITY NETWORK ERROR:", exc)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to build entity subgraph: {exc}",
        )