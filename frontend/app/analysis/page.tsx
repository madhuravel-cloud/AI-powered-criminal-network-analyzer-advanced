"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import {
    ArrowLeft,
    Brain,
    AlertCircle,
    Users,
    Database,
    FileText,
} from "lucide-react";

import {
    analyzeInvestigation,
    type Candidate,
    type InvestigationAnalysis,
} from "@/lib/api";

export default function AnalysisPage() {
    const searchParams = useSearchParams();

    const caseId = searchParams.get("case");

    const [analysis, setAnalysis] =
        useState<InvestigationAnalysis | null>(null);

    const [selected, setSelected] =
        useState<Candidate | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    // =====================================================
    // LOAD ANALYSIS FOR SELECTED CASE
    // =====================================================

    async function loadAnalysis() {
        try {
            setLoading(true);
            setError(null);

            if (!caseId) {
                throw new Error(
                    "No case was selected. Please open Analysis from a case."
                );
            }

            const response =
                await analyzeInvestigation(caseId);

            setAnalysis(response.analysis);

            if (
                response.analysis.top_relevant_people.length > 0
            ) {
                setSelected(
                    response.analysis.top_relevant_people[0]
                );
            } else {
                setSelected(null);
            }
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to run investigation analysis."
            );
        } finally {
            setLoading(false);
        }
    }

    // =====================================================
    // RUN WHEN CASE CHANGES
    // =====================================================

    useEffect(() => {
        loadAnalysis();
    }, [caseId]);

    return (
        <section className="min-h-screen bg-[#070b12] p-8 text-white">
            <div className="mx-auto max-w-7xl">

                {/* BACK */}
                <Link
                    href="/cases"
                    className="mb-4 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
                >
                    <ArrowLeft size={16} />
                    Back to Cases
                </Link>

                {/* HEADER */}
                <div className="mb-8 flex items-end justify-between">
                    <div>

                        <div className="mb-2 flex items-center gap-2 text-xs text-emerald-400">
                            <span className="h-2 w-2 rounded-full bg-emerald-400" />
                            ANALYSIS ENGINE ONLINE
                        </div>

                        <h1 className="text-3xl font-semibold">
                            Investigation Analysis
                        </h1>

                        <p className="mt-1 text-slate-400">
                            Direct predictive analysis from the Master Graph.
                        </p>

                        {/* SELECTED CASE */}
                        {caseId && (
                            <div className="mt-3 text-xs text-cyan-400">
                                CASE: {caseId.replace("case:", "")}
                            </div>
                        )}

                    </div>

                    <button
                        onClick={loadAnalysis}
                        disabled={loading}
                        className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {loading
                            ? "Running..."
                            : "Run Analysis"}
                    </button>
                </div>

                {/* LOADING */}
                {loading && (
                    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-12 text-center">

                        <Brain className="mx-auto mb-4 animate-pulse text-slate-500" />

                        <div className="text-slate-300">
                            Analyzing investigation graph...
                        </div>

                        <div className="mt-2 text-sm text-slate-600">
                            Querying Neo4j and calculating candidate relevance.
                        </div>

                    </div>
                )}

                {/* ERROR */}
                {error && (
                    <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6">

                        <div className="flex items-center gap-3 text-red-400">

                            <AlertCircle size={20} />

                            <span className="font-medium">
                                Analysis failed
                            </span>

                        </div>

                        <p className="mt-3 text-sm text-slate-400">
                            {error}
                        </p>

                        <button
                            onClick={loadAnalysis}
                            className="mt-5 rounded-lg border border-red-500/20 px-4 py-2 text-sm text-red-300 transition hover:bg-red-500/10"
                        >
                            Retry
                        </button>

                    </div>
                )}

                {/* ANALYSIS */}
                {!loading && !error && analysis && (
                    <>
                        {/* STATS */}
                        <div className="mb-6 grid gap-4 sm:grid-cols-3">

                            <Stat
                                label="INVESTIGATION"
                                value={analysis.case_id}
                            />

                            <Stat
                                label="SEED PEOPLE"
                                value={String(
                                    analysis.seed_people.length
                                )}
                            />

                            <Stat
                                label="CANDIDATES"
                                value={String(
                                    analysis.candidate_count
                                )}
                            />

                        </div>

                        {/* MAIN GRID */}
                        <div className="grid gap-6 xl:grid-cols-[1fr_380px]">

                            {/* TOP PEOPLE */}
                            <div className="rounded-2xl border border-white/10 bg-white/[0.025]">

                                <div className="border-b border-white/10 p-6">

                                    <div className="flex items-center gap-2">

                                        <Users size={18} />

                                        <h2 className="font-medium">
                                            Top Relevant People
                                        </h2>

                                    </div>

                                    <p className="mt-1 text-sm text-slate-500">
                                        Ranked by investigation-specific relevance.
                                    </p>

                                </div>

                                <div>

                                    {analysis.top_relevant_people.map(
                                        (person, index) => (

                                            <button
                                                key={person.person_id}
                                                onClick={() =>
                                                    setSelected(person)
                                                }
                                                className={`flex w-full items-center gap-4 border-b border-white/5 p-5 text-left transition last:border-0 ${selected?.person_id ===
                                                    person.person_id
                                                    ? "bg-white/[0.06]"
                                                    : "hover:bg-white/[0.03]"
                                                    }`}
                                            >

                                                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/10 text-sm">
                                                    {index + 1}
                                                </div>

                                                <div className="min-w-0 flex-1">

                                                    <div className="font-medium">
                                                        {person.name}
                                                    </div>

                                                    <div className="mt-1 text-xs text-slate-500">

                                                        {
                                                            person
                                                                .features
                                                                .unique_connections
                                                        }{" "}
                                                        connections •{" "}
                                                        {
                                                            person
                                                                .source_layers
                                                                .length
                                                        }{" "}
                                                        source layers

                                                    </div>

                                                </div>

                                                <div className="w-24">

                                                    <div className="text-right text-sm font-medium">

                                                        {person.relevance_score.toFixed(
                                                            2
                                                        )}

                                                    </div>

                                                    <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">

                                                        <div
                                                            className="h-full rounded-full bg-white"
                                                            style={{
                                                                width: `${Math.min(
                                                                    person.relevance_score,
                                                                    100
                                                                )}%`,
                                                            }}
                                                        />

                                                    </div>

                                                </div>

                                            </button>

                                        )
                                    )}

                                </div>

                            </div>

                            {/* SELECTED PERSON */}
                            {selected && (

                                <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-6">

                                    <div className="mb-6">

                                        <div className="text-xs tracking-widest text-slate-600">
                                            SELECTED CANDIDATE
                                        </div>

                                        <h2 className="mt-2 text-2xl font-semibold">
                                            {selected.name}
                                        </h2>

                                        <div className="mt-2 text-sm text-slate-500">
                                            {selected.person_id}
                                        </div>

                                    </div>

                                    {/* RELEVANCE */}
                                    <div className="mb-6 rounded-xl border border-white/10 bg-white/[0.03] p-4">

                                        <div className="text-xs text-slate-500">
                                            INVESTIGATION RELEVANCE
                                        </div>

                                        <div className="mt-2 text-3xl font-semibold">
                                            {selected.relevance_score.toFixed(
                                                2
                                            )}
                                        </div>

                                        <div className="mt-1 text-xs text-slate-600">
                                            This is an investigative ranking signal,
                                            not a probability of guilt.
                                        </div>

                                    </div>

                                    {/* METRICS */}
                                    <div className="grid grid-cols-2 gap-3">

                                        <Metric
                                            icon={
                                                <Users size={15} />
                                            }
                                            label="Connections"
                                            value={
                                                selected.features
                                                    .unique_connections
                                            }
                                        />

                                        <Metric
                                            icon={
                                                <Database size={15} />
                                            }
                                            label="Cases"
                                            value={
                                                selected.features
                                                    .connected_cases
                                            }
                                        />

                                        <Metric
                                            icon={
                                                <FileText size={15} />
                                            }
                                            label="Evidence"
                                            value={
                                                selected.evidence_ids
                                                    .length
                                            }
                                        />

                                        <Metric
                                            icon={
                                                <Brain size={15} />
                                            }
                                            label="Sources"
                                            value={
                                                selected.source_layers
                                                    .length
                                            }
                                        />

                                    </div>

                                    {/* SIGNALS */}
                                    <div className="mt-6 border-t border-white/10 pt-5">

                                        <div className="text-xs tracking-widest text-slate-600">
                                            INVESTIGATION SIGNALS
                                        </div>

                                        <div className="mt-3 space-y-2">

                                            {selected.signals.map(
                                                (signal) => (

                                                    <div
                                                        key={signal}
                                                        className="rounded-lg bg-white/[0.03] px-3 py-2 text-xs leading-5 text-slate-400"
                                                    >
                                                        {signal}
                                                    </div>

                                                )
                                            )}

                                        </div>

                                    </div>

                                    {/* EVIDENCE */}
                                    <div className="mt-6 border-t border-white/10 pt-5">

                                        <div className="text-xs tracking-widest text-slate-600">
                                            EVIDENCE REFERENCES
                                        </div>

                                        <div className="mt-3 space-y-2">

                                            {selected.evidence_ids.map(
                                                (id) => (

                                                    <div
                                                        key={id}
                                                        className="rounded-lg border border-white/5 px-3 py-2 font-mono text-[11px] text-slate-500"
                                                    >
                                                        {id}
                                                    </div>

                                                )
                                            )}

                                        </div>

                                    </div>

                                </div>

                            )}

                        </div>
                    </>
                )}

            </div>
        </section>
    );
}


// =========================================================
// STAT
// =========================================================

function Stat({
    label,
    value,
}: {
    label: string;
    value: string;
}) {
    return (
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">

            <div className="text-[10px] tracking-widest text-slate-600">
                {label}
            </div>

            <div className="mt-2 text-2xl font-semibold">
                {value}
            </div>

        </div>
    );
}


// =========================================================
// METRIC
// =========================================================

function Metric({
    icon,
    label,
    value,
}: {
    icon: React.ReactNode;
    label: string;
    value: number;
}) {
    return (
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">

            <div className="flex items-center gap-2 text-slate-500">

                {icon}

                <span className="text-xs">
                    {label}
                </span>

            </div>

            <div className="mt-2 text-lg font-medium">
                {value}
            </div>

        </div>
    );
}