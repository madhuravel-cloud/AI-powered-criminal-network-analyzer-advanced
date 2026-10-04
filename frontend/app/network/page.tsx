"use client";

import Link from "next/link";
import {
    ArrowLeft,
    Network,
    Search,
} from "lucide-react";
import { useState } from "react";

const nodes = [
    {
        id: "ravi",
        label: "Ravi",
        type: "Person",
        x: 50,
        y: 45,
    },
    {
        id: "kumar",
        label: "Kumar",
        type: "Person",
        x: 25,
        y: 28,
    },
    {
        id: "joseph",
        label: "Joseph",
        type: "Person",
        x: 75,
        y: 28,
    },
    {
        id: "phone",
        label: "Phone",
        type: "CDR",
        x: 20,
        y: 65,
    },
    {
        id: "vehicle",
        label: "Vehicle",
        type: "Vehicle",
        x: 80,
        y: 65,
    },
    {
        id: "location",
        label: "Connaught Place",
        type: "Location",
        x: 50,
        y: 82,
    },
];

const edges = [
    ["ravi", "kumar"],
    ["ravi", "joseph"],
    ["ravi", "phone"],
    ["ravi", "vehicle"],
    ["ravi", "location"],
];

export default function NetworkPage() {
    const [search, setSearch] = useState("");

    const visibleNodes = nodes.filter((node) =>
        node.label
            .toLowerCase()
            .includes(search.toLowerCase())
    );

    return (
        <section className="min-h-screen bg-[#070b12] p-8 text-white">
            <div className="mx-auto max-w-7xl">

                {/* HEADER */}
                <div className="mb-6 flex items-end justify-between">
                    <div>
                        <Link
                            href="/"
                            className="mb-4 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
                        >
                            <ArrowLeft size={16} />
                            Back to Overview
                        </Link>

                        <h1 className="text-3xl font-semibold">
                            Master Network
                        </h1>

                        <p className="mt-1 text-slate-400">
                            Multilayer relationship view for the active investigation.
                        </p>
                    </div>

                    {/* SEARCH */}
                    <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5">
                        <Search
                            size={16}
                            className="text-slate-500"
                        />

                        <input
                            value={search}
                            onChange={(e) =>
                                setSearch(e.target.value)
                            }
                            placeholder="Find entity..."
                            className="w-44 bg-transparent text-sm outline-none placeholder:text-slate-600"
                        />
                    </div>
                </div>

                {/* MAIN GRID */}
                <div className="grid gap-5 xl:grid-cols-[1fr_280px]">

                    {/* GRAPH */}
                    <div className="relative h-[650px] overflow-hidden rounded-2xl border border-white/10 bg-[#090e17]">

                        {/* GRAPH TITLE */}
                        <div className="absolute left-5 top-5 z-10 flex items-center gap-2 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-slate-400">
                            <Network size={15} />
                            Master Temporal Multilayer Graph
                        </div>

                        {/* EDGES */}
                        <svg
                            viewBox="0 0 100 100"
                            preserveAspectRatio="none"
                            className="absolute inset-0 h-full w-full"
                        >
                            {edges.map(([a, b], index) => {
                                const source = nodes.find(
                                    (n) => n.id === a
                                );

                                const target = nodes.find(
                                    (n) => n.id === b
                                );

                                if (!source || !target) {
                                    return null;
                                }

                                return (
                                    <line
                                        key={index}
                                        x1={`${source.x}%`}
                                        y1={`${source.y}%`}
                                        x2={`${target.x}%`}
                                        y2={`${target.y}%`}
                                        stroke="rgba(148,163,184,.22)"
                                        strokeWidth=".25"
                                    />
                                );
                            })}
                        </svg>

                        {/* NODES */}
                        {visibleNodes.map((node) => (
                            <div
                                key={node.id}
                                className="absolute -translate-x-1/2 -translate-y-1/2"
                                style={{
                                    left: `${node.x}%`,
                                    top: `${node.y}%`,
                                }}
                            >
                                <div
                                    className={`flex h-16 min-w-16 items-center justify-center rounded-full border px-4 text-center text-xs ${node.type === "Person"
                                        ? "border-white/30 bg-white/10"
                                        : "border-white/10 bg-slate-900"
                                        }`}
                                >
                                    {node.label}
                                </div>

                                <div className="mt-2 text-center text-[10px] text-slate-600">
                                    {node.type}
                                </div>
                            </div>
                        ))}

                        {visibleNodes.length === 0 && (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="rounded-xl border border-white/10 bg-black/30 px-5 py-3 text-sm text-slate-500">
                                    No matching entity found.
                                </div>
                            </div>
                        )}
                    </div>

                    {/* GRAPH LAYERS */}
                    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
                        <h2 className="font-medium">
                            Graph Layers
                        </h2>

                        <div className="mt-5 space-y-3">
                            {[
                                "FIR",
                                "COURT",
                                "CDR",
                                "VEHICLE",
                                "CCTV",
                                "FINANCIAL",
                                "LOCATION",
                            ].map((layer) => (
                                <div
                                    key={layer}
                                    className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] px-3 py-3"
                                >
                                    <span className="text-sm text-slate-300">
                                        {layer}
                                    </span>

                                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                                </div>
                            ))}
                        </div>

                        {/* STATUS */}
                        <div className="mt-6 border-t border-white/10 pt-5">
                            <div className="text-xs text-slate-500">
                                GRAPH STATUS
                            </div>

                            <div className="mt-2 text-sm text-emerald-400">
                                Master graph connected
                            </div>

                            <div className="mt-1 text-xs text-slate-600">
                                Neo4j • NetworkX analysis
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}