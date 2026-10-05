const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";


// ============================================================
// CASES
// ============================================================

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


export interface RelevantCasesResponse {
    status: string;
    seed_case: string;
    count: number;
    cases: CaseData[];
}


export async function getCases(): Promise<CaseData[]> {

    const response = await fetch(
        `${API_BASE_URL}/cases`,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch cases (${response.status}): ${errorText}`
        );
    }

    const data: CasesResponse =
        await response.json();

    return data.cases;
}


export async function getCase(
    caseId: string
): Promise<CaseData> {

    const response = await fetch(
        `${API_BASE_URL}/cases/${encodeURIComponent(caseId)}`,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch case (${response.status}): ${errorText}`
        );
    }

    const data: CaseResponse =
        await response.json();

    return data.case;
}


export async function getRelevantCases(
    caseId: string
): Promise<CaseData[]> {

    const response = await fetch(
        `${API_BASE_URL}/cases/relevant/${encodeURIComponent(caseId)}`,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch relevant cases (${response.status}): ${errorText}`
        );
    }

    const data: RelevantCasesResponse =
        await response.json();

    return data.cases;
}


// ============================================================
// DASHBOARD
// ============================================================

export interface DashboardStatistics {
    total_cases: number;
    active_cases: number;
    total_people: number;
    total_entities: number;
    total_evidence: number;
    total_relationships: number;
}


export interface DashboardCase {
    id: string;
    fir_number: string | null;
    case_type: string | null;
    police_station: string | null;
    incident_date: string | null;
    registered_date: string | null;
    status: string | null;
    created_at: string | null;
}


export interface DashboardCaseType {
    type: string;
    count: number;
}


export interface DashboardEvidenceSource {
    type: string;
    count: number;
}


export interface DashboardResponse {
    status: string;
    statistics: DashboardStatistics;
    case_types: DashboardCaseType[];
    evidence_sources: DashboardEvidenceSource[];
    recent_cases: DashboardCase[];
}


export async function getDashboard(): Promise<DashboardResponse> {

    const response = await fetch(
        `${API_BASE_URL}/dashboard`,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch dashboard (${response.status}): ${errorText}`
        );
    }

    return response.json();
}


// ============================================================
// ANALYSIS
// ============================================================

export interface SeedPerson {
    person_id: string;
    name: string;
}


export interface CandidateFeatures {
    unique_connections?: number;
    total_relationships?: number;
    degree?: number;
    connected_people?: number;
    connected_phones?: number;
    connected_vehicles?: number;
    connected_locations?: number;
    connected_accounts?: number;
    connected_cases?: number;
    case_relationship_count?: number;
    cross_case_connections?: number;
    cdr_call_count?: number;
    cdr_unique_contacts?: number;
    cdr_total_duration?: number;
    cctv_observation_count?: number;
    cctv_unique_locations?: number;
    cctv_vehicle_links?: number;
    vehicle_links?: number;
    unique_vehicles?: number;
    location_links?: number;
    unique_locations?: number;
    financial_transaction_count?: number;
    financial_total_amount?: number;
    evidence_count?: number;
    source_layer_count?: number;
    relationship_type_count?: number;
    [key: string]:
    | number
    | string
    | boolean
    | null
    | undefined;
}


export interface SupportingRelationship {
    graph_relationship?: string;
    relationship_type?: string;
    connected_entity_id?: string;
    connected_entity?: string;
    source_layer?: string;
    timestamp?: string;
    evidence_id?: string;
    confidence?: number;
    [key: string]: unknown;
}


export interface TimelineEvent {
    timestamp?: string;
    relationship_type?: string;
    source_layer?: string;
    connected_entity_id?: string;
    connected_entity?: string;
    evidence_id?: string;
    [key: string]: unknown;
}


export interface Candidate {
    person_id?: string;
    name?: string;
    relevance_score?: number;
    features?: CandidateFeatures;
    supporting_relationships?: SupportingRelationship[];
    connected_cases?: string[];
    source_layers?: string[];
    evidence_ids?: string[];
    timeline?: TimelineEvent[];
    signals?: string[];
    [key: string]: unknown;
}


export interface InvestigationAnalysis {
    case_id: string;
    seed_people: SeedPerson[];
    candidate_count: number;
    top_relevant_people: Candidate[];
    [key: string]: unknown;
}


export interface AnalysisResponse {
    status: string;
    analysis: InvestigationAnalysis;
}


export async function analyzeInvestigation(
    caseId: string
): Promise<InvestigationAnalysis> {

    const response = await fetch(
        `${API_BASE_URL}/investigations/${encodeURIComponent(caseId)}/analyze`,
        {
            method: "POST",
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to analyze investigation (${response.status}): ${errorText}`
        );
    }

    const data: AnalysisResponse =
        await response.json();

    return data.analysis;
}


// ============================================================
// EVIDENCE
// ============================================================

export interface EvidenceData {
    id: string;
    case_id: string;
    evidence_type: string | null;
    source: string | null;
    storage_path: string | null;
    extracted_text: string | null;
    file_hash: string | null;
    layer_id: string | null;
    created_at: string | null;
}


export interface EvidenceResponse {
    status: string;
    count: number;
    evidence: EvidenceData[];
}


export interface EvidenceCreate {
    id: string;
    case_id: string;
    evidence_type: string;
    source?: string;
    storage_path?: string;
    extracted_text?: string;
    file_hash?: string;
    layer_id?: string;
}


export async function getEvidence(
    caseId?: string
): Promise<EvidenceData[]> {

    const url = caseId
        ? `${API_BASE_URL}/evidence?case_id=${encodeURIComponent(caseId)}`
        : `${API_BASE_URL}/evidence`;

    const response = await fetch(
        url,
        {
            cache: "no-store",
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to fetch evidence (${response.status}): ${errorText}`
        );
    }

    const data: EvidenceResponse =
        await response.json();

    return data.evidence;
}


export async function createEvidence(
    evidence: EvidenceCreate
): Promise<EvidenceData> {

    const response = await fetch(
        `${API_BASE_URL}/evidence`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(evidence),
        }
    );

    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to create evidence (${response.status}): ${errorText}`
        );
    }

    const data =
        await response.json();

    return data.evidence;
}