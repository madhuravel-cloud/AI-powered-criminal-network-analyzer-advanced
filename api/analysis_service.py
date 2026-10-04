from database.neo4j_connection import driver


# =========================================================
# CASE ID NORMALIZATION
# =========================================================

def normalize_case_id(case_id: str) -> str:
    if case_id.startswith("case:"):
        return case_id

    return f"case:{case_id}"


# =========================================================
# TIMESTAMP HELPER
# =========================================================

def serialize_timestamp(value):
    """
    Safely convert Neo4j datetime/date/string values
    into JSON-compatible strings.
    """

    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


# =========================================================
# SEED PEOPLE
# =========================================================

def get_case_people(case_id: str):

    query = """
    MATCH (p:Person)-[r:RELATED]-(n)
    WHERE r.case_id = $case_id

    RETURN DISTINCT
        p.canonical_id AS person_id,
        p.name AS name

    ORDER BY p.name
    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        return [
            {
                "person_id": record["person_id"],
                "name": record["name"]
            }
            for record in result
        ]


# =========================================================
# CANDIDATE DISCOVERY
# =========================================================

def get_candidate_people(case_id: str):

    query = """
    MATCH (seed:Person)-[r1:RELATED]-(n)
    WHERE r1.case_id = $case_id

    MATCH (candidate:Person)-[r2]-(connected)
    WHERE candidate <> seed

    RETURN DISTINCT
        candidate.canonical_id AS person_id,
        candidate.name AS name
    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        return [
            {
                "person_id": record["person_id"],
                "name": record["name"]
            }
            for record in result
        ]


# =========================================================
# CANDIDATE FEATURES
# =========================================================

def calculate_candidate_features(
    person_id: str,
    case_id: str
):

    # -----------------------------------------------------
    # GLOBAL GRAPH FEATURES
    # -----------------------------------------------------

    query = """
    MATCH (p:Person {canonical_id: $person_id})

    OPTIONAL MATCH (p)-[r]-(n)

    WITH
        p,
        collect(DISTINCT n) AS neighbors,
        collect(DISTINCT r) AS relationships

    RETURN

        size(neighbors)
            AS unique_connections,

        size(relationships)
            AS total_relationships,

        size([
            x IN neighbors
            WHERE x:Person
        ])
            AS connected_people,

        size([
            x IN neighbors
            WHERE x:Phone
        ])
            AS connected_phones,

        size([
            x IN neighbors
            WHERE x:Vehicle
        ])
            AS connected_vehicles,

        size([
            x IN neighbors
            WHERE x:Location
        ])
            AS connected_locations,

        size([
            x IN neighbors
            WHERE x:Account
        ])
            AS connected_accounts,

        size([
            x IN neighbors
            WHERE x:Case
        ])
            AS connected_cases
    """

    with driver.session() as session:

        record = session.run(
            query,
            person_id=person_id
        ).single()

    if not record:
        return {}

    features = dict(record)

    # -----------------------------------------------------
    # CURRENT CASE RELATIONSHIPS
    # -----------------------------------------------------

    case_query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id = $case_id

    RETURN count(r)
        AS case_relationship_count
    """

    with driver.session() as session:

        record = session.run(
            case_query,
            person_id=person_id,
            case_id=case_id
        ).single()

    features["case_relationship_count"] = (
        record["case_relationship_count"]
        if record
        else 0
    )

    # -----------------------------------------------------
    # CROSS CASE CONNECTIONS
    # -----------------------------------------------------

    cross_case_query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id IS NOT NULL
      AND r.case_id <> $case_id

    RETURN count(r)
        AS cross_case_connections
    """

    with driver.session() as session:

        record = session.run(
            cross_case_query,
            person_id=person_id,
            case_id=case_id
        ).single()

    features["cross_case_connections"] = (
        record["cross_case_connections"]
        if record
        else 0
    )

    # -----------------------------------------------------
    # CONNECTED CASE COUNT
    # -----------------------------------------------------

    connected_case_query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id IS NOT NULL

    RETURN count(DISTINCT r.case_id)
        AS connected_cases
    """

    with driver.session() as session:

        record = session.run(
            connected_case_query,
            person_id=person_id
        ).single()

    features["connected_cases"] = (
        record["connected_cases"]
        if record
        else 0
    )

    return features


# =========================================================
# RELEVANCE SCORE
# =========================================================

def calculate_relevance(features):

    """
    Prototype investigation relevance score.

    IMPORTANT:
    This is NOT probability of guilt.
    This is NOT a criminality score.

    It ranks how relevant a person may be
    to the current investigation based on
    graph-derived evidence features.
    """

    if not features:
        return 0.0

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

        value = features.get(
            feature,
            0
        ) or 0

        normalized = value / (value + 5)

        score += normalized * weight

    return round(
        score * 100,
        2
    )


# =========================================================
# SUPPORTING RELATIONSHIPS
# =========================================================

def get_supporting_relationships(
    person_id: str,
    case_id: str
):

    query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id = $case_id

    RETURN

        type(r)
            AS graph_relationship,

        r.relationship_type
            AS relationship_type,

        n.canonical_id
            AS connected_entity_id,

        coalesce(
            n.name,
            n.canonical_id
        )
            AS connected_entity,

        r.source_layer
            AS source_layer,

        r.timestamp
            AS timestamp,

        r.evidence_id
            AS evidence_id,

        r.confidence
            AS confidence

    ORDER BY r.timestamp
    """

    with driver.session() as session:

        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id
        )

        relationships = []

        for record in result:

            relationships.append(
                {
                    "graph_relationship":
                        record["graph_relationship"],

                    "relationship_type":
                        record["relationship_type"],

                    "connected_entity_id":
                        record["connected_entity_id"],

                    "connected_entity":
                        record["connected_entity"],

                    "source_layer":
                        record["source_layer"],

                    "timestamp":
                        serialize_timestamp(
                            record["timestamp"]
                        ),

                    "evidence_id":
                        record["evidence_id"],

                    "confidence":
                        record["confidence"],
                }
            )

        return relationships


# =========================================================
# CONNECTED CASES
# =========================================================

def get_connected_cases(
    person_id: str
):

    query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id IS NOT NULL

    RETURN DISTINCT
        r.case_id AS case_id

    ORDER BY case_id
    """

    with driver.session() as session:

        result = session.run(
            query,
            person_id=person_id
        )

        return [
            record["case_id"]
            for record in result
            if record["case_id"]
        ]


# =========================================================
# SOURCE LAYERS
# =========================================================

def get_source_layers(
    person_id: str,
    case_id: str
):

    query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id = $case_id
      AND r.source_layer IS NOT NULL

    RETURN DISTINCT
        r.source_layer AS source_layer

    ORDER BY source_layer
    """

    with driver.session() as session:

        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id
        )

        return [
            record["source_layer"]
            for record in result
            if record["source_layer"]
        ]


# =========================================================
# EVIDENCE IDS
# =========================================================

def get_evidence_ids(
    person_id: str,
    case_id: str
):

    query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id = $case_id
      AND r.evidence_id IS NOT NULL

    RETURN DISTINCT
        r.evidence_id AS evidence_id

    ORDER BY evidence_id
    """

    with driver.session() as session:

        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id
        )

        return [
            record["evidence_id"]
            for record in result
            if record["evidence_id"]
        ]


# =========================================================
# TIMELINE
# =========================================================

def get_timeline(
    person_id: str,
    case_id: str
):

    query = """
    MATCH (p:Person {canonical_id: $person_id})-[r]-(n)

    WHERE r.case_id = $case_id
      AND r.timestamp IS NOT NULL

    RETURN

        r.timestamp
            AS timestamp,

        r.relationship_type
            AS relationship_type,

        r.source_layer
            AS source_layer,

        n.canonical_id
            AS connected_entity_id,

        coalesce(
            n.name,
            n.canonical_id
        )
            AS connected_entity,

        r.evidence_id
            AS evidence_id

    ORDER BY r.timestamp
    """

    with driver.session() as session:

        result = session.run(
            query,
            person_id=person_id,
            case_id=case_id
        )

        timeline = []

        for record in result:

            timeline.append(
                {
                    "timestamp":
                        serialize_timestamp(
                            record["timestamp"]
                        ),

                    "relationship_type":
                        record["relationship_type"],

                    "source_layer":
                        record["source_layer"],

                    "connected_entity_id":
                        record["connected_entity_id"],

                    "connected_entity":
                        record["connected_entity"],

                    "evidence_id":
                        record["evidence_id"],
                }
            )

        return timeline


# =========================================================
# INVESTIGATION SIGNALS
# =========================================================

def generate_signals(
    features,
    source_layers,
    connected_cases
):

    signals = []

    # -----------------------------------------------------
    # DIRECT CASE CONNECTION
    # -----------------------------------------------------

    if features.get(
        "case_relationship_count",
        0
    ) > 0:

        signals.append(
            "Direct relationship with the investigation case"
        )

    # -----------------------------------------------------
    # CROSS CASE
    # -----------------------------------------------------

    if features.get(
        "cross_case_connections",
        0
    ) > 0:

        signals.append(
            "Connections detected across other cases"
        )

    # -----------------------------------------------------
    # PEOPLE
    # -----------------------------------------------------

    if features.get(
        "connected_people",
        0
    ) >= 3:

        signals.append(
            "Multiple person-to-person connections detected"
        )

    # -----------------------------------------------------
    # LOCATIONS
    # -----------------------------------------------------

    if features.get(
        "connected_locations",
        0
    ) >= 2:

        signals.append(
            "Multiple location associations detected"
        )

    # -----------------------------------------------------
    # VEHICLES
    # -----------------------------------------------------

    if features.get(
        "connected_vehicles",
        0
    ) > 0:

        signals.append(
            "Vehicle association detected"
        )

    # -----------------------------------------------------
    # ACCOUNTS
    # -----------------------------------------------------

    if features.get(
        "connected_accounts",
        0
    ) > 0:

        signals.append(
            "Financial account association detected"
        )

    # -----------------------------------------------------
    # MULTI SOURCE
    # -----------------------------------------------------

    if len(source_layers) >= 3:

        signals.append(
            "Evidence spans multiple source layers"
        )

    # -----------------------------------------------------
    # MULTI CASE
    # -----------------------------------------------------

    if len(connected_cases) >= 2:

        signals.append(
            "Person appears across multiple cases"
        )

    return signals


# =========================================================
# FULL INVESTIGATION ANALYSIS
# =========================================================

def analyze_investigation(
    case_id: str
):

    case_id = normalize_case_id(
        case_id
    )

    # -----------------------------------------------------
    # GET SEED PEOPLE
    # -----------------------------------------------------

    case_people = get_case_people(
        case_id
    )

    # -----------------------------------------------------
    # DISCOVER CANDIDATES
    # -----------------------------------------------------

    candidates = get_candidate_people(
        case_id
    )

    results = []

    # -----------------------------------------------------
    # ANALYZE EACH CANDIDATE
    # -----------------------------------------------------

    for candidate in candidates:

        person_id = candidate["person_id"]

        # ---------------------------------------------
        # FEATURES
        # ---------------------------------------------

        features = calculate_candidate_features(
            person_id,
            case_id
        )

        # ---------------------------------------------
        # RELEVANCE
        # ---------------------------------------------

        relevance = calculate_relevance(
            features
        )

        # ---------------------------------------------
        # RELATIONSHIPS
        # ---------------------------------------------

        supporting_relationships = (
            get_supporting_relationships(
                person_id,
                case_id
            )
        )

        # ---------------------------------------------
        # CONNECTED CASES
        # ---------------------------------------------

        connected_cases = get_connected_cases(
            person_id
        )

        # ---------------------------------------------
        # SOURCE LAYERS
        # ---------------------------------------------

        source_layers = get_source_layers(
            person_id,
            case_id
        )

        # ---------------------------------------------
        # EVIDENCE
        # ---------------------------------------------

        evidence_ids = get_evidence_ids(
            person_id,
            case_id
        )

        # ---------------------------------------------
        # TIMELINE
        # ---------------------------------------------

        timeline = get_timeline(
            person_id,
            case_id
        )

        # ---------------------------------------------
        # INVESTIGATION SIGNALS
        # ---------------------------------------------

        signals = generate_signals(
            features,
            source_layers,
            connected_cases
        )

        # ---------------------------------------------
        # FINAL CANDIDATE RESULT
        # ---------------------------------------------

        results.append(
            {
                "person_id":
                    person_id,

                "name":
                    candidate["name"],

                "relevance_score":
                    relevance,

                "features":
                    features,

                "supporting_relationships":
                    supporting_relationships,

                "connected_cases":
                    connected_cases,

                "source_layers":
                    source_layers,

                "evidence_ids":
                    evidence_ids,

                "timeline":
                    timeline,

                "signals":
                    signals,
            }
        )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    results.sort(
        key=lambda x:
            x["relevance_score"],
        reverse=True
    )

    # -----------------------------------------------------
    # TOP 5
    # -----------------------------------------------------

    top_five = results[:5]

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {
        "case_id":
            case_id,

        "seed_people":
            case_people,

        "candidate_count":
            len(results),

        "top_relevant_people":
            top_five,
    }