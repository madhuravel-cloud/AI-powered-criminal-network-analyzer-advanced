# api/analysis_service.py

from collections import Counter
from typing import Any, Dict, List

from database.neo4j_connection import driver


# ============================================================
# CASE / FIR HELPERS
# ============================================================

def normalize_case_id(case_id: str) -> str:
    """
    Convert:
        FIR-101-2025
    into:
        case:FIR-101-2025

    If already normalized, keep it unchanged.
    """
    if not case_id:
        raise ValueError("case_id is required")

    case_id = case_id.strip()

    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


# ============================================================
# CASE PEOPLE
# ============================================================

def get_case_people(case_id: str) -> List[Dict[str, Any]]:
    """
    Get people directly associated with the selected FIR
    through that FIR's evidence.
    """

    canonical_case_id = normalize_case_id(case_id)

    query = """
    MATCH (c:Case {id: $case_id})
    MATCH (c)-[:BELONGS_TO]-(e:Evidence)
    MATCH (e)-[]-(p:Person)

    RETURN DISTINCT
        p.canonical_id AS person_id,
        p.name AS name

    ORDER BY name
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=canonical_case_id,
        )

        return [dict(record) for record in result]


# ============================================================
# FIR-SCOPED CANDIDATE DISCOVERY
# ============================================================

def get_candidate_people(case_id: str) -> List[Dict[str, Any]]:
    """
    Find candidate people using ONLY entities/evidence that are
    connected to the selected FIR.

    Important:
    We do NOT search the entire global graph first.

    Flow:

        FIR
          ↓
        Evidence
          ↓
        Seed Person
          ↓
        Shared Entity
          ↓
        Candidate Person

    This prevents every FIR from producing the same candidate set.
    """

    canonical_case_id = normalize_case_id(case_id)

    query = """
    MATCH (selected_case:Case {id: $case_id})
    MATCH (selected_case)-[:BELONGS_TO]-(selected_evidence:Evidence)
    MATCH (seed_person:Person)-[]-(selected_evidence)

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
            case_id=canonical_case_id,
        )

        return [dict(record) for record in result]


# ============================================================
# FIR-SCOPED PERSON FEATURES
# ============================================================

def get_person_features(
    person_id: str,
    case_id: str,
) -> Dict[str, Any]:
    """
    Calculate investigation features for ONE person.

    The important difference from the previous implementation is
    that FIR-specific features are calculated from evidence belonging
    to the selected case.
    """

    canonical_case_id = normalize_case_id(case_id)

    query = """
    MATCH (p:Person {canonical_id: $person_id})

    // --------------------------------------------------------
    // FIR-SCOPED EVIDENCE
    // --------------------------------------------------------

    OPTIONAL MATCH (selected_case:Case {id: $case_id})
    OPTIONAL MATCH (selected_case)-[:BELONGS_TO]-(case_evidence:Evidence)
    OPTIONAL MATCH (p)-[]-(case_evidence)

    WITH
        p,
        selected_case,
        collect(DISTINCT case_evidence) AS fir_evidence

    // --------------------------------------------------------
    // FIR-SCOPED RELATIONSHIPS
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence

    OPTIONAL MATCH (p)-[fir_rel]-(evidence)

    WITH
        p,
        selected_case,
        fir_evidence,
        collect(DISTINCT fir_rel) AS fir_relationships

    // --------------------------------------------------------
    // FIR-SCOPED PEOPLE
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence_for_people

    OPTIONAL MATCH (evidence_for_people)-[]-(fir_person:Person)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        collect(DISTINCT fir_person) AS fir_people

    // --------------------------------------------------------
    // FIR-SCOPED PHONES
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence_for_phones

    OPTIONAL MATCH (evidence_for_phones)-[]-(phone:Phone)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        fir_people,
        collect(DISTINCT phone) AS fir_phones

    // --------------------------------------------------------
    // FIR-SCOPED VEHICLES
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence_for_vehicles

    OPTIONAL MATCH (evidence_for_vehicles)-[]-(vehicle:Vehicle)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        fir_people,
        fir_phones,
        collect(DISTINCT vehicle) AS fir_vehicles

    // --------------------------------------------------------
    // FIR-SCOPED LOCATIONS
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence_for_locations

    OPTIONAL MATCH (evidence_for_locations)-[]-(location:Location)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        fir_people,
        fir_phones,
        fir_vehicles,
        collect(DISTINCT location) AS fir_locations

    // --------------------------------------------------------
    // FIR-SCOPED ACCOUNTS
    // --------------------------------------------------------

    UNWIND CASE
        WHEN size(fir_evidence) = 0
        THEN [NULL]
        ELSE fir_evidence
    END AS evidence_for_accounts

    OPTIONAL MATCH (evidence_for_accounts)-[]-(account:Account)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        fir_people,
        fir_phones,
        fir_vehicles,
        fir_locations,
        collect(DISTINCT account) AS fir_accounts

    // --------------------------------------------------------
    // GLOBAL CASE CONNECTIONS
    // Used only as a secondary cross-case signal.
    // --------------------------------------------------------

    OPTIONAL MATCH (p)-[]-(all_evidence:Evidence)
    OPTIONAL MATCH (all_evidence)-[:BELONGS_TO]-(connected_case:Case)

    WITH
        p,
        selected_case,
        fir_evidence,
        fir_relationships,
        fir_people,
        fir_phones,
        fir_vehicles,
        fir_locations,
        fir_accounts,
        collect(DISTINCT connected_case) AS all_cases

    RETURN
        p.canonical_id AS person_id,
        p.name AS name,

        // FIR-specific counts
        size(fir_evidence) AS evidence_count,
        size(fir_relationships) AS relationship_count,
        size(fir_people) AS connected_people,
        size(fir_phones) AS connected_phones,
        size(fir_vehicles) AS connected_vehicles,
        size(fir_locations) AS connected_locations,
        size(fir_accounts) AS connected_accounts,

        // Global cases are used only for cross-case intelligence
        size(all_cases) AS connected_cases,

        // FIR evidence types
        [e IN fir_evidence | e.evidence_type] AS evidence_types,

        // Relationship types inside FIR
        [r IN fir_relationships | type(r)] AS relationship_types,

        // FIR evidence IDs
        [e IN fir_evidence | e.id] AS evidence_ids
    """

    with driver.session() as session:
        record = session.run(
            query,
            person_id=person_id,
            case_id=canonical_case_id,
        ).single()

        if not record:
            return empty_person_features(person_id)

        data = dict(record)

    evidence_types = [
        x for x in (data.get("evidence_types") or [])
        if x
    ]

    relationship_types = [
        x for x in (data.get("relationship_types") or [])
        if x
    ]

    # --------------------------------------------------------
    # FIR-SPECIFIC EVIDENCE COUNTS
    # --------------------------------------------------------

    evidence_counter = Counter(evidence_types)

    fir_evidence_count = len(evidence_types)

    cdr_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "CDR" in evidence_type.upper()
    )

    cctv_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "CCTV" in evidence_type.upper()
    )

    vehicle_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "VEHICLE" in evidence_type.upper()
    )

    court_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "COURT" in evidence_type.upper()
    )

    financial_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "FINANCIAL" in evidence_type.upper()
        or "BANK" in evidence_type.upper()
    )

    location_evidence_count = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "LOCATION" in evidence_type.upper()
    )

    fir_evidence_count_only = sum(
        count
        for evidence_type, count in evidence_counter.items()
        if "FIR" in evidence_type.upper()
    )

    # --------------------------------------------------------
    # FIR-SPECIFIC SIGNALS
    # --------------------------------------------------------

    relationship_type_count = len(set(relationship_types))

    # In this FIR, the person is directly associated with the
    # selected case evidence.
    case_relationship_count = len(
        data.get("evidence_ids") or []
    )

    # Connected cases minus the selected case gives a
    # cross-case signal.
    connected_cases = int(data.get("connected_cases") or 0)

    cross_case_connections = max(
        connected_cases - 1,
        0,
    )

    unique_connections = (
        int(data.get("connected_people") or 0)
        + int(data.get("connected_phones") or 0)
        + int(data.get("connected_vehicles") or 0)
        + int(data.get("connected_locations") or 0)
        + int(data.get("connected_accounts") or 0)
    )

    total_relationships = int(
        data.get("relationship_count") or 0
    )

    degree = total_relationships

    # --------------------------------------------------------
    # RETURN 35-FEATURE STRUCTURE
    # --------------------------------------------------------

    return {
        "unique_connections": unique_connections,
        "total_relationships": total_relationships,
        "degree": degree,

        "connected_people": int(
            data.get("connected_people") or 0
        ),

        "connected_phones": int(
            data.get("connected_phones") or 0
        ),

        "connected_vehicles": int(
            data.get("connected_vehicles") or 0
        ),

        "connected_locations": int(
            data.get("connected_locations") or 0
        ),

        "connected_accounts": int(
            data.get("connected_accounts") or 0
        ),

        "connected_cases": connected_cases,

        "court_cases": court_evidence_count,

        "evidence_count": fir_evidence_count,

        "fir_evidence_count": fir_evidence_count_only,

        "cdr_evidence_count": cdr_evidence_count,

        "cctv_evidence_count": cctv_evidence_count,

        "vehicle_evidence_count": vehicle_evidence_count,

        "court_evidence_count": court_evidence_count,

        "financial_evidence_count": financial_evidence_count,

        "location_evidence_count": location_evidence_count,

        "source_layer_count": len(
            set(evidence_types)
        ),

        "relationship_type_count": relationship_type_count,

        "case_relationship_count": case_relationship_count,

        "cross_case_connections": cross_case_connections,

        "cdr_call_count": cdr_evidence_count,

        "cdr_unique_contacts": int(
            data.get("connected_phones") or 0
        ),

        "cdr_total_duration": 0,

        "cctv_observation_count": cctv_evidence_count,

        "cctv_unique_locations": int(
            data.get("connected_locations") or 0
        ),

        "cctv_vehicle_links": int(
            data.get("connected_vehicles") or 0
        ),

        "vehicle_links": int(
            data.get("connected_vehicles") or 0
        ),

        "unique_vehicles": int(
            data.get("connected_vehicles") or 0
        ),

        "location_links": int(
            data.get("connected_locations") or 0
        ),

        "unique_locations": int(
            data.get("connected_locations") or 0
        ),

        "financial_transaction_count": financial_evidence_count,

        "financial_total_amount": 0,

        "temporal_span_days": 0,

        # Extra useful metadata
        "_evidence_types": evidence_types,
        "_relationship_types": relationship_types,
        "_evidence_ids": data.get("evidence_ids") or [],
    }


def empty_person_features(person_id: str) -> Dict[str, Any]:
    """
    Return a valid zero-filled Layer 1 feature object.
    """

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
        "_evidence_types": [],
        "_relationship_types": [],
        "_evidence_ids": [],
    }


# ============================================================
# SUPPORTING RELATIONSHIPS
# ============================================================

def get_supporting_relationships(
    person_id: str,
    case_id: str,
) -> List[Dict[str, Any]]:
    """
    Return relationships that support the person's relevance
    specifically within the selected FIR.
    """

    canonical_case_id = normalize_case_id(case_id)

    query = """
    MATCH (c:Case {id: $case_id})
    MATCH (c)-[:BELONGS_TO]-(e:Evidence)
    MATCH (p:Person {canonical_id: $person_id})-[r]-(e)

    RETURN DISTINCT
        type(r) AS relationship_type,
        coalesce(e.evidence_type, "UNKNOWN") AS evidence_type,
        e.id AS evidence_id

    ORDER BY evidence_type, relationship_type
    LIMIT 100
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=canonical_case_id,
            person_id=person_id,
        )

        return [dict(record) for record in result]


# ============================================================
# RELEVANT CASES
# ============================================================

def get_relevant_case_ids(
    case_id: str,
    person_id: str | None = None,
) -> List[str]:
    """
    Find other cases connected through the same person/evidence
    network.
    """

    canonical_case_id = normalize_case_id(case_id)

    if person_id:
        query = """
        MATCH (p:Person {canonical_id: $person_id})
        MATCH (p)-[]-(e:Evidence)
        MATCH (e)-[:BELONGS_TO]-(other_case:Case)

        WHERE other_case.id <> $case_id

        RETURN DISTINCT other_case.id AS case_id
        ORDER BY case_id
        """

        params = {
            "person_id": person_id,
            "case_id": canonical_case_id,
        }

    else:
        query = """
        MATCH (seed:Case {id: $case_id})
        MATCH (seed)-[:BELONGS_TO]-(seed_evidence:Evidence)
        MATCH (seed_evidence)-[]-(person:Person)
        MATCH (person)-[]-(other_evidence:Evidence)
        MATCH (other_evidence)-[:BELONGS_TO]-(other_case:Case)

        WHERE other_case.id <> seed.id

        RETURN DISTINCT other_case.id AS case_id
        ORDER BY case_id
        """

        params = {
            "case_id": canonical_case_id,
        }

    with driver.session() as session:
        result = session.run(
            query,
            **params,
        )

        return [
            record["case_id"]
            for record in result
        ]


# ============================================================
# PERSON TIMELINE
# ============================================================

def get_person_timeline(
    person_id: str,
    case_id: str,
) -> List[Dict[str, Any]]:
    """
    Return timeline/evidence information for the selected FIR.
    """

    canonical_case_id = normalize_case_id(case_id)

    query = """
    MATCH (c:Case {id: $case_id})
    MATCH (c)-[:BELONGS_TO]-(e:Evidence)
    MATCH (p:Person {canonical_id: $person_id})-[]-(e)

    RETURN DISTINCT
        e.id AS evidence_id,
        e.evidence_type AS evidence_type,
        e.created_at AS timestamp

    ORDER BY timestamp
    LIMIT 100
    """

    with driver.session() as session:
        result = session.run(
            query,
            case_id=canonical_case_id,
            person_id=person_id,
        )

        return [dict(record) for record in result]


# ============================================================
# SIGNAL GENERATION
# ============================================================

def get_person_signals(
    features: Dict[str, Any],
) -> List[str]:
    """
    Generate investigator-facing signals from FIR-specific
    features.
    """

    signals = []

    if features["case_relationship_count"] > 0:
        signals.append(
            "Direct evidence association with selected FIR"
        )

    if features["connected_people"] >= 2:
        signals.append(
            "Multiple person connections within FIR evidence"
        )

    if features["connected_phones"] > 0:
        signals.append(
            "Phone-related evidence connection"
        )

    if features["connected_vehicles"] > 0:
        signals.append(
            "Vehicle-related evidence connection"
        )

    if features["connected_locations"] > 0:
        signals.append(
            "Location-related evidence connection"
        )

    if features["financial_evidence_count"] > 0:
        signals.append(
            "Financial evidence connection"
        )

    if features["cctv_evidence_count"] > 0:
        signals.append(
            "CCTV evidence connection"
        )

    if features["cdr_evidence_count"] > 0:
        signals.append(
            "CDR evidence connection"
        )

    if features["cross_case_connections"] > 0:
        signals.append(
            "Cross-case association detected"
        )

    if features["source_layer_count"] >= 3:
        signals.append(
            "Multiple evidence source types"
        )

    return signals


# ============================================================
# RELEVANCE SCORE
# ============================================================

def calculate_relevance_score(
    features: Dict[str, Any],
) -> float:
    """
    FIR-SCOPED investigation relevance score.

    This is NOT:
        - probability of guilt
        - probability of crime
        - ML confidence
        - model accuracy

    It is a ranking score used to prioritize investigative
    attention.
    """

    # --------------------------------------------------------
    # FIR-SPECIFIC COMPONENTS
    # --------------------------------------------------------

    direct_evidence = min(
        features["case_relationship_count"] / 10.0,
        1.0,
    )

    fir_relationships = min(
        features["total_relationships"] / 15.0,
        1.0,
    )

    cdr_signal = min(
        features["cdr_evidence_count"] / 5.0,
        1.0,
    )

    cctv_signal = min(
        features["cctv_evidence_count"] / 5.0,
        1.0,
    )

    financial_signal = min(
        features["financial_evidence_count"] / 5.0,
        1.0,
    )

    vehicle_location_signal = min(
        (
            features["vehicle_evidence_count"]
            + features["location_evidence_count"]
        ) / 8.0,
        1.0,
    )

    cross_case_signal = min(
        features["cross_case_connections"] / 5.0,
        1.0,
    )

    # --------------------------------------------------------
    # WEIGHTS
    # --------------------------------------------------------

    score = (
        direct_evidence * 30.0
        + fir_relationships * 20.0
        + cdr_signal * 10.0
        + cctv_signal * 10.0
        + financial_signal * 10.0
        + vehicle_location_signal * 10.0
        + cross_case_signal * 10.0
    )

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


# ============================================================
# ANOMALY DETECTION
# ============================================================

def calculate_anomaly(
    features: Dict[str, Any],
) -> List[str]:
    """
    Simple graph-derived anomaly indicators.

    These are investigative indicators, not crime predictions.
    """

    indicators = []

    if (
        features["cross_case_connections"] >= 3
    ):
        indicators.append(
            "Strong cross-case association"
        )

    if (
        features["source_layer_count"] >= 4
    ):
        indicators.append(
            "Activity spans multiple evidence sources"
        )

    if (
        features["connected_people"] >= 4
    ):
        indicators.append(
            "High person connectivity within FIR"
        )

    if (
        features["connected_phones"] >= 2
    ):
        indicators.append(
            "Multiple phone connections"
        )

    if (
        features["connected_vehicles"] >= 2
    ):
        indicators.append(
            "Multiple vehicle connections"
        )

    if (
        features["financial_evidence_count"] > 0
        and features["cdr_evidence_count"] > 0
        and features["cctv_evidence_count"] > 0
    ):
        indicators.append(
            "Convergence across financial, CDR and CCTV evidence"
        )

    return indicators


# ============================================================
# INVESTIGATOR MESSAGE
# ============================================================

def generate_investigator_message(
    case_id: str,
    ranked_candidates: List[Dict[str, Any]],
    anomaly_indicators: List[str],
) -> str:
    """
    Generate a deterministic investigator-facing summary.

    This is intentionally rule-based for the current prototype.
    It is NOT a real LLM call.
    """

    if not ranked_candidates:
        return (
            f"No relevant connected persons were identified "
            f"for {case_id}."
        )

    top = ranked_candidates[0]

    name = top["name"]
    score = top["relevance_score"]

    features = top["features"]

    evidence_count = features["evidence_count"]
    cross_case = features["cross_case_connections"]
    sources = features["source_layer_count"]

    message = (
        f"For {case_id}, {name} currently has the highest "
        f"investigation relevance score ({score}/100). "
        f"The ranking is supported by {evidence_count} "
        f"FIR-linked evidence connection(s), "
        f"{sources} evidence source type(s), and "
        f"{cross_case} cross-case connection(s)."
    )

    if anomaly_indicators:
        message += (
            f" The analysis also identified "
            f"{len(anomaly_indicators)} investigative "
            f"anomaly indicator(s) requiring review."
        )

    message += (
        " This score is an investigative prioritization signal "
        "and does not represent a determination of guilt."
    )

    return message


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_investigation(
    case_id: str,
) -> Dict[str, Any]:
    """
    Main FIR-specific investigation analysis.

    Pipeline:

        Selected FIR
             ↓
        FIR evidence
             ↓
        FIR people
             ↓
        FIR-connected candidates
             ↓
        FIR-specific features
             ↓
        relevance score
             ↓
        anomaly indicators
             ↓
        top 5
    """

    canonical_case_id = normalize_case_id(case_id)

    # --------------------------------------------------------
    # 1. DIRECT PEOPLE
    # --------------------------------------------------------

    seed_people = get_case_people(
        canonical_case_id
    )

    if not seed_people:
        return {
            "case_id": case_id,
            "seed_people": [],
            "candidate_count": 0,
            "overall_relevance_score": 0,
            "top_relevant_people": [],
            "anomaly": {
                "present": False,
                "indicator_count": 0,
                "indicators": [],
            },
            "llm_message": (
                f"No people were found directly connected "
                f"to {case_id}."
            ),
        }

    # --------------------------------------------------------
    # 2. CANDIDATES
    # --------------------------------------------------------

    candidate_people = get_candidate_people(
        canonical_case_id
    )

    # Add direct FIR people too, so they can be ranked.
    all_candidates: Dict[str, Dict[str, Any]] = {}

    for person in seed_people:
        if person.get("person_id"):
            all_candidates[
                person["person_id"]
            ] = {
                "person_id": person["person_id"],
                "name": person.get("name")
                or person["person_id"],
                "direct_case_person": True,
            }

    for person in candidate_people:
        if person.get("person_id"):
            if person["person_id"] not in all_candidates:
                all_candidates[
                    person["person_id"]
                ] = {
                    "person_id": person["person_id"],
                    "name": person.get("name")
                    or person["person_id"],
                    "direct_case_person": False,
                }

    # --------------------------------------------------------
    # 3. FEATURE EXTRACTION + SCORING
    # --------------------------------------------------------

    ranked_candidates = []

    for person_id, candidate in all_candidates.items():

        features = get_person_features(
            person_id=person_id,
            case_id=canonical_case_id,
        )

        score = calculate_relevance_score(
            features
        )

        signals = get_person_signals(
            features
        )

        supporting_relationships = (
            get_supporting_relationships(
                person_id=person_id,
                case_id=canonical_case_id,
            )
        )

        timeline = get_person_timeline(
            person_id=person_id,
            case_id=canonical_case_id,
        )

        relevant_cases = get_relevant_case_ids(
            canonical_case_id,
            person_id=person_id,
        )

        ranked_candidates.append(
            {
                "person_id": person_id,
                "name": candidate["name"],
                "relevance_score": score,

                "direct_case_person": candidate[
                    "direct_case_person"
                ],

                "signals": signals,

                "features": features,

                "supporting_relationships":
                    supporting_relationships,

                "timeline": timeline,

                "relevant_cases":
                    relevant_cases,
            }
        )

    # --------------------------------------------------------
    # 4. SORT
    # --------------------------------------------------------

    ranked_candidates.sort(
        key=lambda item: item["relevance_score"],
        reverse=True,
    )

    # --------------------------------------------------------
    # 5. TOP 5
    # --------------------------------------------------------

    top_people = ranked_candidates[:5]

    # --------------------------------------------------------
    # 6. OVERALL SCORE
    # --------------------------------------------------------

    if top_people:
        overall_score = round(
            sum(
                person["relevance_score"]
                for person in top_people
            ) / len(top_people),
            2,
        )
    else:
        overall_score = 0

    # --------------------------------------------------------
    # 7. ANOMALY AGGREGATION
    # --------------------------------------------------------

    anomaly_counter = Counter()

    for person in ranked_candidates:
        person_anomalies = calculate_anomaly(
            person["features"]
        )

        for indicator in person_anomalies:
            anomaly_counter[indicator] += 1

    anomaly_indicators = list(
        anomaly_counter.keys()
    )

    # --------------------------------------------------------
    # 8. LLM-STYLE INVESTIGATOR MESSAGE
    # --------------------------------------------------------

    llm_message = generate_investigator_message(
        case_id=case_id,
        ranked_candidates=top_people,
        anomaly_indicators=anomaly_indicators,
    )

    # --------------------------------------------------------
    # 9. CLEAN INTERNAL FIELDS
    # --------------------------------------------------------

    for person in ranked_candidates:

        # Keep the 35 features but remove internal metadata
        # from the API response.
        person["features"] = {
            key: value
            for key, value in person["features"].items()
            if not key.startswith("_")
        }

    # --------------------------------------------------------
    # 10. RESPONSE
    # --------------------------------------------------------

    return {
        "case_id": case_id,

        "seed_people": seed_people,

        "candidate_count": len(
            ranked_candidates
        ),

        "overall_relevance_score": overall_score,

        "top_relevant_people": top_people,

        "anomaly": {
            "present": len(anomaly_indicators) >= 2,
            "indicator_count": len(
                anomaly_indicators
            ),
            "indicators": anomaly_indicators,
        },

        "llm_message": llm_message,
    }