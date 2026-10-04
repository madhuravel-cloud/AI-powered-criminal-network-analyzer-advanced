"use client";

import Link from "next/link";
import { Search, ArrowRight } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getCases, type CaseData } from "@/lib/api";

export default function CasesPage() {
    const [cases, setCases] = useState<CaseData[]>([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // =====================================================
    // LOAD REAL CASES FROM FASTAPI
    // =====================================================

    useEffect(() => {
        async function loadCases() {
            try {
                setLoading(true);
                setError(null);

                const data = await getCases();

                setCases(data);
            } catch (err) {
                console.error("Failed to load cases:", err);

                setError(
                    err instanceof Error
                        ? err.message
                        : "Failed to load cases"
                );
            } finally {
                setLoading(false);
            }
        }

        loadCases();
    }, []);

    // =====================================================
    // SEARCH
    // =====================================================

    const filteredCases = useMemo(() => {
        const query = search.toLowerCase().trim();

        if (!query) {
            return cases;
        }

        return cases.filter((item) =>
            [
                item.id,
                item.fir_number,
                item.case_type,
                item.police_station,
                item.status,
            ]
                .filter(Boolean)
                .some((value) =>
                    String(value).toLowerCase().includes(query)
                )
        );
    }, [search, cases]);

    // =====================================================
    // FORMAT DATE
    // =====================================================

    function formatDate(date: string | null) {
        if (!date) {
            return "—";
        }

        return date.split("T")[0];
    }

    // =====================================================
    // DISPLAY ID
    // =====================================================

    function displayCaseId(item: CaseData) {
        if (item.fir_number) {
            return item.id.replace("case:", "");
        }

        return item.id.replace("case:", "");
    }

    return (
        <div className="min-h-screen bg-[#05070b] text-white">
            <div className="p-8">

                {/* Header */}
                <div className="mb-8">

                    <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                        Investigation Management
                    </p>

                    <h1 className="mt-2 text-3xl font-bold">
                        Cases
                    </h1>

                    <p className="mt-2 text-sm text-white/40">
                        Browse and investigate registered cases
                    </p>

                </div>

                {/* Search */}
                <div className="mb-6 flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4">

                    <Search
                        size={18}
                        className="text-white/30"
                    />

                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search FIR, case type or police station..."
                        className="h-12 w-full bg-transparent text-sm text-white outline-none placeholder:text-white/25"
                    />

                </div>

                {/* Loading */}
                {loading && (
                    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]">
                        <div className="px-6 py-12 text-center text-sm text-white/40">
                            Loading cases...
                        </div>
                    </div>
                )}

                {/* Error */}
                {!loading && error && (
                    <div className="overflow-hidden rounded-2xl border border-red-400/20 bg-red-400/5">
                        <div className="px-6 py-12 text-center">

                            <p className="text-sm text-red-400">
                                Failed to load cases
                            </p>

                            <p className="mt-2 text-xs text-white/30">
                                {error}
                            </p>

                        </div>
                    </div>
                )}

                {/* Cases */}
                {!loading && !error && (
                    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]">

                        <div className="overflow-x-auto">

                            <table className="w-full text-left">

                                <thead className="border-b border-white/10 bg-white/[0.03]">

                                    <tr className="text-xs uppercase tracking-wider text-white/30">

                                        <th className="px-6 py-4">
                                            FIR Number
                                        </th>

                                        <th className="px-6 py-4">
                                            Case Type
                                        </th>

                                        <th className="px-6 py-4">
                                            Police Station
                                        </th>

                                        <th className="px-6 py-4">
                                            Incident Date
                                        </th>

                                        <th className="px-6 py-4">
                                            Status
                                        </th>

                                        <th className="px-6 py-4">
                                            Action
                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filteredCases.map((item) => (

                                        <tr
                                            key={item.id}
                                            className="border-b border-white/5 transition-colors hover:bg-white/[0.03]"
                                        >

                                            <td className="px-6 py-5">

                                                <span className="font-medium text-cyan-400">
                                                    {displayCaseId(item)}
                                                </span>

                                            </td>

                                            <td className="px-6 py-5 text-sm text-white/70">
                                                {item.case_type || "—"}
                                            </td>

                                            <td className="px-6 py-5 text-sm text-white/50">
                                                {item.police_station || "—"}
                                            </td>

                                            <td className="px-6 py-5 text-sm text-white/50">
                                                {formatDate(item.incident_date)}
                                            </td>

                                            <td className="px-6 py-5">

                                                <span
                                                    className={`rounded-full px-3 py-1 text-xs font-medium ${item.status === "ACTIVE"
                                                        ? "bg-emerald-400/10 text-emerald-400"
                                                        : item.status === "ONGOING"
                                                            ? "bg-cyan-400/10 text-cyan-400"
                                                            : "bg-white/10 text-white/40"
                                                        }`}
                                                >
                                                    {item.status || "UNKNOWN"}
                                                </span>

                                            </td>

                                            <td className="px-6 py-5">

                                                <Link
                                                    href={`/analysis?case=${encodeURIComponent(
                                                        item.id
                                                    )}`}
                                                    className="inline-flex items-center gap-2 rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2 text-xs font-medium text-cyan-400 transition hover:bg-cyan-400/10"
                                                >
                                                    Analyze

                                                    <ArrowRight size={14} />

                                                </Link>

                                            </td>

                                        </tr>

                                    ))}

                                </tbody>

                            </table>

                        </div>

                        {filteredCases.length === 0 && (
                            <div className="px-6 py-12 text-center text-sm text-white/30">
                                No cases found.
                            </div>
                        )}

                    </div>
                )}

            </div>
        </div>
    );
}