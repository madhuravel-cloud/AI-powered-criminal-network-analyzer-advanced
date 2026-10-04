from fastapi import APIRouter, HTTPException
from typing import Optional

from database.neo4j_connection import driver

router = APIRouter(
    prefix="/network",
    tags=["Network"],
)


# ============================================================
# HELPERS
# ============================================================

def get_node_id(node):
    """
    Safely extract the canonical ID from a Neo4j node.
    """

    return (
        node.get("id")
        or node.get("entity_id")
        or node.get("uuid")
    )


def get_node_label(node):
    """
    Human-readable node label.
    """

    node_id = get_node_id(node)

    return (
        node.get("name")
        or node.get("label")
        or node.get("value")
        or node_id
        or "Unknown"
    )


def get_node_type(node):
    """
    Resolve entity type from properties or Neo4j labels.
    """

    node_type = node.get("type")

    if node_type:
        return node_type

    node_type = node.get("entity_type")

    if node_type:
        return node_type

    try:
        labels = list(node.labels)

        if labels:
            return labels[0]

    except Exception:
        pass

    return "Unknown"


def serialize_node(node):
    """
    Convert Neo4j node into frontend-safe JSON.
    """

    node_id = get_node_id(node)

    return {
        "id": node_id,
        "label": get_node_label(node),
        "type": get_node_type(node),
        "source_layer": node.get("source_layer"),
        "properties": dict(node),
    }


def serialize_relationship(
    source_id,
    target_id,
    relationship_type,
    relationship_properties=None,
):
    """
    Convert Neo4j relationship into frontend-safe JSON.
    """

    return {
        "id": f"{source_id}__{relationship_type}__{target_id}",
        "source": source_id,
        "target": target_id,
        "relationship": relationship_type,
        "properties": relationship_properties or {},
    }


# ============================================================
# MASTER NETWORK
# ============================================================

@router.get("")
def get_network(
    case_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    source_layer: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 1000,
):
    """
    Return the master investigation network.

    This is the large investigation graph.
    The frontend can display the full 164-node network.
    """

    try:

        with driver.session() as session:

            # ----------------------------------------------------
            # BUILD NODE QUERY
            # ----------------------------------------------------

            conditions = []
            parameters = {
                "limit": limit,
            }

            if entity_type:
                conditions.append(
                    """
                    (
                        n.type = $entity_type
                        OR n.entity_type = $entity_type
                        OR $entity_type IN labels(n)
                    )
                    """
                )

                parameters["entity_type"] = entity_type

            if source_layer:
                conditions.append(
                    "n.source_layer = $source_layer"
                )

                parameters["source_layer"] = source_layer

            if search:
                conditions.append(
                    """
                    (
                        toLower(coalesce(n.id, ''))
                        CONTAINS toLower($search)

                        OR

                        toLower(coalesce(n.name, ''))
                        CONTAINS toLower($search)

                        OR

                        toLower(coalesce(n.label, ''))
                        CONTAINS toLower($search)
                    )
                    """
                )

                parameters["search"] = search

            # ----------------------------------------------------
            # CASE FILTER
            # ----------------------------------------------------

            if case_id:

                query = """
                MATCH (n)
                WHERE (
                    EXISTS {
                        MATCH (n)-[*1..2]-(c)
                        WHERE c.id = $case_id
                           OR c.case_id = $case_id
                    }
                    OR n.id = $case_id
                    OR n.case_id = $case_id
                )
                """

                parameters["case_id"] = case_id

            else:

                query = """
                MATCH (n)
                """

            if conditions:
                query += "\nAND " + "\nAND ".join(conditions)

            query += """
            RETURN n
            LIMIT $limit
            """

            result = session.run(
                query,
                **parameters,
            )

            nodes = []

            for record in result:

                node = record["n"]

                serialized = serialize_node(node)

                if serialized["id"]:
                    nodes.append(serialized)

            # ----------------------------------------------------
            # GET EDGES BETWEEN RETURNED NODES
            # ----------------------------------------------------

            node_ids = [
                node["id"]
                for node in nodes
                if node.get("id")
            ]

            edges = []

            if node_ids:

                edge_result = session.run(
                    """
                    MATCH (a)-[r]-(b)

                    WHERE
                        a.id IN $node_ids
                        AND b.id IN $node_ids

                    RETURN
                        a.id AS source,
                        b.id AS target,
                        type(r) AS relationship,
                        properties(r) AS properties
                    """,
                    node_ids=node_ids,
                )

                seen_edges = set()

                for record in edge_result:

                    source = record["source"]
                    target = record["target"]
                    relationship = record["relationship"]

                    edge_key = (
                        f"{source}"
                        f"__{relationship}"
                        f"__{target}"
                    )

                    reverse_key = (
                        f"{target}"
                        f"__{relationship}"
                        f"__{source}"
                    )

                    if (
                        edge_key in seen_edges
                        or reverse_key in seen_edges
                    ):
                        continue

                    seen_edges.add(edge_key)

                    edges.append(
                        serialize_relationship(
                            source,
                            target,
                            relationship,
                            record["properties"],
                        )
                    )

            return {
                "status": "success",
                "count": len(nodes),
                "nodes": nodes,
                "edges": edges,
            }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to load network: {str(e)}",
        )


# ============================================================
# ENTITY FOCUSED NETWORK
# ============================================================

@router.get("/entity/{entity_id}")
def get_entity_network(
    entity_id: str,
    limit: int = 6,
):
    """
    Return a focused graph around one entity.

    Example:

        /network/entity/person:ravi?limit=6

    Result:

        Ravi
         ├── Phone
         ├── Vehicle
         ├── Location
         ├── Person
         ├── Account
         └── Case
    """

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    if limit < 1:
        limit = 1

    if limit > 6:
        limit = 6

    try:

        with driver.session() as session:

            # ====================================================
            # 1. FIND SELECTED ENTITY
            # ====================================================

            result = session.run(
                """
                MATCH (n)
                WHERE
                    n.id = $entity_id
                    OR n.entity_id = $entity_id

                RETURN n

                LIMIT 1
                """,
                entity_id=entity_id,
            )

            record = result.single()

            if not record:

                raise HTTPException(
                    status_code=404,
                    detail=f"Entity {entity_id} not found",
                )

            selected = record["n"]

            selected_node = serialize_node(
                selected
            )

            selected_id = selected_node["id"]

            # ====================================================
            # 2. GET DIRECT CONNECTIONS
            # ====================================================

            result = session.run(
                """
                MATCH (n)-[r]-(neighbor)

                WHERE
                    n.id = $entity_id
                    OR n.entity_id = $entity_id

                RETURN
                    neighbor,
                    type(r) AS relationship_type,
                    properties(r) AS relationship_properties

                ORDER BY relationship_type

                LIMIT $limit
                """,
                entity_id=entity_id,
                limit=limit,
            )

            neighbors = []

            edges = []

            seen_neighbors = set()

            # ====================================================
            # 3. PROCESS CONNECTIONS
            # ====================================================

            for record in result:

                neighbor = record["neighbor"]

                neighbor_node = serialize_node(
                    neighbor
                )

                neighbor_id = neighbor_node["id"]

                if not neighbor_id:
                    continue

                # Remove duplicates
                if neighbor_id in seen_neighbors:
                    continue

                seen_neighbors.add(
                    neighbor_id
                )

                neighbors.append(
                    neighbor_node
                )

                # --------------------------------------------
                # Relationship
                # --------------------------------------------

                edges.append(
                    serialize_relationship(
                        selected_id,
                        neighbor_id,
                        record[
                            "relationship_type"
                        ],
                        record[
                            "relationship_properties"
                        ],
                    )
                )

            # ====================================================
            # 4. BUILD FINAL NODE LIST
            # ====================================================

            nodes = [
                selected_node,
                *neighbors,
            ]

            # ====================================================
            # 5. RETURN
            # ====================================================

            return {
                "status": "success",

                "selected_entity":
                    selected_node,

                "nodes":
                    nodes,

                "edges":
                    edges,

                "connection_count":
                    len(neighbors),
            }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load entity network: "
                f"{str(e)}"
            ),
        )


# ============================================================
# ENTITY DETAILS
# ============================================================

@router.get("/entity/{entity_id}/details")
def get_entity_details(
    entity_id: str,
):
    """
    Return complete information about one entity.
    """

    try:

        with driver.session() as session:

            result = session.run(
                """
                MATCH (n)

                WHERE
                    n.id = $entity_id
                    OR n.entity_id = $entity_id

                RETURN n

                LIMIT 1
                """,
                entity_id=entity_id,
            )

            record = result.single()

            if not record:

                raise HTTPException(
                    status_code=404,
                    detail=f"Entity {entity_id} not found",
                )

            node = record["n"]

            # ----------------------------------------------------
            # CONNECTION COUNT
            # ----------------------------------------------------

            connection_result = session.run(
                """
                MATCH (n)-[r]-(neighbor)

                WHERE
                    n.id = $entity_id
                    OR n.entity_id = $entity_id

                RETURN count(r) AS count
                """,
                entity_id=entity_id,
            )

            connection_record = (
                connection_result.single()
            )

            connection_count = (
                connection_record["count"]
                if connection_record
                else 0
            )

            # ----------------------------------------------------
            # RETURN
            # ----------------------------------------------------

            return {
                "status": "success",
                "entity": serialize_node(node),
                "connection_count":
                    connection_count,
            }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load entity details: "
                f"{str(e)}"
            ),
        )