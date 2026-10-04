"use client";

import Link from "next/link";
import {
    ArrowLeft,
    Upload,
    FileText,
    Phone,
    Video,
    Scale,
    Car,
    Wallet,
    MapPin,
} from "lucide-react";

const sources = [
    {
        name: "FIR",
        description:
            "First Information Reports and case documents",
        count: 10,
        icon: FileText,
    },
    {
        name: "CDR",
        description:
            "Call detail records and communication metadata",
        count: 10,
        icon: Phone,
    },
    {
        name: "CCTV",
        description:
            "Camera observations and video evidence",
        count: 10,
        icon: Video,
    },
    {
        name: "Court",
        description:
            "Court cases, hearings and party records",
        count: 10,
        icon: Scale,
    },
    {
        name: "Vehicle",
        description:
            "Vehicle associations and records",
        count: 10,
        icon: Car,
    },
    {
        name: "Financial",
        description:
            "Transactions and account relationships",
        count: 10,
        icon: Wallet,
    },
    {
        name: "Location",
        description:
            "Movement and location records",
        count: 10,
        icon: MapPin,
    },
];

export default function EvidencePage() {
    return (
        <section className="min-h-screen bg-[#070b12] p-8 text-white">
            <div className="mx-auto max-w-7xl">

                {/* HEADER */}
                <Link
                    href="/"
                    className="mb-4 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
                >
                    <ArrowLeft size={16} />
                    Back to Overview
                </Link>

                <div className="mb-8 flex items-end justify-between">
                    <div>
                        <h1 className="text-3xl font-semibold">
                            Evidence
                        </h1>

                        <p className="mt-1 text-slate-400">
                            Unified evidence intake and source management.
                        </p>
                    </div>

                    <button className="flex items-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-medium text-black transition hover:bg-slate-200">
                        <Upload size={17} />
                        Add Evidence
                    </button>
                </div>

                {/* STATS */}
                <div className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Stat
                        label="TOTAL EVIDENCE"
                        value="70"
                    />

                    <Stat
                        label="SOURCE TYPES"
                        value="7"
                    />

                    <Stat
                        label="CASES COVERED"
                        value="20"
                    />

                    <Stat
                        label="LINKED ENTITIES"
                        value="84"
                    />
                </div>

                {/* SOURCES */}
                <h2 className="mb-4 text-lg font-medium">
                    Evidence Sources
                </h2>

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    {sources.map((source) => {
                        const Icon = source.icon;

                        return (
                            <div
                                key={source.name}
                                className="group rounded-2xl border border-white/10 bg-white/[0.025] p-6 transition hover:border-white/20 hover:bg-white/[0.04]"
                            >
                                <div className="mb-5 flex items-start justify-between">
                                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10">
                                        <Icon size={20} />
                                    </div>

                                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-400">
                                        {source.count} records
                                    </span>
                                </div>

                                <h3 className="text-lg font-medium">
                                    {source.name}
                                </h3>

                                <p className="mt-2 text-sm leading-6 text-slate-500">
                                    {source.description}
                                </p>

                                <button className="mt-5 text-sm text-slate-300 transition group-hover:text-white">
                                    View evidence →
                                </button>
                            </div>
                        );
                    })}
                </div>

                {/* UPLOAD AREA */}
                <div className="mt-8 rounded-2xl border border-dashed border-white/15 bg-white/[0.02] p-10 text-center">
                    <Upload
                        size={28}
                        className="mx-auto mb-4 text-slate-600"
                    />

                    <h3 className="font-medium">
                        Add new evidence
                    </h3>

                    <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
                        Upload FIRs, CDR files, CCTV metadata,
                        court records, vehicle records, financial
                        data or location evidence.
                    </p>

                    <button className="mt-5 rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/5">
                        Select Evidence
                    </button>
                </div>
            </div>
        </section>
    );
}

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