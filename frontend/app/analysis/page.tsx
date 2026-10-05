"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
    Activity,
    AlertTriangle,
    ArrowLeft,
    BrainCircuit,
    CheckCircle2,
    Clock3,
    FileSearch,
    GitBranch,
    MapPin,
    Network,
    Phone,
    ShieldAlert,
    Users,
    Car,
    Wallet,
} from "lucide-react";

import {
    analyzeInvestigation,
    getCase,
    type CaseData,
    type Candidate,
    type InvestigationAnalysis,
} from "@/lib/api";


export default function AnalysisPage() {

    const [caseId, setCaseId] =
        useState("");

    const [caseData, setCaseData] =
        useState<CaseData | null>(null);

    const [analysis, setAnalysis] =
        useState<InvestigationAnalysis | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    // ========================================================
    // READ CASE FROM URL
    // ========================================================

    useEffect(() => {

        const params =
            new URLSearchParams(
                window.location.search
            );

        const selectedCase =
            params.get("case");

        if (!selectedCase) {

            setError(
                "No case selected. Please select a case from the Cases page."
            );

            setLoading(false);

            return;
        }

        setCaseId(selectedCase);

        loadAnalysis(selectedCase);

    }, []);


    // ========================================================
    // LOAD REAL ANALYSIS
    // ========================================================

    async function loadAnalysis(
        selectedCase: string
    ) {

        try {

            setLoading(true);
            setError("");

            const [
                caseResult,
                analysisResult,
            ] = await Promise.all([
                getCase(selectedCase),
                analyzeInvestigation(selectedCase),
            ]);

            setCaseData(caseResult);
            setAnalysis(analysisResult);

        } catch (err) {

            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to analyse case."
            );

        } finally {

            setLoading(false);
        }
    }


    // ========================================================
    // REAL LAYER 1 DATA
    // ========================================================

    const topPeople =
        analysis?.top_relevant_people || [];


    const layer1Stats =
        useMemo(() => {

            if (!topPeople.length) {

                return {
                    people: 0,
                    connections: 0,
                    cases: 0,
                    evidence: 0,
                };
            }

            const uniqueCases =
                new Set<string>();

            let connections = 0;
            let evidence = 0;

            for (const person of topPeople) {

                connections +=
                    person.features
                        ?.unique_connections || 0;

                evidence +=
                    person.evidence_ids
                        ?.length || 0;

                for (
                    const connectedCase
                    of person.connected_cases || []
                ) {

                    uniqueCases.add(
                        connectedCase
                    );
                }
            }

            return {
                people: topPeople.length,
                connections,
                cases: uniqueCases.size,
                evidence,
            };

        }, [topPeople]);


    // ========================================================
    // LOADING
    // ========================================================

    if (loading) {

        return (
            <div className="min-h-screen bg-[#05070b] p-8 text-white">

                <div className="flex min-h-[70vh] items-center justify-center">

                    <div className="text-center">

                        <Activity
                            size={28}
                            className="mx-auto animate-spin text-cyan-400"
                        />

                        <p className="mt-4 text-sm text-white/40">
                            Running investigation analysis...
                        </p>

                        <p className="mt-2 text-xs text-white/20">
                            Extracting Layer 1 intelligence from the master graph
                        </p>

                    </div>

                </div>

            </div>
        );
    }


    // ========================================================
    // ERROR
    // ========================================================

    if (error) {

        return (
            <div className="min-h-screen bg-[#05070b] p-8 text-white">

                <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-8">

                    <div className="flex items-center gap-3">

                        <AlertTriangle
                            size={22}
                            className="text-red-400"
                        />

                        <h1 className="text-xl font-semibold">
                            Analysis Error
                        </h1>

                    </div>

                    <p className="mt-4 text-sm text-red-300">
                        {error}
                    </p>

                    <Link
                        href="/cases"
                        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-black"
                    >
                        <ArrowLeft size={16} />
                        Back to Cases
                    </Link>

                </div>

            </div>
        );
    }


    // ========================================================
    // MAIN
    // ========================================================

    return (
        <div className="min-h-screen bg-[#05070b] p-8 text-white">

            {/* HEADER */}

            <div className="flex items-start justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                        Investigation Intelligence
                    </div>

                    <h1 className="mt-2 text-3xl font-bold">
                        Detailed Case Analysis
                    </h1>

                    <p className="mt-2 text-sm text-white/40">
                        Seven-layer investigation analysis and anomaly intelligence
                    </p>

                </div>


                <Link
                    href="/cases"
                    className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/60 transition hover:bg-white/[0.06] hover:text-white"
                >
                    <ArrowLeft size={16} />
                    Relevant Cases
                </Link>

            </div>


            {/* CASE HEADER */}

            <div className="mt-8 rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.035] p-6">

                <div className="flex items-center justify-between">

                    <div>

                        <div className="text-xs uppercase tracking-wider text-cyan-400">
                            Selected Investigation
                        </div>

                        <div className="mt-2 text-2xl font-bold">
                            {caseData?.fir_number ||
                                caseId.replace("case:", "")}
                        </div>

                        <div className="mt-2 text-xs text-white/30">
                            {caseId}
                        </div>

                    </div>


                    <div className="text-right">

                        <div className="text-xs uppercase tracking-wider text-white/20">
                            Status
                        </div>

                        <div className="mt-2 flex items-center justify-end gap-2">

                            <span className="h-2 w-2 rounded-full bg-emerald-400" />

                            <span className="text-sm font-semibold text-emerald-400">
                                {caseData?.status ||
                                    "ACTIVE"}
                            </span>

                        </div>

                    </div>

                </div>

            </div>


            {/* OVERVIEW */}

            <div className="mt-6 grid grid-cols-4 gap-4">

                <Metric
                    icon={<Users size={18} />}
                    label="Relevant People"
                    value={layer1Stats.people}
                />

                <Metric
                    icon={<Network size={18} />}
                    label="Connections"
                    value={layer1Stats.connections}
                />

                <Metric
                    icon={<GitBranch size={18} />}
                    label="Connected Cases"
                    value={layer1Stats.cases}
                />

                <Metric
                    icon={<FileSearch size={18} />}
                    label="Evidence Signals"
                    value={layer1Stats.evidence}
                />

            </div>


            {/* SEVEN LAYERS */}

            <div className="mt-8">

                <div className="mb-5">

                    <h2 className="text-xl font-semibold">
                        Seven-Layer Analysis Engine
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        Layer 1 is generated from the live investigation graph. Layers 2–7 are currently prototype analysis modules.
                    </p>

                </div>


                <div className="grid grid-cols-2 gap-5">

                    {/* LAYER 1 */}

                    <Layer1
                        analysis={analysis}
                    />


                    {/* LAYER 2 */}

                    <StaticLayer
                        number="02"
                        title="Direct Relationship Analysis"
                        icon={<Network size={20} />}
                        description="Examines direct relationships surrounding the investigation subjects and highlights strong first-degree connections."
                        signals={[
                            "Direct person relationships",
                            "Phone associations",
                            "Vehicle associations",
                            "Account relationships",
                        ]}
                    />


                    {/* LAYER 3 */}

                    <StaticLayer
                        number="03"
                        title="Indirect Network Analysis"
                        icon={<GitBranch size={20} />}
                        description="Examines second-degree and indirect network paths that may connect apparently unrelated entities."
                        signals={[
                            "Indirect paths",
                            "Shared intermediaries",
                            "Multi-hop relationships",
                            "Network bridges",
                        ]}
                    />


                    {/* LAYER 4 */}

                    <StaticLayer
                        number="04"
                        title="Spatial Analysis"
                        icon={<MapPin size={20} />}
                        description="Evaluates geographic relationships between people, locations, vehicles and recorded events."
                        signals={[
                            "Location overlap",
                            "Movement proximity",
                            "Repeated locations",
                            "Spatial associations",
                        ]}
                    />


                    {/* LAYER 5 */}

                    <StaticLayer
                        number="05"
                        title="Temporal / Behavioral Analysis"
                        icon={<Clock3 size={20} />}
                        description="Examines timing patterns, repeated activities and behavioral relationships across the investigation."
                        signals={[
                            "Temporal patterns",
                            "Repeated activity",
                            "Behavioral consistency",
                            "Event sequences",
                        ]}
                    />


                    {/* LAYER 6 */}

                    <StaticLayer
                        number="06"
                        title="Cross-Case / Source Analysis"
                        icon={<FileSearch size={20} />}
                        description="Examines relationships that appear across multiple investigations and evidence sources."
                        signals={[
                            "Cross-case associations",
                            "Multiple evidence sources",
                            "Shared entities",
                            "Source convergence",
                        ]}
                    />


                    {/* LAYER 7 */}

                    <StaticLayer
                        number="07"
                        title="Intelligence Analysis"
                        icon={<BrainCircuit size={20} />}
                        description="Combines investigative signals to prioritize leads for investigator validation."
                        signals={[
                            "Lead prioritization",
                            "Network importance",
                            "Evidence convergence",
                            "Investigation signals",
                        ]}
                    />

                </div>

            </div>


            {/* TOP PEOPLE */}

            <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">

                <div className="flex items-center gap-3">

                    <Users
                        size={20}
                        className="text-cyan-400"
                    />

                    <div>

                        <h2 className="font-semibold">
                            Layer 1 — Top Relevant People
                        </h2>

                        <p className="mt-1 text-xs text-white/30">
                            Real graph-derived investigation relevance
                        </p>

                    </div>

                </div>


                <div className="mt-6 space-y-3">

                    {topPeople.length === 0 ? (

                        <div className="rounded-xl border border-dashed border-white/10 p-8 text-center text-sm text-white/30">
                            No Layer 1 candidates found.
                        </div>

                    ) : (

                        topPeople.map(
                            (person, index) => (

                                <PersonRow
                                    key={
                                        person.person_id ||
                                        person.name ||
                                        index
                                    }
                                    person={person}
                                    rank={index + 1}
                                />

                            )
                        )

                    )}

                </div>

            </div>


            {/* ANOMALY ENGINE */}

            <div className="mt-8">

                <div className="mb-5">

                    <h2 className="text-xl font-semibold">
                        Anomaly Engine
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        Investigative anomalies requiring validation
                    </p>

                </div>


                <div className="grid grid-cols-3 gap-5">

                    <Anomaly
                        icon={<Phone size={19} />}
                        title="Communication Concentration"
                        description="Multiple communication relationships may indicate a highly connected network cluster."
                        level="HIGH"
                    />

                    <Anomaly
                        icon={<Car size={19} />}
                        title="Vehicle Association"
                        description="Repeated vehicle relationships can provide an additional investigative linkage."
                        level="MEDIUM"
                    />

                    <Anomaly
                        icon={<Wallet size={19} />}
                        title="Financial Connectivity"
                        description="Financial relationships connected to investigation entities should be validated against source evidence."
                        level="MEDIUM"
                    />

                </div>

            </div>


            {/* LLM MESSAGE */}

            <div className="mt-8 rounded-2xl border border-purple-500/20 bg-purple-500/[0.035] p-6">

                <div className="flex items-center gap-3">

                    <div className="rounded-xl bg-purple-500/10 p-3">

                        <BrainCircuit
                            size={21}
                            className="text-purple-400"
                        />

                    </div>

                    <div>

                        <h2 className="font-semibold">
                            AI-Assisted Investigation Message
                        </h2>

                        <p className="mt-1 text-xs text-white/30">
                            Investigator-facing lead summary
                        </p>

                    </div>

                </div>


                <p className="mt-5 text-sm leading-7 text-white/55">
                    {generateLLMMessage(
                        caseData,
                        analysis
                    )}
                </p>

            </div>


            {/* DISCLAIMER */}

            <div className="mt-6 rounded-xl border border-amber-500/10 bg-amber-500/[0.025] p-4">

                <div className="flex gap-3">

                    <ShieldAlert
                        size={18}
                        className="mt-0.5 text-amber-400"
                    />

                    <p className="text-xs leading-6 text-white/35">
                        These outputs represent investigative relevance
                        signals generated from available graph relationships
                        and evidence metadata. They are not determinations
                        of guilt and must be validated against the underlying
                        evidence by an authorized investigator.
                    </p>

                </div>

            </div>

        </div>
    );
}


// ============================================================
// REAL LAYER 1
// ============================================================

function Layer1({
    analysis,
}: {
    analysis: InvestigationAnalysis | null;
}) {

    const candidates =
        analysis?.top_relevant_people || [];

    const scores =
        candidates.map(
            (person) =>
                person.relevance_score || 0
        );

    const average =
        scores.length
            ? scores.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) / scores.length
            : 0;


    return (

        <div className="rounded-2xl border border-cyan-500/25 bg-cyan-500/[0.035] p-6">

            <div className="flex items-start justify-between">

                <div className="flex items-center gap-3">

                    <div className="rounded-xl bg-cyan-500/10 p-3">

                        <Users
                            size={20}
                            className="text-cyan-400"
                        />

                    </div>

                    <div>

                        <div className="text-xs font-bold tracking-wider text-cyan-400">
                            LAYER 01
                        </div>

                        <h3 className="mt-1 font-semibold">
                            Target / Profile Analysis
                        </h3>

                    </div>

                </div>


                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
                    LIVE
                </span>

            </div>


            <p className="mt-5 text-sm leading-6 text-white/45">
                Real Layer 1 analysis generated from the selected
                investigation and its connected entities in Neo4j.
            </p>


            <div className="mt-5 grid grid-cols-3 gap-3">

                <SmallMetric
                    label="Candidates"
                    value={
                        analysis?.candidate_count ||
                        0
                    }
                />

                <SmallMetric
                    label="Top People"
                    value={
                        candidates.length
                    }
                />

                <SmallMetric
                    label="Avg Relevance"
                    value={`${average.toFixed(1)}%`}
                />

            </div>


            <div className="mt-5 space-y-2">

                {candidates
                    .slice(0, 3)
                    .map(
                        (person, index) => (

                            <div
                                key={
                                    person.person_id ||
                                    index
                                }
                                className="flex items-center justify-between rounded-lg border border-white/10 bg-black/10 px-3 py-2"
                            >

                                <span className="text-sm text-white/70">
                                    {person.name ||
                                        "Unknown"}
                                </span>

                                <span className="text-sm font-semibold text-cyan-400">
                                    {(
                                        person.relevance_score ||
                                        0
                                    ).toFixed(1)}
                                    %
                                </span>

                            </div>

                        )
                    )}

            </div>

        </div>
    );
}


// ============================================================
// STATIC LAYERS 2–7
// ============================================================

function StaticLayer({
    number,
    title,
    icon,
    description,
    signals,
}: {
    number: string;
    title: string;
    icon: React.ReactNode;
    description: string;
    signals: string[];
}) {

    return (

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">

            <div className="flex items-start gap-3">

                <div className="rounded-xl bg-white/[0.05] p-3 text-white/60">
                    {icon}
                </div>

                <div>

                    <div className="text-xs font-bold tracking-wider text-white/30">
                        LAYER {number}
                    </div>

                    <h3 className="mt-1 font-semibold">
                        {title}
                    </h3>

                </div>

            </div>


            <p className="mt-5 text-sm leading-6 text-white/40">
                {description}
            </p>


            <div className="mt-5 grid grid-cols-2 gap-2">

                {signals.map(
                    (signal) => (

                        <div
                            key={signal}
                            className="flex items-center gap-2 rounded-lg bg-white/[0.025] px-3 py-2 text-xs text-white/35"
                        >

                            <CheckCircle2
                                size={13}
                                className="text-white/20"
                            />

                            {signal}

                        </div>

                    )
                )}

            </div>


            <div className="mt-5 flex items-center gap-2 text-[10px] uppercase tracking-wider text-amber-400/60">

                <Clock3 size={12} />

                Prototype module

            </div>

        </div>
    );
}


// ============================================================
// PERSON
// ============================================================

function PersonRow({
    person,
    rank,
}: {
    person: Candidate;
    rank: number;
}) {

    const features =
        person.features || {};

    return (

        <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4">

            <div className="flex items-center justify-between">

                <div className="flex items-center gap-4">

                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/10 text-sm font-bold text-cyan-400">
                        {rank}
                    </div>

                    <div>

                        <div className="font-semibold">
                            {person.name ||
                                "Unknown Person"}
                        </div>

                        <div className="mt-1 text-xs text-white/25">
                            {person.person_id}
                        </div>

                    </div>

                </div>


                <div className="text-right">

                    <div className="text-lg font-bold text-cyan-400">
                        {(
                            person.relevance_score ||
                            0
                        ).toFixed(1)}
                        %
                    </div>

                    <div className="text-[9px] uppercase tracking-wider text-white/20">
                        relevance
                    </div>

                </div>

            </div>


            <div className="mt-4 grid grid-cols-6 gap-2">

                <Feature
                    label="Connections"
                    value={
                        features.unique_connections ||
                        0
                    }
                />

                <Feature
                    label="People"
                    value={
                        features.connected_people ||
                        0
                    }
                />

                <Feature
                    label="Phones"
                    value={
                        features.connected_phones ||
                        0
                    }
                />

                <Feature
                    label="Vehicles"
                    value={
                        features.connected_vehicles ||
                        0
                    }
                />

                <Feature
                    label="Locations"
                    value={
                        features.connected_locations ||
                        0
                    }
                />

                <Feature
                    label="Cases"
                    value={
                        features.connected_cases ||
                        0
                    }
                />

            </div>

        </div>
    );
}


// ============================================================
// ANOMALY
// ============================================================

function Anomaly({
    icon,
    title,
    description,
    level,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    level: "HIGH" | "MEDIUM" | "LOW";
}) {

    return (

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">

            <div className="flex items-start justify-between">

                <div className="rounded-xl bg-amber-500/10 p-3 text-amber-400">
                    {icon}
                </div>

                <span className="rounded-full bg-amber-500/10 px-2 py-1 text-[9px] font-semibold text-amber-400">
                    {level}
                </span>

            </div>


            <h3 className="mt-5 font-semibold">
                {title}
            </h3>

            <p className="mt-2 text-xs leading-6 text-white/35">
                {description}
            </p>

        </div>
    );
}


// ============================================================
// METRICS
// ============================================================

function Metric({
    icon,
    label,
    value,
}: {
    icon: React.ReactNode;
    label: string;
    value: number | string;
}) {

    return (

        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">

            <div className="flex items-center gap-2 text-white/30">

                {icon}

                <span className="text-xs uppercase tracking-wider">
                    {label}
                </span>

            </div>

            <div className="mt-3 text-2xl font-bold">
                {value}
            </div>

        </div>
    );
}


function SmallMetric({
    label,
    value,
}: {
    label: string;
    value: number | string;
}) {

    return (

        <div className="rounded-lg bg-black/10 p-3">

            <div className="text-[9px] uppercase tracking-wider text-white/20">
                {label}
            </div>

            <div className="mt-1 text-sm font-semibold text-white/70">
                {value}
            </div>

        </div>
    );
}


function Feature({
    label,
    value,
}: {
    label: string;
    value: number;
}) {

    return (

        <div className="rounded-lg bg-black/10 p-2">

            <div className="truncate text-[8px] uppercase tracking-wider text-white/20">
                {label}
            </div>

            <div className="mt-1 text-xs font-semibold text-white/55">
                {value}
            </div>

        </div>
    );
}


// ============================================================
// LLM SUMMARY
// ============================================================

function generateLLMMessage(
    caseData: CaseData | null,
    analysis: InvestigationAnalysis | null
): string {

    if (!analysis) {

        return "No investigation analysis is currently available.";
    }

    const people =
        analysis.top_relevant_people || [];

    if (!people.length) {

        return `The analysis of ${caseData?.fir_number ||
            analysis.case_id
            } did not identify enough connected person entities to generate a meaningful lead summary.`;
    }

    const topPerson =
        people[0];

    const secondPerson =
        people[1];

    const topName =
        topPerson?.name ||
        "the highest-ranked person";

    const secondName =
        secondPerson?.name ||
        "another connected person";

    const topScore =
        topPerson?.relevance_score || 0;

    return `For ${caseData?.fir_number ||
        analysis.case_id
        }, Layer 1 identifies ${topName} as the highest-ranked investigative lead with a relevance score of ${topScore.toFixed(
            1
        )}%. ${secondName} is also strongly connected within the available graph. The ranking is based on observable graph relationships and supporting evidence metadata, including cross-case connectivity and entity relationships. Investigators should review the underlying evidence, timelines and source records before drawing conclusions.`;
}