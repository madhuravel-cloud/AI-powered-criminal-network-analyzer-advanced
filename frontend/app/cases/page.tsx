"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
    ArrowLeft,
    ArrowRight,
    FileText,
    Network,
    RefreshCw,
    Search,
    Shield,
} from "lucide-react";

import {
    getCase,
    getRelevantCases,
    type CaseData,
} from "@/lib/api";


const SELECTED_FIR_KEY =
    "criminal-network-selected-fir";


export default function CasesPage() {

    const [selectedFir, setSelectedFir] =
        useState("");

    const [selectedCase, setSelectedCase] =
        useState<CaseData | null>(null);

    const [cases, setCases] =
        useState<CaseData[]>([]);

    const [search, setSearch] =
        useState("");

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    // --------------------------------------------------------
    // LOAD SELECTED FIR
    // --------------------------------------------------------

    useEffect(() => {

        const params =
            new URLSearchParams(
                window.location.search
            );

        const queryFir =
            params.get("fir");

        const savedFir =
            window.localStorage.getItem(
                SELECTED_FIR_KEY
            );

        const fir =
            queryFir ||
            savedFir ||
            "";

        if (!fir) {

            setLoading(false);

            setError(
                "No FIR selected. Please select an FIR from the dashboard."
            );

            return;
        }

        setSelectedFir(fir);

        window.localStorage.setItem(
            SELECTED_FIR_KEY,
            fir
        );

        loadRelevantCases(fir);

    }, []);


    // --------------------------------------------------------
    // LOAD RELEVANT CASES
    // --------------------------------------------------------

    async function loadRelevantCases(
        fir: string
    ) {

        try {

            setLoading(true);
            setError("");

            const [
                seedCase,
                relevantCases,
            ] = await Promise.all([
                getCase(fir),
                getRelevantCases(fir),
            ]);

            setSelectedCase(
                seedCase
            );

            setCases(
                relevantCases
            );

        } catch (err) {

            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load relevant cases."
            );

        } finally {

            setLoading(false);
        }
    }


    // --------------------------------------------------------
    // FILTER
    // --------------------------------------------------------

    const filteredCases =
        cases.filter((item) => {

            const value =
                search
                    .toLowerCase()
                    .trim();

            if (!value) {
                return true;
            }

            return (
                item.id
                    ?.toLowerCase()
                    .includes(value) ||

                item.fir_number
                    ?.toLowerCase()
                    .includes(value) ||

                item.case_type
                    ?.toLowerCase()
                    .includes(value) ||

                item.police_station
                    ?.toLowerCase()
                    .includes(value) ||

                item.status
                    ?.toLowerCase()
                    .includes(value)
            );

        });


    // --------------------------------------------------------
    // UI
    // --------------------------------------------------------

    return (

        <div className="min-h-screen bg-[#05070b] p-8 text-white">

            {/* HEADER */}

            <div className="flex items-start justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                        Connected Investigations
                    </div>

                    <h1 className="mt-2 text-3xl font-bold">
                        Relevant Cases
                    </h1>

                    <p className="mt-2 text-sm text-white/40">
                        Cases connected to the selected FIR through the master investigation graph
                    </p>

                </div>


                <Link
                    href="/"
                    className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/60 transition hover:bg-white/[0.06] hover:text-white"
                >
                    <ArrowLeft size={16} />
                    Dashboard
                </Link>

            </div>


            {/* SELECTED FIR */}

            {selectedCase && (

                <div className="mt-8 rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.04] p-6">

                    <div className="flex items-center justify-between">

                        <div className="flex items-center gap-4">

                            <div className="rounded-xl bg-cyan-500/10 p-3">

                                <Shield
                                    size={22}
                                    className="text-cyan-400"
                                />

                            </div>


                            <div>

                                <div className="text-xs uppercase tracking-wider text-cyan-400">
                                    Investigation Source FIR
                                </div>

                                <div className="mt-1 text-xl font-bold">
                                    {selectedCase.fir_number ||
                                        selectedCase.id}
                                </div>

                            </div>

                        </div>


                        <div className="text-right">

                            <div className="text-2xl font-bold text-cyan-400">
                                {cases.length}
                            </div>

                            <div className="text-xs text-white/30">
                                relevant cases
                            </div>

                        </div>

                    </div>

                </div>

            )}


            {/* ERROR */}

            {error && (

                <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
                    {error}
                </div>

            )}


            {/* SEARCH */}

            <div className="mt-8 flex items-center justify-between">

                <div>

                    <h2 className="text-lg font-semibold">
                        Connected Cases
                    </h2>

                    <p className="mt-1 text-xs text-white/30">
                        Derived from relationships in Neo4j
                    </p>

                </div>


                <div className="flex items-center gap-3">

                    <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4">

                        <Search
                            size={16}
                            className="text-white/30"
                        />

                        <input
                            value={search}
                            onChange={(event) =>
                                setSearch(
                                    event.target.value
                                )
                            }
                            placeholder="Search cases..."
                            className="w-64 bg-transparent py-3 text-sm text-white outline-none placeholder:text-white/20"
                        />

                    </div>


                    <button
                        onClick={() =>
                            selectedFir &&
                            loadRelevantCases(
                                selectedFir
                            )
                        }
                        className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-white/40 transition hover:bg-white/[0.06] hover:text-white"
                    >

                        <RefreshCw
                            size={16}
                        />

                    </button>

                </div>

            </div>


            {/* CONTENT */}

            <div className="mt-5">

                {loading ? (

                    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-16 text-center">

                        <RefreshCw
                            size={22}
                            className="mx-auto animate-spin text-cyan-400"
                        />

                        <p className="mt-4 text-sm text-white/30">
                            Finding relevant cases from the master graph...
                        </p>

                    </div>

                ) : filteredCases.length === 0 ? (

                    <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-16 text-center">

                        <Network
                            size={36}
                            className="mx-auto text-white/20"
                        />

                        <h3 className="mt-4 font-semibold">
                            No relevant cases found
                        </h3>

                        <p className="mt-2 text-sm text-white/30">
                            No other case is currently connected to the selected FIR through shared investigative entities.
                        </p>

                    </div>

                ) : (

                    <div className="grid grid-cols-2 gap-5">

                        {filteredCases.map(
                            (caseData) => (

                                <CaseCard
                                    key={caseData.id}
                                    caseData={caseData}
                                    sourceFir={selectedFir}
                                />

                            )
                        )}

                    </div>

                )}

            </div>

        </div>
    );
}


// ============================================================
// CASE CARD
// ============================================================

function CaseCard({
    caseData,
    sourceFir,
}: {
    caseData: CaseData;
    sourceFir: string;
}) {

    return (

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition hover:border-cyan-500/20 hover:bg-white/[0.045]">

            <div className="flex items-start justify-between">

                <div className="flex items-start gap-4">

                    <div className="rounded-xl bg-cyan-500/10 p-3">

                        <FileText
                            size={21}
                            className="text-cyan-400"
                        />

                    </div>


                    <div>

                        <div className="text-lg font-semibold">
                            {caseData.fir_number ||
                                caseData.id}
                        </div>

                        <div className="mt-1 text-xs text-white/30">
                            {caseData.id}
                        </div>

                    </div>

                </div>


                <span
                    className={`rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wider ${caseData.status === "ACTIVE"
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-white/10 text-white/40"
                        }`}
                >
                    {caseData.status ||
                        "UNKNOWN"}
                </span>

            </div>


            {/* DETAILS */}

            <div className="mt-6 grid grid-cols-2 gap-4">

                <Detail
                    label="Case Type"
                    value={
                        caseData.case_type ||
                        "—"
                    }
                />

                <Detail
                    label="Police Station"
                    value={
                        caseData.police_station ||
                        "—"
                    }
                />

                <Detail
                    label="Evidence"
                    value={String(
                        caseData.evidence_count
                    )}
                />

                <Detail
                    label="Relationships"
                    value={String(
                        caseData.relationship_count
                    )}
                />

                <Detail
                    label="Incident"
                    value={
                        formatDate(
                            caseData.incident_date
                        )
                    }
                />

                <Detail
                    label="Registered"
                    value={
                        formatDate(
                            caseData.registered_date
                        )
                    }
                />

            </div>


            {/* CONNECTION */}

            <div className="mt-5 rounded-xl border border-cyan-500/10 bg-cyan-500/[0.025] p-3">

                <div className="text-[10px] uppercase tracking-wider text-cyan-400">
                    Graph Connection
                </div>

                <div className="mt-1 text-xs text-white/40">
                    Connected to the selected FIR through shared investigative entities.
                </div>

            </div>


            {/* ACTION */}

            <div className="mt-5 flex justify-end">

                <Link
                    href={`/analysis?case=${encodeURIComponent(
                        caseData.id
                    )}&source=${encodeURIComponent(
                        sourceFir
                    )}`}
                    className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-black transition hover:bg-cyan-400"
                >

                    Analyse Case

                    <ArrowRight
                        size={16}
                    />

                </Link>

            </div>

        </div>
    );
}


// ============================================================
// HELPERS
// ============================================================

function Detail({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div>

            <div className="text-[10px] uppercase tracking-wider text-white/20">
                {label}
            </div>

            <div className="mt-1 truncate text-sm text-white/60">
                {value}
            </div>

        </div>
    );
}


function formatDate(
    value: string | null
): string {

    if (!value) {
        return "—";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return value;
    }

    return date.toLocaleDateString();
}