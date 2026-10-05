from typing import Any, Dict, List

from database.neo4j_connection import driver


# ============================================================
# CASE ID HELPERS
# ============================================================

def normalize_case_id(case_id: str) -> str:
    if not case_id:
        raise ValueError("case_id is required")

    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


# ============================================================
# CASE PEOPLE
# ============================================================

def get_case_people(case_id: str) -> List[Dict[str, Any]]:
    case_id = normalize_case_id(case_id)

    query = """
    MATCH (c:Case {id: $case_id})
    MATCH (c)-[:BELONGS_TO]-(e:Evidence)
    MATCH (p:Person)-[]-(e)

    RETURN DISTINCT
        p.canonical_id AS person_id,
        p.name AS name

    ORDER BY name
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=case_id,
        )

        return [
            {
                "person_id": record["person_id"],
                "name": record["name"],
            }
            for record in result
            if record["person_id"]
        ]


# ============================================================
# CANDIDATE PEOPLE
# ============================================================

def get_candidate_people(
    case_id: str,
) -> List[Dict[str, Any]]:

    case_id = normalize_case_id(case_id)

    query = """
    MATCH (seed_case:Case {id: $case_id})
    MATCH (seed_case)-[:BELONGS_TO]-(seed_evidence:Evidence)
    MATCH (seed_evidence)-[]-(seed_person:Person)

    MATCH (seed_person)-[]-(shared_entity)

    MATCH (candidate:Person)-[]-(shared_entity)
    WHERE candidate <> seed_person

    RETURN DISTINCT
        candidate.canonical_id AS person_id,
        candidate.name AS name

    ORDER BY name
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=case_id,
        )

        return [
            {
                "person_id": record["person_id"],
                "name": record["name"],
            }
            for record in result
            if record["person_id"]
        ]


# ============================================================
# BULK PERSON FEATURES
#
# This replaces the old approach where every candidate caused
# many separate Neo4j queries.
# ============================================================

def get_bulk_person_features(
    person_ids: List[str],
    case_id: str,
) -> Dict[str, Dict[str, Any]]:

    case_id = normalize_case_id(case_id)

    if not person_ids:
        return {}

    query = """
    UNWIND $person_ids AS person_id

    MATCH (p:Person {canonical_id: person_id})

    // --------------------------------------------------------
    // General graph connections
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(connected)

    WITH
        p,
        count(DISTINCT connected) AS unique_connections

    // --------------------------------------------------------
    // People
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(person:Person)

    WITH
        p,
        unique_connections,
        count(DISTINCT person) AS connected_people

    // --------------------------------------------------------
    // Phones
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(phone:Phone)

    WITH
        p,
        unique_connections,
        connected_people,
        count(DISTINCT phone) AS connected_phones

    // --------------------------------------------------------
    // Vehicles
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(vehicle:Vehicle)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        count(DISTINCT vehicle) AS connected_vehicles

    // --------------------------------------------------------
    // Locations
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(location:Location)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        count(DISTINCT location) AS connected_locations

    // --------------------------------------------------------
    // Accounts
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(account:Account)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        count(DISTINCT account) AS connected_accounts

    // --------------------------------------------------------
    // Court cases
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(court:CourtCase)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        count(DISTINCT court) AS court_cases

    // --------------------------------------------------------
    // Evidence
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(evidence:Evidence)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        court_cases,
        collect(DISTINCT evidence) AS evidences

    // --------------------------------------------------------
    // Cases
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(case_node:Case)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        court_cases,
        evidences,
        collect(DISTINCT case_node) AS cases

    // --------------------------------------------------------
    // Selected case evidence
    // --------------------------------------------------------

    OPTIONAL MATCH (selected_case:Case {id: $case_id})
        -[:BELONGS_TO]-(selected_evidence:Evidence)

    OPTIONAL MATCH (p)-[]-(selected_evidence)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        court_cases,
        evidences,
        cases,
        count(DISTINCT selected_evidence) AS case_relationship_count

    // --------------------------------------------------------
    // CDR
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(cdr_phone:Phone)
    OPTIONAL MATCH (cdr_phone)-[cdr_rel:RELATED]-(other_phone:Phone)

    WITH
        p,
        unique_connections,
        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        court_cases,
        evidences,
        cases,
        case_relationship_count,
        count(DISTINCT other_phone) AS cdr_unique_contacts,
        count(DISTINCT cdr_rel) AS cdr_call_count,
        coalesce(
            sum(
                toFloat(
                    coalesce(
                        cdr_rel.duration,
                        cdr_rel.call_duration,
                        0
                    )
                )
            ),
            0
        ) AS cdr_total_duration

    // --------------------------------------------------------
    // Return core information
    // --------------------------------------------------------

    RETURN
        p.canonical_id AS person_id,
        p.name AS name,

        unique_connections,

        unique_connections AS total_relationships,

        unique_connections AS degree,

        connected_people,
        connected_phones,
        connected_vehicles,
        connected_locations,
        connected_accounts,
        size(cases) AS connected_cases,
        court_cases,

        size(
            [
                x IN evidences
                WHERE x IS NOT NULL
            ]
        ) AS evidence_count,

        case_relationship_count,

        cdr_call_count,
        cdr_unique_contacts,
        cdr_total_duration,

        [
            e IN evidences
            WHERE e IS NOT NULL
            AND e.evidence_type IS NOT NULL
            | e.evidence_type
        ] AS evidence_types,

        [
            e IN evidences
            WHERE e IS NOT NULL
            AND e.id IS NOT NULL
            | e.id
        ] AS evidence_ids

    ORDER BY p.name
    """

    with driver.session() as session:
        result = session.run(
            query,
            person_ids=person_ids,
            case_id=case_id,
        )

        features = {}

        for record in result:

            evidence_types = list(
                set(
                    record["evidence_types"] or []
                )
            )

            evidence_ids = list(
                set(
                    record["evidence_ids"] or []
                )
            )

            source_counts = {
                "FIR_DOCUMENT": 0,
                "CDR_FILE": 0,
                "CCTV_VIDEO": 0,
                "VEHICLE_RECORD": 0,
                "COURT_DOCUMENT": 0,
                "BANK_TRANSACTION_FILE": 0,
                "LOCATION_RECORD": 0,
            }

            for evidence_type in evidence_types:
                if evidence_type in source_counts:
                    source_counts[evidence_type] += 1

            # ------------------------------------------------
            # Base features
            # ------------------------------------------------

            person_features = {
                "unique_connections": record["unique_connections"] or 0,

                "total_relationships":
                    record["total_relationships"] or 0,

                "degree":
                    record["degree"] or 0,

                "connected_people":
                    record["connected_people"] or 0,

                "connected_phones":
                    record["connected_phones"] or 0,

                "connected_vehicles":
                    record["connected_vehicles"] or 0,

                "connected_locations":
                    record["connected_locations"] or 0,

                "connected_accounts":
                    record["connected_accounts"] or 0,

                "connected_cases":
                    record["connected_cases"] or 0,

                "court_cases":
                    record["court_cases"] or 0,

                "evidence_count":
                    record["evidence_count"] or 0,

                "fir_evidence_count":
                    source_counts["FIR_DOCUMENT"],

                "cdr_evidence_count":
                    source_counts["CDR_FILE"],

                "cctv_evidence_count":
                    source_counts["CCTV_VIDEO"],

                "vehicle_evidence_count":
                    source_counts["VEHICLE_RECORD"],

                "court_evidence_count":
                    source_counts["COURT_DOCUMENT"],

                "financial_evidence_count":
                    source_counts[
                        "BANK_TRANSACTION_FILE"
                    ],

                "location_evidence_count":
                    source_counts["LOCATION_RECORD"],

                "source_layer_count":
                    len(
                        [
                            value
                            for value in source_counts.values()
                            if value > 0
                        ]
                    ),

                "relationship_type_count": 0,

                "case_relationship_count":
                    record["case_relationship_count"] or 0,

                "cross_case_connections":
                    max(
                        (record["connected_cases"] or 0) - 1,
                        0,
                    ),

                "cdr_call_count":
                    record["cdr_call_count"] or 0,

                "cdr_unique_contacts":
                    record["cdr_unique_contacts"] or 0,

                "cdr_total_duration":
                    float(
                        record["cdr_total_duration"] or 0
                    ),

                "cctv_observation_count":
                    source_counts["CCTV_VIDEO"],

                "cctv_unique_locations": 0,

                "cctv_vehicle_links": 0,

                "vehicle_links":
                    record["connected_vehicles"] or 0,

                "unique_vehicles":
                    record["connected_vehicles"] or 0,

                "location_links":
                    record["connected_locations"] or 0,

                "unique_locations":
                    record["connected_locations"] or 0,

                "financial_transaction_count":
                    source_counts[
                        "BANK_TRANSACTION_FILE"
                    ],

                "financial_total_amount": 0,

                "temporal_span_days": 0,
            }

            features[
                record["person_id"]
            ] = person_features

    return features


# ============================================================
# EMPTY FEATURE OBJECT
# ============================================================

def empty_features() -> Dict[str, Any]:

    return {
        "unique_connections": 0,
        "total_relationships": 0,
        "degree": 0,
        "connected_people": 0,
        "connected_phones": 0,
        "connected_vehicles": 0,
        "connected_locations": 0,
        "connected_accounts": 0,
        "connected_cases": 0,
        "court_cases": 0,
        "evidence_count": 0,
        "fir_evidence_count": 0,
        "cdr_evidence_count": 0,
        "cctv_evidence_count": 0,
        "vehicle_evidence_count": 0,
        "court_evidence_count": 0,
        "financial_evidence_count": 0,
        "location_evidence_count": 0,
        "source_layer_count": 0,
        "relationship_type_count": 0,
        "case_relationship_count": 0,
        "cross_case_connections": 0,
        "cdr_call_count": 0,
        "cdr_unique_contacts": 0,
        "cdr_total_duration": 0,
        "cctv_observation_count": 0,
        "cctv_unique_locations": 0,
        "cctv_vehicle_links": 0,
        "vehicle_links": 0,
        "unique_vehicles": 0,
        "location_links": 0,
        "unique_locations": 0,
        "financial_transaction_count": 0,
        "financial_total_amount": 0,
        "temporal_span_days": 0,
    }


# ============================================================
# SUPPORTING RELATIONSHIPS
# ============================================================

def get_supporting_relationships(
    person_id: str,
    case_id: str,
) -> List[Dict[str, Any]]:

    case_id = normalize_case_id(case_id)

    query = """
    MATCH (p:Person {canonical_id: $person_id})
    MATCH (p)-[r]-(connected)

    OPTIONAL MATCH (connected_evidence:Evidence)
    WHERE connected_evidence.id = r.evidence_id

    RETURN
        type(r) AS graph_relationship,

        coalesce(
            r.relationship_type,
            type(r)
        ) AS relationship_type,

        coalesce(
            connected.canonical_id,
            connected.id
        ) AS connected_entity_id,

        coalesce(
            connected.name,
            connected.fir_number,
            connected.id,
            connected.canonical_id
        ) AS connected_entity,

        coalesce(
            r.source_layer,
            connected.source_layer,
            connected_evidence.evidence_type
        ) AS source_layer,

        r.timestamp AS timestamp,

        coalesce(
            r.evidence_id,
            connected_evidence.id
        ) AS evidence_id,

        coalesce(
            r.confidence,
            1.0
        ) AS confidence

    LIMIT 200
    """

    with driver.session() as session:
        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id,
        )

        return [
            dict(record)
            for record in result
        ]


# ============================================================
# PERSON EVIDENCE
# ============================================================

def get_person_evidence_ids(
    person_id: str,
    case_id: str,
) -> List[str]:

    query = """
    MATCH (p:Person {canonical_id: $person_id})
    MATCH (p)-[]-(e:Evidence)

    RETURN DISTINCT e.id AS evidence_id
    """

    with driver.session() as session:
        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id,
        )

        return [
            record["evidence_id"]
            for record in result
            if record["evidence_id"]
        ]


# ============================================================
# TIMELINE
# ============================================================

def get_person_timeline(
    person_id: str,
    case_id: str,
) -> List[Dict[str, Any]]:

    query = """
    MATCH (p:Person {canonical_id: $person_id})
    MATCH (p)-[r]-(connected)

    OPTIONAL MATCH (e:Evidence)
    WHERE e.id = r.evidence_id

    RETURN
        r.timestamp AS timestamp,

        coalesce(
            r.relationship_type,
            type(r)
        ) AS relationship_type,

        coalesce(
            r.source_layer,
            e.evidence_type
        ) AS source_layer,

        coalesce(
            connected.canonical_id,
            connected.id
        ) AS connected_entity_id,

        coalesce(
            connected.name,
            connected.fir_number,
            connected.id
        ) AS connected_entity,

        coalesce(
            r.evidence_id,
            e.id
        ) AS evidence_id

    ORDER BY timestamp
    LIMIT 200
    """

    with driver.session() as session:
        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id,
        )

        return [
            dict(record)
            for record in result
        ]


# ============================================================
# CONNECTED CASES
# ============================================================

def get_relevant_case_ids(
    case_id: str,
) -> List[str]:

    case_id = normalize_case_id(case_id)

    query = """
    MATCH (seed:Case {id: $case_id})
    MATCH (seed)-[:BELONGS_TO]-(seed_evidence:Evidence)
    MATCH (seed_evidence)-[]-(person:Person)

    MATCH (person)-[]-(other_evidence:Evidence)
    MATCH (other:Case)-[:BELONGS_TO]-(other_evidence)

    WHERE other.id <> seed.id

    RETURN DISTINCT other.id AS case_id
    ORDER BY other.id
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=case_id,
        )

        return [
            record["case_id"]
            for record in result
            if record["case_id"]
        ]


# ============================================================
# SIGNALS
# ============================================================

def get_person_signals(
    features: Dict[str, Any],
    relationships: List[Dict[str, Any]],
    source_layers: List[str],
    connected_cases: List[str],
) -> List[str]:

    signals = []

    if features.get(
        "case_relationship_count",
        0,
    ) > 0:

        signals.append(
            "Direct relationship with selected case"
        )

    if features.get(
        "cross_case_connections",
        0,
    ) > 0:

        signals.append(
            "Connected to additional cases"
        )

    if features.get(
        "cdr_unique_contacts",
        0,
    ) > 0:

        signals.append(
            "Communication network detected"
        )

    if features.get(
        "cctv_observation_count",
        0,
    ) > 0:

        signals.append(
            "CCTV-linked activity detected"
        )

    if features.get(
        "financial_transaction_count",
        0,
    ) > 0:

        signals.append(
            "Financial evidence detected"
        )

    if features.get(
        "connected_vehicles",
        0,
    ) > 0:

        signals.append(
            "Vehicle association detected"
        )

    if features.get(
        "connected_locations",
        0,
    ) > 0:

        signals.append(
            "Location association detected"
        )

    if len(source_layers) >= 3:

        signals.append(
            "Multi-source evidence presence"
        )

    return signals


# ============================================================
# RELEVANCE SCORE
# ============================================================

def calculate_relevance_score(
    features: Dict[str, Any],
) -> float:

    weights = {
        "case_relationship_count": 0.30,
        "cross_case_connections": 0.20,
        "unique_connections": 0.15,
        "connected_people": 0.10,
        "connected_phones": 0.05,
        "connected_vehicles": 0.05,
        "connected_locations": 0.05,
        "connected_accounts": 0.05,
        "connected_cases": 0.05,
    }

    score = 0.0

    for feature, weight in weights.items():

        value = float(
            features.get(feature, 0)
            or 0
        )

        normalized = min(
            value / 10.0,
            1.0,
        )

        score += (
            normalized * weight * 100
        )

    return round(
        min(score, 100),
        2,
    )


# ============================================================
# ANOMALY
# ============================================================

def calculate_anomaly(
    features: Dict[str, Any],
) -> Dict[str, Any]:

    indicators = []

    if features.get(
        "cross_case_connections",
        0,
    ) >= 3:

        indicators.append(
            "High cross-case connectivity"
        )

    if features.get(
        "connected_people",
        0,
    ) >= 5:

        indicators.append(
            "Large person network"
        )

    if features.get(
        "source_layer_count",
        0,
    ) >= 4:

        indicators.append(
            "Multi-source evidence footprint"
        )

    if features.get(
        "financial_transaction_count",
        0,
    ) >= 3:

        indicators.append(
            "Multiple financial records"
        )

    if features.get(
        "cdr_unique_contacts",
        0,
    ) >= 5:

        indicators.append(
            "High communication connectivity"
        )

    return {
        "present": len(indicators) >= 2,
        "indicator_count": len(indicators),
        "indicators": indicators,
    }


# ============================================================
# COMPLETE INVESTIGATION ANALYSIS
# ============================================================

def analyze_investigation(
    case_id: str,
) -> Dict[str, Any]:

    case_id = normalize_case_id(case_id)

    # --------------------------------------------------------
    # STEP 1
    # Get people directly connected to selected FIR
    # --------------------------------------------------------

    case_people = get_case_people(
        case_id
    )

    # --------------------------------------------------------
    # STEP 2
    # Get candidate people
    # --------------------------------------------------------

    candidate_people = get_candidate_people(
        case_id
    )

    if not candidate_people:

        return {
            "case_id": case_id,
            "seed_people": case_people,
            "candidate_count": 0,
            "overall_relevance_score": 0.0,
            "top_relevant_people": [],
            "anomaly": {
                "present": False,
                "indicator_count": 0,
                "indicators": [],
            },
        }

    # --------------------------------------------------------
    # STEP 3
    # BULK FEATURE EXTRACTION
    #
    # One Neo4j query instead of many queries per candidate.
    # --------------------------------------------------------

    candidate_ids = [
        person["person_id"]
        for person in candidate_people
        if person.get("person_id")
    ]

    bulk_features = get_bulk_person_features(
        candidate_ids,
        case_id,
    )

    # --------------------------------------------------------
    # STEP 4
    # Connected cases are the same investigation-level result.
    # Calculate ONCE.
    # --------------------------------------------------------

    connected_cases = get_relevant_case_ids(
        case_id
    )

    # --------------------------------------------------------
    # STEP 5
    # Calculate ranking locally
    # --------------------------------------------------------

    ranked_candidates = []

    for candidate in candidate_people:

        person_id = candidate["person_id"]

        features = bulk_features.get(
            person_id,
            empty_features(),
        )

        score = calculate_relevance_score(
            features
        )

        anomaly = calculate_anomaly(
            features
        )

        ranked_candidates.append(
            {
                "person_id": person_id,

                "name": candidate.get(
                    "name",
                    "Unknown Person",
                ),

                "relevance_score": score,

                "features": features,

                "supporting_relationships": [],

                "connected_cases": connected_cases,

                "source_layers": [],

                "evidence_ids": [],

                "timeline": [],

                "signals": [],

                "anomaly": anomaly,
            }
        )

    # --------------------------------------------------------
    # STEP 6
    # Sort
    # --------------------------------------------------------

    ranked_candidates.sort(
        key=lambda item: item[
            "relevance_score"
        ],
        reverse=True,
    )

    # --------------------------------------------------------
    # STEP 7
    # Detailed graph information ONLY for top 10
    #
    # This is the major performance improvement.
    # --------------------------------------------------------

    top_people = ranked_candidates[:10]

    for person in top_people:

        person_id = person["person_id"]

        relationships = (
            get_supporting_relationships(
                person_id,
                case_id,
            )
        )

        source_layers = sorted(
            list(
                set(
                    relationship.get(
                        "source_layer"
                    )
                    for relationship in relationships
                    if relationship.get(
                        "source_layer"
                    )
                )
            )
        )

        evidence_ids = sorted(
            list(
                set(
                    relationship.get(
                        "evidence_id"
                    )
                    for relationship in relationships
                    if relationship.get(
                        "evidence_id"
                    )
                )
            )
        )

        timeline = get_person_timeline(
            person_id,
            case_id,
        )

        signals = get_person_signals(
            person["features"],
            relationships,
            source_layers,
            connected_cases,
        )

        person["supporting_relationships"] = (
            relationships
        )

        person["source_layers"] = (
            source_layers
        )

        person["evidence_ids"] = (
            evidence_ids
        )

        person["timeline"] = (
            timeline
        )

        person["signals"] = (
            signals
        )

    # --------------------------------------------------------
    # STEP 8
    # Overall relevance
    # --------------------------------------------------------

    if top_people:

        overall_score = round(
            sum(
                person["relevance_score"]
                for person in top_people
            )
            / len(top_people),
            2,
        )

    else:

        overall_score = 0.0

    # --------------------------------------------------------
    # STEP 9
    # Overall anomaly indicators
    # --------------------------------------------------------

    anomaly_indicators = []

    for person in top_people:

        anomaly = person.get(
            "anomaly",
            {},
        )

        anomaly_indicators.extend(
            anomaly.get(
                "indicators",
                [],
            )
        )

    anomaly_indicators = sorted(
        list(
            set(
                anomaly_indicators
            )
        )
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "case_id": case_id,

        "seed_people": case_people,

        "candidate_count": len(
            ranked_candidates
        ),

        "overall_relevance_score":
            overall_score,

        "top_relevant_people":
            top_people,

        "anomaly": {
            "present":
                len(anomaly_indicators) >= 2,

            "indicator_count":
                len(anomaly_indicators),

            "indicators":
                anomaly_indicators,
        },
    }