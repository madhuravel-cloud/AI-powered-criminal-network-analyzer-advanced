const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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