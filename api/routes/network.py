from fastapi import APIRouter, HTTPException

from database.neo4j_connection import driver


router = APIRouter(
    prefix="/network",
    tags=["Network"],
)


# ============================================================
# CASE ID
# ============================================================

def normalize_case_id(case_id: str) -> str:
    if not case_id:
        raise ValueError("case_id is required")

    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


# ============================================================
# NODE HELPERS
# ============================================================

def is_internal_node(node) -> bool:
    labels = set(node.labels)

    return (
        "Case" in labels
        or "Evidence" in labels
    )


def get_node_type(node) -> str:

    labels = set(node.labels)

    priority = [
        "Person",
        "Phone",
        "Vehicle",
        "Location",
        "Account",
        "Organization",
        "Case",
        "Evidence",
    ]

    for label in priority:
        if label in labels:
            return label

    if labels:
        return sorted(labels)[0]

    return "Entity"


def clean_value(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


# ============================================================
# NAME RESOLUTION
# ============================================================

def get_node_name(node) -> str:

    props = dict(node)

    node_type = get_node_type(node)

    # --------------------------------------------------------
    # PERSON
    # --------------------------------------------------------

    if node_type == "Person":

        candidates = [
            props.get("name"),
            props.get("full_name"),
            props.get("person_name"),
            props.get("display_name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if node_type == "Phone":

        candidates = [
            props.get("phone_number"),
            props.get("number"),
            props.get("phone"),
            props.get("mobile"),
            props.get("name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # VEHICLE
    # --------------------------------------------------------

    if node_type == "Vehicle":

        candidates = [
            props.get("registration_number"),
            props.get("vehicle_number"),
            props.get("registration"),
            props.get("number"),
            props.get("name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if node_type == "Location":

        candidates = [
            props.get("location_name"),
            props.get("address"),
            props.get("place"),
            props.get("location"),
            props.get("name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    if node_type == "Account":

        candidates = [
            props.get("account_number"),
            props.get("account_id"),
            props.get("number"),
            props.get("name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # ORGANIZATION
    # --------------------------------------------------------

    if node_type == "Organization":

        candidates = [
            props.get("name"),
            props.get("organization_name"),
            props.get("company_name"),
            props.get("org_name"),
            props.get("canonical_id"),
        ]

        for value in candidates:
            value = clean_value(value)

            if value:
                return value


    # --------------------------------------------------------
    # GENERIC FALLBACK
    # --------------------------------------------------------

    candidates = [
        props.get("name"),
        props.get("display_name"),
        props.get("canonical_id"),
        props.get("id"),
    ]

    for value in candidates:

        value = clean_value(value)

        if value:
            return value


    # --------------------------------------------------------
    # NEO4J ELEMENT ID FALLBACK
    # --------------------------------------------------------

    try:
        return str(node.element_id)
    except Exception:
        return "Unknown Entity"


# ============================================================
# NODE SERIALIZATION
# ============================================================

def serialize_node(node):

    node_type = get_node_type(node)

    props = dict(node)

    canonical_id = clean_value(
        props.get("canonical_id")
    )

    node_id = (
        canonical_id
        or clean_value(props.get("id"))
        or str(node.element_id)
    )

    name = get_node_name(node)

    return {
        "id": str(node_id),

        "node_type": node_type,

        "name": name,

        "canonical_id": canonical_id,

        "properties": props,
    }


# ============================================================
# EDGE SERIALIZATION
# ============================================================

def serialize_edge(
    relationship,
    source_node,
    target_node,
):

    relationship_type = (
        relationship.type
        if hasattr(
            relationship,
            "type",
        )
        else "RELATED"
    )

    source_id = (
        clean_value(
            dict(source_node).get(
                "canonical_id"
            )
        )
        or clean_value(
            dict(source_node).get(
                "id"
            )
        )
        or str(
            source_node.element_id
        )
    )

    target_id = (
        clean_value(
            dict(target_node).get(
                "canonical_id"
            )
        )
        or clean_value(
            dict(target_node).get(
                "id"
            )
        )
        or str(
            target_node.element_id
        )
    )

    return {
        "id": str(
            relationship.element_id
        ),

        "source": str(
            source_id
        ),

        "target": str(
            target_id
        ),

        "relationship_type": relationship_type,

        "properties": dict(
            relationship
        ),
    }


# ============================================================
# GET FIR ENTITIES
# ============================================================

@router.get(
    "/case/{case_id}/entities"
)
def get_case_entities(
    case_id: str,
):

    normalized_case_id = (
        normalize_case_id(case_id)
    )

    query = """
    MATCH (case_node:Case)
    WHERE
        case_node.id = $case_id
        OR case_node.fir_number = $raw_case_id

    MATCH (case_node)-[:BELONGS_TO]-(evidence:Evidence)

    MATCH (evidence)-[]-(entity)

    WHERE
        NOT entity:Case
        AND NOT entity:Evidence

    RETURN DISTINCT entity

    ORDER BY
        CASE
            WHEN entity:Person THEN 1
            WHEN entity:Phone THEN 2
            WHEN entity:Vehicle THEN 3
            WHEN entity:Location THEN 4
            WHEN entity:Account THEN 5
            WHEN entity:Organization THEN 6
            ELSE 7
        END
    """

    try:

        with driver.session() as session:

            result = session.run(
                query,
                case_id=normalized_case_id,
                raw_case_id=case_id,
            )

            entities = []

            seen = set()

            for record in result:

                entity = record["entity"]

                serialized = serialize_node(
                    entity
                )

                entity_id = serialized["id"]

                if entity_id in seen:
                    continue

                seen.add(
                    entity_id
                )

                entities.append(
                    serialized
                )

        return {
            "status": "success",

            "case_id":
                normalized_case_id,

            "count":
                len(entities),

            "entities":
                entities,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to load FIR entities: {str(e)}"
            ),
        )


# ============================================================
# GET ENTITY GRAPH
# ============================================================

@router.get(
    "/case/{case_id}/entity/{entity_id:path}"
)
def get_entity_graph(
    case_id: str,
    entity_id: str,
):

    normalized_case_id = (
        normalize_case_id(case_id)
    )

    # --------------------------------------------------------
    # FIR ENTITY UNIVERSE
    # --------------------------------------------------------

    universe_query = """
    MATCH (case_node:Case)
    WHERE
        case_node.id = $case_id
        OR case_node.fir_number = $raw_case_id

    MATCH (case_node)-[:BELONGS_TO]-(evidence:Evidence)

    MATCH (evidence)-[]-(entity)

    WHERE
        NOT entity:Case
        AND NOT entity:Evidence

    RETURN DISTINCT entity
    """

    # --------------------------------------------------------
    # SELECTED ENTITY
    # --------------------------------------------------------

    selected_query = """
    MATCH (case_node:Case)
    WHERE
        case_node.id = $case_id
        OR case_node.fir_number = $raw_case_id

    MATCH (case_node)-[:BELONGS_TO]-(evidence:Evidence)

    MATCH (evidence)-[]-(entity)

    WHERE
        NOT entity:Case
        AND NOT entity:Evidence
        AND (
            entity.canonical_id = $entity_id
            OR entity.id = $entity_id
            OR entity.name = $entity_id
            OR entity.phone_number = $entity_id
            OR entity.vehicle_number = $entity_id
            OR entity.registration_number = $entity_id
            OR entity.location_name = $entity_id
            OR entity.account_number = $entity_id
        )

    RETURN DISTINCT entity
    LIMIT 1
    """

    try:

        with driver.session() as session:

            # ------------------------------------------------
            # BUILD FIR ENTITY UNIVERSE
            # ------------------------------------------------

            universe_result = session.run(
                universe_query,
                case_id=normalized_case_id,
                raw_case_id=case_id,
            )

            universe_nodes = []

            universe_element_ids = set()

            for record in universe_result:

                node = record["entity"]

                universe_nodes.append(
                    node
                )

                universe_element_ids.add(
                    str(
                        node.element_id
                    )
                )


            # ------------------------------------------------
            # FIND SELECTED ENTITY
            # ------------------------------------------------

            selected_result = session.run(
                selected_query,
                case_id=normalized_case_id,
                raw_case_id=case_id,
                entity_id=entity_id,
            )

            selected_record = (
                selected_result.single()
            )

            if not selected_record:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Entity not found "
                        "inside the selected FIR."
                    ),
                )


            selected_node = (
                selected_record[
                    "entity"
                ]
            )


            # ------------------------------------------------
            # 2-HOP GRAPH
            # ------------------------------------------------

            graph_query = """
            MATCH (selected)
            WHERE elementId(selected) = $selected_element_id

            MATCH path =
                (selected)-[*1..2]-(connected)

            RETURN path
            """

            graph_result = session.run(
                graph_query,
                selected_element_id=
                    selected_node.element_id,
            )


            graph_nodes = {}

            graph_edges = {}


            # ------------------------------------------------
            # ADD SELECTED NODE
            # ------------------------------------------------

            graph_nodes[
                str(
                    selected_node.element_id
                )
            ] = selected_node


            # ------------------------------------------------
            # PROCESS PATHS
            # ------------------------------------------------

            for record in graph_result:

                path = record["path"]

                for node in path.nodes:

                    element_id = str(
                        node.element_id
                    )

                    # Only allow entities belonging
                    # to the selected FIR.

                    if (
                        element_id
                        not in
                        universe_element_ids
                    ):
                        continue

                    graph_nodes[
                        element_id
                    ] = node


                for relationship in path.relationships:

                    start_id = str(
                        relationship.start_node.element_id
                    )

                    end_id = str(
                        relationship.end_node.element_id
                    )


                    if (
                        start_id
                        not in
                        universe_element_ids
                    ):
                        continue

                    if (
                        end_id
                        not in
                        universe_element_ids
                    ):
                        continue


                    source_node = (
                        graph_nodes.get(
                            start_id
                        )
                    )

                    target_node = (
                        graph_nodes.get(
                            end_id
                        )
                    )


                    if (
                        source_node is None
                        or target_node is None
                    ):
                        continue


                    serialized_edge = (
                        serialize_edge(
                            relationship,
                            source_node,
                            target_node,
                        )
                    )


                    graph_edges[
                        serialized_edge["id"]
                    ] = (
                        serialized_edge
                    )


            # ------------------------------------------------
            # SERIALIZE NODES
            # ------------------------------------------------

            serialized_nodes = []

            for node in graph_nodes.values():

                serialized_nodes.append(
                    serialize_node(
                        node
                    )
                )


            # ------------------------------------------------
            # SERIALIZE EDGES
            # ------------------------------------------------

            serialized_edges = list(
                graph_edges.values()
            )


            return {

                "status":
                    "success",

                "case_id":
                    normalized_case_id,

                "selected_entity":
                    serialize_node(
                        selected_node
                    ),

                "nodes":
                    serialized_nodes,

                "edges":
                    serialized_edges,

            }


    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to build entity graph: {str(e)}"
            ),
        )