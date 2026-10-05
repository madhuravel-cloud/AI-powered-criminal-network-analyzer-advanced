"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
    Activity,
    AlertTriangle,
    ArrowLeft,
    BrainCircuit,
    Car,
    CheckCircle2,
    Clock3,
    FileSearch,
    GitBranch,
    MapPin,
    Network,
    Phone,
    ShieldAlert,
    Users,
    Wallet,
} from "lucide-react";

import {
    analyzeInvestigation,
    getCase,
    type CaseData,
    type Candidate,
    type InvestigationAnalysis,
} from "@/lib/api";

const SELECTED_FIR_KEY =
    "criminal-network-selected-fir";

export default function AnalysisPage() {
    const [selectedFir, setSelectedFir] =
        useState<string>("");

    const [caseData, setCaseData] =
        useState<CaseData | null>(null);

    const [analysis, setAnalysis] =
        useState<InvestigationAnalysis | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [debugResponse, setDebugResponse] =
        useState<string>("");

    // ============================================================
    // INITIAL LOAD
    // ============================================================

    useEffect(() => {
        const loadSelectedFir = async () => {
            try {
                setLoading(true);
                setError("");

                const params =
                    new URLSearchParams(
                        window.location.search
                    );

                /*
                 * Priority:
                 *
                 * 1. ?case=
                 * 2. Dashboard localStorage
                 */

                const urlCase =
                    params.get("case");

                const storedFir =
                    window.localStorage.getItem(
                        SELECTED_FIR_KEY
                    );

                const fir =
                    urlCase ||
                    storedFir ||
                    "";

                console.log(
                    "ANALYSIS - URL CASE:",
                    urlCase
                );

                console.log(
                    "ANALYSIS - STORED FIR:",
                    storedFir
                );

                console.log(
                    "ANALYSIS - FINAL FIR:",
                    fir
                );

                if (!fir) {
                    setError(
                        "No FIR is selected. Please select an FIR from the Dashboard."
                    );

                    setLoading(false);

                    return;
                }

                setSelectedFir(fir);

                /*
                 * Keep the same FIR for all pages.
                 */

                window.localStorage.setItem(
                    SELECTED_FIR_KEY,
                    fir
                );

                // ====================================================
                // LOAD CASE + ANALYSIS
                // ====================================================

                console.log(
                    "ANALYSIS - Loading case:",
                    fir
                );

                const caseResult =
                    await getCase(fir);

                console.log(
                    "ANALYSIS - CASE RESULT:",
                    caseResult
                );

                setCaseData(caseResult);

                console.log(
                    "ANALYSIS - Calling backend analysis..."
                );

                const analysisResult =
                    await analyzeInvestigation(
                        fir
                    );

                console.log(
                    "ANALYSIS - ANALYSIS RESULT:",
                    analysisResult
                );

                /*
                 * Keep a visible debug representation.
                 * This also helps if backend fields are absent.
                 */

                setDebugResponse(
                    JSON.stringify(
                        analysisResult,
                        null,
                        2
                    )
                );

                setAnalysis(
                    analysisResult
                );
            } catch (err) {
                console.error(
                    "ANALYSIS PAGE ERROR:",
                    err
                );

                setError(
                    err instanceof Error
                        ? err.message
                        : "Failed to load investigation analysis."
                );
            } finally {
                setLoading(false);
            }
        };

        loadSelectedFir();
    }, []);

    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <div className="min-h-screen bg-[#05070b] p-8 text-white">

                <div className="flex min-h-[70vh] items-center justify-center">

                    <div className="text-center">

                        <Activity
                            size={32}
                            className="mx-auto animate-spin text-cyan-400"
                        />

                        <h2 className="mt-5 text-lg font-semibold">
                            Running Investigation Analysis
                        </h2>

                        <p className="mt-2 text-sm text-white/40">
                            Loading the FIR selected in Dashboard...
                        </p>

                    </div>

                </div>

            </div>
        );
    }

    // ============================================================
    // ERROR
    // ============================================================

    if (error) {
        return (
            <div className="min-h-screen bg-[#05070b] p-8 text-white">

                <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-8">

                    <div className="flex items-center gap-3">

                        <AlertTriangle
                            size={24}
                            className="text-red-400"
                        />

                        <h1 className="text-xl font-semibold">
                            Analysis Failed
                        </h1>

                    </div>

                    <p className="mt-4 text-sm text-red-300">
                        {error}
                    </p>

                    <div className="mt-4 rounded-xl bg-black/30 p-4 text-xs text-white/40">
                        Selected FIR:{" "}
                        {selectedFir || "None"}
                    </div>

                    <div className="mt-6 flex gap-3">

                        <Link
                            href="/"
                            className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-black"
                        >
                            <ArrowLeft size={16} />
                            Dashboard
                        </Link>

                        <button
                            onClick={() =>
                                window.location.reload()
                            }
                            className="rounded-xl border border-white/10 px-5 py-3 text-sm text-white/60"
                        >
                            Retry
                        </button>

                    </div>

                </div>

            </div>
        );
    }

    // ============================================================
    // MAIN DATA
    // ============================================================

    const people =
        analysis?.top_relevant_people || [];

    const candidateCount =
        Number(
            analysis?.candidate_count || 0
        );

    const relevance =
        Number(
            analysis?.overall_relevance_score || 0
        );

    const anomaly =
        analysis?.anomaly;

    // ============================================================
    // MAIN
    // ============================================================

    return (
        <div className="min-h-screen bg-[#05070b] p-8 text-white">

            {/* ====================================================
                HEADER
            ==================================================== */}

            <div className="flex items-start justify-between">

                <div>

                    <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                        Investigation Intelligence
                    </p>

                    <h1 className="mt-2 text-3xl font-bold">
                        FIR Analysis
                    </h1>

                    <p className="mt-2 text-sm text-white/40">
                        Live analysis generated from the selected FIR
                    </p>

                </div>

                <Link
                    href="/"
                    className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/60 hover:bg-white/[0.06] hover:text-white"
                >
                    <ArrowLeft size={16} />
                    Dashboard
                </Link>

            </div>

            {/* ====================================================
                SELECTED FIR
            ==================================================== */}

            <div className="mt-8 rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.035] p-6">

                <div className="flex items-center justify-between">

                    <div>

                        <p className="text-xs uppercase tracking-wider text-cyan-400">
                            Selected FIR
                        </p>

                        <h2 className="mt-2 text-2xl font-bold">
                            {caseData?.fir_number ||
                                selectedFir}
                        </h2>

                        <p className="mt-2 text-xs text-white/30">
                            Case ID:{" "}
                            {caseData?.id ||
                                selectedFir}
                        </p>

                    </div>

                    <div className="text-right">

                        <p className="text-xs uppercase tracking-wider text-white/25">
                            Police Station
                        </p>

                        <p className="mt-2 text-sm font-semibold text-white/70">
                            {caseData?.police_station ||
                                "Not available"}
                        </p>

                    </div>

                </div>

            </div>

            {/* ====================================================
                SUMMARY CARDS
            ==================================================== */}

            <div className="mt-6 grid grid-cols-4 gap-4">

                <Metric
                    icon={
                        <BrainCircuit size={19} />
                    }
                    label="Relevance"
                    value={`${relevance.toFixed(
                        1
                    )}%`}
                />

                <Metric
                    icon={
                        <Users size={19} />
                    }
                    label="Candidates"
                    value={candidateCount}
                />

                <Metric
                    icon={
                        <Network size={19} />
                    }
                    label="Top Leads"
                    value={people.length}
                />

                <Metric
                    icon={
                        <FileSearch size={19} />
                    }
                    label="Evidence"
                    value={
                        caseData?.evidence_count ||
                        0
                    }
                />

            </div>

            {/* ====================================================
                AI SUMMARY
            ==================================================== */}

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
                            AI-Assisted Investigation Summary
                        </h2>

                        <p className="mt-1 text-xs text-white/30">
                            Generated from the current investigation analysis
                        </p>

                    </div>

                </div>

                <p className="mt-5 text-sm leading-7 text-white/60">

                    {typeof analysis?.llm_message ===
                        "string" &&
                        analysis.llm_message.trim()
                        ? analysis.llm_message
                        : generateSummary(
                            caseData,
                            analysis
                        )}

                </p>

            </div>

            {/* ====================================================
                TOP RELEVANT PEOPLE
            ==================================================== */}

            <div className="mt-8">

                <div className="mb-5">

                    <h2 className="text-xl font-semibold">
                        Top Relevant People
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        People ranked using graph-derived investigation signals
                    </p>

                </div>

                {people.length === 0 ? (

                    <div className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.035] p-8">

                        <div className="flex items-center gap-3">

                            <AlertTriangle
                                size={20}
                                className="text-amber-400"
                            />

                            <div>

                                <h3 className="font-semibold">
                                    No ranked people returned
                                </h3>

                                <p className="mt-1 text-sm text-white/40">
                                    The backend returned an analysis response, but no
                                    `top_relevant_people` were returned for this FIR.
                                </p>

                            </div>

                        </div>

                    </div>

                ) : (

                    <div className="space-y-3">

                        {people
                            .slice(0, 5)
                            .map(
                                (
                                    person,
                                    index
                                ) => (
                                    <PersonCard
                                        key={
                                            person.person_id ||
                                            person.name ||
                                            index
                                        }
                                        person={person}
                                        rank={
                                            index + 1
                                        }
                                    />
                                )
                            )}

                    </div>

                )}

            </div>

            {/* ====================================================
                ANOMALY ENGINE
            ==================================================== */}

            <div className="mt-8">

                <div className="mb-5">

                    <h2 className="text-xl font-semibold">
                        Anomaly Engine
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        Graph-derived anomaly signals
                    </p>

                </div>

                <div className="grid grid-cols-3 gap-5">

                    <AnomalyCard
                        icon={
                            <Phone size={19} />
                        }
                        title="Communication"
                        description="Communication relationships connected to entities in the selected FIR."
                        level={
                            anomaly?.level ||
                            "MEDIUM"
                        }
                    />

                    <AnomalyCard
                        icon={
                            <Car size={19} />
                        }
                        title="Vehicle Association"
                        description="Vehicle relationships connected to the investigation network."
                        level="MEDIUM"
                    />

                    <AnomalyCard
                        icon={
                            <Wallet size={19} />
                        }
                        title="Financial Connectivity"
                        description="Financial relationships should be validated against source evidence."
                        level="MEDIUM"
                    />

                </div>

            </div>

            {/* ====================================================
                SEVEN LAYERS
            ==================================================== */}

            <div className="mt-8">

                <div className="mb-5">

                    <h2 className="text-xl font-semibold">
                        Seven-Layer Analysis Engine
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        Layer 1 currently uses the live investigation graph.
                        Remaining layers are prototype modules.
                    </p>

                </div>

                <div className="grid grid-cols-2 gap-5">

                    <LayerCard
                        number="01"
                        title="Target / Profile"
                        icon={
                            <Users size={20} />
                        }
                        live
                        description={`Live profile analysis returned ${candidateCount} candidate entities for this FIR.`}
                    />

                    <LayerCard
                        number="02"
                        title="Direct Relationship"
                        icon={
                            <Network size={20} />
                        }
                        description="Analyses direct relationships surrounding investigation subjects."
                    />

                    <LayerCard
                        number="03"
                        title="Indirect Network"
                        icon={
                            <GitBranch size={20} />
                        }
                        description="Analyses multi-hop relationships and indirect network paths."
                    />

                    <LayerCard
                        number="04"
                        title="Spatial"
                        icon={
                            <MapPin size={20} />
                        }
                        description="Analyses geographic relationships between connected entities."
                    />

                    <LayerCard
                        number="05"
                        title="Temporal / Behavioral"
                        icon={
                            <Clock3 size={20} />
                        }
                        description="Analyses temporal patterns and repeated behavioral activity."
                    />

                    <LayerCard
                        number="06"
                        title="Cross-Case / Source"
                        icon={
                            <FileSearch size={20} />
                        }
                        description="Analyses relationships across cases and evidence sources."
                    />

                    <LayerCard
                        number="07"
                        title="Intelligence"
                        icon={
                            <BrainCircuit size={20} />
                        }
                        description="Combines investigative signals for lead prioritization."
                    />

                </div>

            </div>

            {/* ====================================================
                RAW BACKEND RESPONSE
                ==================================================== */}

            <details className="mt-8 rounded-2xl border border-white/10 bg-black/20">

                <summary className="cursor-pointer px-5 py-4 text-xs font-semibold uppercase tracking-wider text-white/30">
                    Analysis Backend Response
                </summary>

                <pre className="max-h-[500px] overflow-auto border-t border-white/10 p-5 text-xs leading-6 text-cyan-300/60">
                    {debugResponse ||
                        "No response received"}
                </pre>

            </details>

            {/* ====================================================
                DISCLAIMER
            ==================================================== */}

            <div className="mt-6 rounded-xl border border-amber-500/10 bg-amber-500/[0.025] p-4">

                <div className="flex gap-3">

                    <ShieldAlert
                        size={18}
                        className="mt-0.5 text-amber-400"
                    />

                    <p className="text-xs leading-6 text-white/35">
                        Investigation relevance scores and anomaly signals
                        are investigative aids. They do not determine guilt
                        and must be validated against underlying evidence.
                    </p>

                </div>

            </div>

        </div>
    );
}


// ============================================================
// METRIC
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


// ============================================================
// PERSON CARD
// ============================================================

function PersonCard({
    person,
    rank,
}: {
    person: Candidate;
    rank: number;
}) {
    const features =
        person.features || {};

    const score =
        Number(
            person.relevance_score || 0
        );

    return (
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">

            <div className="flex items-center justify-between">

                <div className="flex items-center gap-4">

                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 font-bold text-cyan-400">
                        {rank}
                    </div>

                    <div>

                        <h3 className="font-semibold">
                            {person.name ||
                                "Unknown Person"}
                        </h3>

                        <p className="mt-1 text-xs text-white/25">
                            {person.person_id ||
                                "No person ID"}
                        </p>

                    </div>

                </div>

                <div className="text-right">

                    <p className="text-2xl font-bold text-cyan-400">
                        {score.toFixed(1)}%
                    </p>

                    <p className="text-[9px] uppercase tracking-wider text-white/20">
                        relevance
                    </p>

                </div>

            </div>

            <div className="mt-5 grid grid-cols-6 gap-2">

                <MiniStat
                    label="Connections"
                    value={
                        features.unique_connections ||
                        0
                    }
                />

                <MiniStat
                    label="People"
                    value={
                        features.connected_people ||
                        0
                    }
                />

                <MiniStat
                    label="Phones"
                    value={
                        features.connected_phones ||
                        0
                    }
                />

                <MiniStat
                    label="Vehicles"
                    value={
                        features.connected_vehicles ||
                        0
                    }
                />

                <MiniStat
                    label="Locations"
                    value={
                        features.connected_locations ||
                        0
                    }
                />

                <MiniStat
                    label="Cases"
                    value={
                        features.connected_cases ||
                        0
                    }
                />

            </div>

            {person.signals &&
                person.signals.length > 0 && (

                    <div className="mt-4 flex flex-wrap gap-2">

                        {person.signals
                            .slice(0, 6)
                            .map(
                                (
                                    signal,
                                    index
                                ) => (
                                    <span
                                        key={`${signal}-${index}`}
                                        className="rounded-full bg-cyan-500/10 px-3 py-1 text-[10px] text-cyan-300/70"
                                    >
                                        {signal}
                                    </span>
                                )
                            )}

                    </div>
                )}

        </div>
    );
}


// ============================================================
// MINI STAT
// ============================================================

function MiniStat({
    label,
    value,
}: {
    label: string;
    value: number;
}) {
    return (
        <div className="rounded-lg bg-black/20 p-3">

            <p className="text-[8px] uppercase tracking-wider text-white/20">
                {label}
            </p>

            <p className="mt-1 text-sm font-semibold text-white/60">
                {value}
            </p>

        </div>
    );
}


// ============================================================
// ANOMALY CARD
// ============================================================

function AnomalyCard({
    icon,
    title,
    description,
    level,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    level: string;
}) {
    return (
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">

            <div className="flex items-start justify-between">

                <div className="rounded-xl bg-amber-500/10 p-3 text-amber-400">
                    {icon}
                </div>

                <span className="rounded-full bg-amber-500/10 px-3 py-1 text-[9px] font-semibold text-amber-400">
                    {String(level).toUpperCase()}
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
// LAYER CARD
// ============================================================

function LayerCard({
    number,
    title,
    icon,
    description,
    live = false,
}: {
    number: string;
    title: string;
    icon: React.ReactNode;
    description: string;
    live?: boolean;
}) {
    return (
        <div
            className={
                live
                    ? "rounded-2xl border border-cyan-500/25 bg-cyan-500/[0.035] p-6"
                    : "rounded-2xl border border-white/10 bg-white/[0.03] p-6"
            }
        >

            <div className="flex items-start justify-between">

                <div className="flex items-center gap-3">

                    <div className="rounded-xl bg-white/[0.05] p-3 text-white/60">
                        {icon}
                    </div>

                    <div>

                        <p className="text-[10px] font-bold tracking-wider text-white/30">
                            LAYER {number}
                        </p>

                        <h3 className="mt-1 font-semibold">
                            {title}
                        </h3>

                    </div>

                </div>

                {live ? (
                    <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-[9px] font-semibold text-emerald-400">
                        LIVE
                    </span>
                ) : (
                    <span className="rounded-full bg-amber-500/10 px-3 py-1 text-[9px] font-semibold text-amber-400">
                        PROTOTYPE
                    </span>
                )}

            </div>

            <p className="mt-5 text-sm leading-6 text-white/40">
                {description}
            </p>

            <div className="mt-5 flex items-center gap-2 text-xs text-white/20">

                {live ? (
                    <>
                        <CheckCircle2 size={13} />
                        Connected to investigation analysis
                    </>
                ) : (
                    <>
                        <Clock3 size={13} />
                        Dedicated engine pending
                    </>
                )}

            </div>

        </div>
    );
}


// ============================================================
// FALLBACK SUMMARY
// ============================================================

function generateSummary(
    caseData: CaseData | null,
    analysis: InvestigationAnalysis | null
): string {
    const fir =
        caseData?.fir_number ||
        analysis?.case_id ||
        "the selected FIR";

    if (!analysis) {
        return `No analysis result is available for ${fir}.`;
    }

    const people =
        analysis.top_relevant_people || [];

    if (people.length === 0) {
        return `The investigation analysis for ${fir} completed, but no ranked person candidates were returned. Review the FIR evidence and connected entities in the Network page.`;
    }

    const first =
        people[0];

    const name =
        first.name ||
        "the highest-ranked entity";

    const score =
        Number(
            first.relevance_score || 0
        );

    return `The analysis for ${fir} identified ${analysis.candidate_count} investigation candidate(s). ${name} currently has the highest investigation relevance score at ${score.toFixed(
        1
    )}%. These results are graph-derived investigative leads and should be validated against the underlying evidence.`;
}