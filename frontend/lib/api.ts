const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";


// =========================================================
// ANALYSIS TYPES
// =========================================================

export interface SeedPerson {
    person_id: string;
    name: string;
}

export interface FeatureSet {
    unique_connections: number;
    total_relationships: number;
    connected_people: number;
    connected_phones: number;
    connected_vehicles: number;
    connected_locations: number;
    connected_accounts: number;
    connected_cases: number;
    case_relationship_count: number;
    cross_case_connections: number;
}

export interface SupportingRelationship {
    graph_relationship: string;
    relationship_type: string | null;
    connected_entity_id: string | null;
    connected_entity: string | null;
    source_layer: string | null;
    timestamp: string | null;
    evidence_id: string | null;
    confidence: number | null;
}

export interface TimelineEvent {
    timestamp: string | null;
    relationship_type: string | null;
    source_layer: string | null;
    connected_entity_id: string | null;
    connected_entity: string | null;
    evidence_id: string | null;
}

export interface Candidate {
    person_id: string;
    name: string;
    relevance_score: number;
    features: FeatureSet;
    supporting_relationships: SupportingRelationship[];
    connected_cases: string[];
    source_layers: string[];
    evidence_ids: string[];
    timeline: TimelineEvent[];
    signals: string[];
}

export interface InvestigationAnalysis {
    case_id: string;
    seed_people: SeedPerson[];
    candidate_count: number;
    top_relevant_people: Candidate[];
}

export interface AnalysisResponse {
    status: string;
    analysis: InvestigationAnalysis;
}


// =========================================================
// CASE TYPES
// =========================================================

export interface CaseData {
    id: string;
    fir_number: string | null;
    case_type: string | null;
    police_station: string | null;
    incident_date: string | null;
    registered_date: string | null;
    status: string | null;
    created_at: string | null;
    evidence_count: number;
    relationship_count: number;
}

export interface CasesResponse {
    status: string;
    count: number;
    cases: CaseData[];
}

export interface CaseResponse {
    status: string;
    case: CaseData;
}


// =========================================================
// ANALYSIS API
// =========================================================

export async function analyzeInvestigation(
    caseId: string
): Promise<AnalysisResponse> {

    const response = await fetch(
        `${API_BASE_URL}/investigations/${encodeURIComponent(
            caseId
        )}/analyze`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    if (!response.ok) {

        const errorText = await response.text();

        throw new Error(
            `Analysis failed (${response.status}): ${errorText}`
        );
    }

    return response.json();
}


// =========================================================
// GET ALL CASES
// =========================================================

export async function getCases(): Promise<CaseData[]> {

    const response = await fetch(
        `${API_BASE_URL}/cases`,
        {
            method: "GET",
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText = await response.text();

        throw new Error(
            `Failed to fetch cases (${response.status}): ${errorText}`
        );
    }

    const data: CasesResponse = await response.json();

    return data.cases;
}


// =========================================================
// GET SINGLE CASE
// =========================================================

export async function getCase(
    caseId: string
): Promise<CaseData> {

    const response = await fetch(
        `${API_BASE_URL}/cases/${encodeURIComponent(caseId)}`,
        {
            method: "GET",
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText = await response.text();

        throw new Error(
            `Failed to fetch case (${response.status}): ${errorText}`
        );
    }

    const data: CaseResponse = await response.json();

    return data.case;
}
// =========================================================
// DASHBOARD
// =========================================================

export interface DashboardStatistics {
    total_cases: number;
    active_cases: number;
    total_people: number;
    total_entities: number;
    total_evidence: number;
    total_relationships: number;
}

export interface DashboardCaseType {
    type: string;
    count: number;
}

export interface DashboardEvidenceSource {
    type: string;
    count: number;
}

export interface DashboardRecentCase {
    id: string;
    fir_number: string | null;
    case_type: string | null;
    police_station: string | null;
    status: string | null;
    incident_date: string | null;
    created_at: string | null;
    evidence_count: number;
    relationship_count: number;
}

export interface DashboardResponse {
    status: string;

    statistics: DashboardStatistics;

    case_types: DashboardCaseType[];

    evidence_sources: DashboardEvidenceSource[];

    recent_cases: DashboardRecentCase[];
}


export async function getDashboard(): Promise<DashboardResponse> {

    const response = await fetch(
        `${API_BASE_URL}/dashboard`,
        {
            method: "GET",
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText = await response.text();

        throw new Error(
            `Failed to fetch dashboard (${response.status}): ${errorText}`
        );
    }

    return response.json();
}
export interface NetworkNode {
    id: string;
    neo4j_id: string;
    label: string;
    type: string;
    labels: string[];
    source_layer: string | null;
    properties: Record<string, unknown>;
}

export interface NetworkEdge {
    id: string;
    source: string;
    target: string;
    type: string;
    source_layer: string | null;
    properties: Record<string, unknown>;
}

export interface NetworkFeatures {
    degree: number;
    unique_connections: number;
    total_relationships: number;

    connected_people: number;
    connected_phones: number;
    connected_vehicles: number;
    connected_locations: number;
    connected_accounts: number;
    connected_cases: number;

    indirect_connections: number;

    case_relationship_count: number;
    cross_case_connections: number;

    cdr_call_count: number;

    relationship_type_count: number;

    case_ids: string[];

    source_layer_count: number;
    source_layers: string[];

    node_type: string;
}

export interface NetworkGraphMetrics {
    degree_centrality: number;
    betweenness_centrality: number;
    closeness_centrality: number;
}

export interface NetworkSignal {
    type: string;
    severity: "HIGH" | "MEDIUM" | "LOW";
    message: string;
}

export interface NetworkCandidate {
    id: string;
    label: string;
    type: string;
    source_layer: string | null;
    properties: Record<string, unknown>;

    features: NetworkFeatures;

    graph_metrics?: NetworkGraphMetrics;

    relevance_score: number;

    signals: NetworkSignal[];
}

export interface NetworkGraph {
    nodes: NetworkNode[];
    edges: NetworkEdge[];

    node_count: number;
    edge_count: number;

    total_nodes: number;
    total_relationships: number;
}

export interface NetworkResponse {
    status: string;

    investigation: {
        case_id: string | null;
        case_found: boolean;
        seed_count: number;
    };

    graph: NetworkGraph;

    analysis: {
        candidate_count: number;
        top_leads: NetworkCandidate[];
    };

    engine: {
        graph_engine: string;
        source_graph: string;
        analysis_type: string;
    };
}

export async function getNetwork(
    options?: {
        caseId?: string;
        entityType?: string;
        sourceLayer?: string;
        search?: string;
        limit?: number;
    }
): Promise<NetworkResponse> {

    const params = new URLSearchParams();

    if (options?.caseId) {
        params.set(
            "case_id",
            options.caseId
        );
    }

    if (options?.entityType) {
        params.set(
            "entity_type",
            options.entityType
        );
    }

    if (options?.sourceLayer) {
        params.set(
            "source_layer",
            options.sourceLayer
        );
    }

    if (options?.search) {
        params.set(
            "search",
            options.search
        );
    }

    if (options?.limit) {
        params.set(
            "limit",
            options.limit.toString()
        );
    }

    const query = params.toString();

    const response = await fetch(
        `${API_BASE_URL}/network${query ? `?${query}` : ""
        }`,
        {
            method: "GET",
            cache: "no-store",
        }
    );

    if (!response.ok) {
        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch network analysis (${response.status}): ${errorText}`
        );
    }

    return response.json();
}