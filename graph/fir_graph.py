from datetime import datetime

import networkx as nx
from sqlalchemy import or_

from database.models import (
    Case,
    Entity,
    Relationship,
    Evidence,
)


# ============================================================
# HELPERS
# ============================================================

def normalize(value):
    """
    Normalize values before comparison.
    """
    if value is None:
        return ""

    return str(value).strip().lower()


def make_node_id(entity):
    """
    Use the canonical database entity ID as the graph node ID.
    """
    return entity.canonical_id


def add_entity_node(graph, entity):
    """
    Add a database entity to the FIR graph.
    """
    node_id = make_node_id(entity)

    graph.add_node(
        node_id,
        entity_id=entity.id,
        canonical_id=entity.canonical_id,
        entity_type=entity.entity_type,
        name=entity.name,
        layer="FIR",
    )


def add_case_node(graph, case):
    """
    Add FIR case node.
    """
    case_node_id = f"case:{case.id}"

    graph.add_node(
        case_node_id,
        entity_type="CASE",
        case_id=case.id,
        fir_number=case.fir_number,
        name=case.fir_number or case.id,
        layer="FIR",
    )

    return case_node_id


# ============================================================
# INPUT ENTITY MATCHING
# ============================================================

def find_matching_entities(db, input_entities):
    """
    Find canonical database entities matching the entities
    extracted from the incoming FIR.

    input_entities example:

    {
        "persons": ["Ravi"],
        "phones": ["9876500001"],
        "locations": ["Connaught Place"],
        "vehicles": ["DL01AB1001"]
    }
    """

    matches = []

    entity_types = {
        "persons": "PERSON",
        "phones": "PHONE",
        "locations": "LOCATION",
        "vehicles": "VEHICLE",
        "organizations": "ORGANIZATION",
        "devices": "DEVICE",
    }

    for field, entity_type in entity_types.items():

        values = input_entities.get(field, [])

        if not values:
            continue

        for value in values:

            normalized_value = normalize(value)

            if not normalized_value:
                continue

            candidates = (
                db.query(Entity)
                .filter(
                    Entity.entity_type == entity_type,
                    Entity.name.isnot(None)
                )
                .all()
            )

            for entity in candidates:

                if (
                    normalize(entity.name) == normalized_value
                    or
                    normalize(entity.canonical_id) == normalized_value
                ):
                    matches.append(entity)

    # Remove duplicates
    unique = {}

    for entity in matches:
        unique[entity.id] = entity

    return list(unique.values())


# ============================================================
# FIND RELEVANT FIR CASES
# ============================================================

def find_matching_cases(db, matched_entities):
    """
    Find FIR cases connected to the matched input entities.

    IMPORTANT:
    We do NOT load every case.

    Only cases connected to the resolved input entities
    are selected.
    """

    if not matched_entities:
        return []

    entity_ids = [
        entity.id
        for entity in matched_entities
    ]

    relationships = (
        db.query(Relationship)
        .filter(
            Relationship.source_entity_id.in_(entity_ids)
            |
            Relationship.target_entity_id.in_(entity_ids)
        )
        .all()
    )

    case_ids = {
        relationship.case_id
        for relationship in relationships
        if relationship.case_id
    }

    if not case_ids:
        return []

    cases = (
        db.query(Case)
        .filter(Case.id.in_(case_ids))
        .all()
    )

    return cases


# ============================================================
# BUILD FIR GRAPH
# ============================================================

def build_fir_graph(
    db,
    input_entities,
    include_case_context=True,
):
    """
    Build a contextual FIR graph from an incoming FIR.

    Workflow:

        Input FIR
             ↓
        Entity matching
             ↓
        Matching FIR cases
             ↓
        Relevant FIR relationships
             ↓
        FIR contextual graph
    """

    graph = nx.MultiDiGraph()

    # --------------------------------------------------------
    # 1. MATCH INPUT ENTITIES
    # --------------------------------------------------------

    matched_entities = find_matching_entities(
        db,
        input_entities
    )

    if not matched_entities:
        return {
            "graph": graph,
            "matched_entities": [],
            "matched_cases": [],
        }

    # --------------------------------------------------------
    # 2. FIND MATCHING FIR CASES
    # --------------------------------------------------------

    matched_cases = find_matching_cases(
        db,
        matched_entities
    )

    matched_case_ids = {
        case.id
        for case in matched_cases
    }

    # --------------------------------------------------------
    # 3. ADD MATCHED INPUT ENTITIES
    # --------------------------------------------------------

    for entity in matched_entities:
        add_entity_node(
            graph,
            entity
        )

    # --------------------------------------------------------
    # 4. ADD CASE NODES
    # --------------------------------------------------------

    for case in matched_cases:
        add_case_node(
            graph,
            case
        )

    # --------------------------------------------------------
    # 5. LOAD ONLY RELATIONSHIPS FROM MATCHED CASES
    # --------------------------------------------------------

    relationships = []

    if matched_case_ids:

        relationships = (
            db.query(Relationship)
            .filter(
                Relationship.case_id.in_(
                    matched_case_ids
                )
            )
            .all()
        )

    # --------------------------------------------------------
    # 6. RESOLVE ENTITIES USED BY THESE RELATIONSHIPS
    # --------------------------------------------------------

    entity_ids = set()

    for relationship in relationships:

        entity_ids.add(
            relationship.source_entity_id
        )

        entity_ids.add(
            relationship.target_entity_id
        )

    context_entities = {}

    if entity_ids:

        entities = (
            db.query(Entity)
            .filter(
                Entity.id.in_(entity_ids)
            )
            .all()
        )

        context_entities = {
            entity.id: entity
            for entity in entities
        }

    # --------------------------------------------------------
    # 7. ADD CONTEXT ENTITIES
    # --------------------------------------------------------

    for entity in context_entities.values():

        add_entity_node(
            graph,
            entity
        )

    # --------------------------------------------------------
    # 8. ADD CASE → ENTITY RELATIONSHIPS
    # --------------------------------------------------------

    for relationship in relationships:

        source_entity = context_entities.get(
            relationship.source_entity_id
        )

        target_entity = context_entities.get(
            relationship.target_entity_id
        )

        if not source_entity or not target_entity:
            continue

        source_node = make_node_id(
            source_entity
        )

        target_node = make_node_id(
            target_entity
        )

        graph.add_edge(
            source_node,
            target_node,

            relationship_id=relationship.id,

            relationship_type=(
                relationship.relationship_type
            ),

            layer="FIR",

            case_id=relationship.case_id,

            timestamp=(
                relationship.timestamp.isoformat()
                if relationship.timestamp
                else None
            ),

            confidence=(
                relationship.confidence
            ),

            evidence_id=(
                relationship.evidence_id
            ),
        )

    # --------------------------------------------------------
    # 9. CONNECT ENTITIES TO THEIR FIR CASES
    # --------------------------------------------------------

    if include_case_context:

        for relationship in relationships:

            source_entity = context_entities.get(
                relationship.source_entity_id
            )

            target_entity = context_entities.get(
                relationship.target_entity_id
            )

            if not source_entity or not target_entity:
                continue

            case_node = (
                f"case:{relationship.case_id}"
            )

            source_node = make_node_id(
                source_entity
            )

            target_node = make_node_id(
                target_entity
            )

            graph.add_edge(
                source_node,
                case_node,
                relationship_type="involved_in",
                layer="FIR",
                case_id=relationship.case_id,
            )

            graph.add_edge(
                target_node,
                case_node,
                relationship_type="involved_in",
                layer="FIR",
                case_id=relationship.case_id,
            )

    # --------------------------------------------------------
    # 10. ATTACH EVIDENCE INFORMATION
    # --------------------------------------------------------

    evidence_ids = {
        relationship.evidence_id
        for relationship in relationships
        if relationship.evidence_id
    }

    if evidence_ids:

        evidence_records = (
            db.query(Evidence)
            .filter(
                Evidence.id.in_(evidence_ids)
            )
            .all()
        )

        for evidence in evidence_records:

            evidence_node = (
                f"evidence:{evidence.id}"
            )

            graph.add_node(
                evidence_node,

                entity_type="EVIDENCE",

                evidence_id=evidence.id,

                evidence_type=(
                    evidence.evidence_type
                ),

                source=evidence.source,

                layer="FIR",

                storage_path=(
                    evidence.storage_path
                ),
            )

    # --------------------------------------------------------
    # 11. CONNECT EVIDENCE TO RELATIONSHIPS
    # --------------------------------------------------------

    for relationship in relationships:

        if not relationship.evidence_id:
            continue

        source_entity = context_entities.get(
            relationship.source_entity_id
        )

        target_entity = context_entities.get(
            relationship.target_entity_id
        )

        if not source_entity or not target_entity:
            continue

        source_node = make_node_id(
            source_entity
        )

        target_node = make_node_id(
            target_entity
        )

        evidence_node = (
            f"evidence:{relationship.evidence_id}"
        )

        if evidence_node not in graph:
            continue

        graph.add_edge(
            source_node,
            evidence_node,

            relationship_type="supported_by",

            layer="FIR",

            case_id=relationship.case_id,
        )

        graph.add_edge(
            evidence_node,
            target_node,

            relationship_type="supports",

            layer="FIR",

            case_id=relationship.case_id,
        )

    return {
        "graph": graph,

        "matched_entities": [
            {
                "id": entity.id,
                "canonical_id": entity.canonical_id,
                "entity_type": entity.entity_type,
                "name": entity.name,
            }
            for entity in matched_entities
        ],

        "matched_cases": [
            {
                "id": case.id,
                "fir_number": case.fir_number,
                "police_station": case.police_station,
                "status": case.status,
            }
            for case in matched_cases
        ],
    }