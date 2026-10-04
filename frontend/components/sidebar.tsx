"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    FolderOpen,
    FileText,
    Network,
    Brain,
    FileSearch,
    Phone,
    Video,
    Scale,
    Car,
    Wallet,
    MapPin,
    Shield,
} from "lucide-react";

const mainNavigation = [
    {
        label: "Overview",
        href: "/",
        icon: LayoutDashboard,
    },
    {
        label: "Cases",
        href: "/cases",
        icon: FolderOpen,
    },
    {
        label: "Evidence",
        href: "/evidence",
        icon: FileText,
    },
    {
        label: "Network",
        href: "/network",
        icon: Network,
    },
    {
        label: "Analysis",
        href: "/analysis",
        icon: Brain,
    },
];

const sourceNavigation = [
    {
        label: "FIR",
        href: "/sources/fir",
        icon: FileSearch,
    },
    {
        label: "CDR",
        href: "/sources/cdr",
        icon: Phone,
    },
    {
        label: "CCTV",
        href: "/sources/cctv",
        icon: Video,
    },
    {
        label: "Court",
        href: "/sources/court",
        icon: Scale,
    },
    {
        label: "Vehicle",
        href: "/sources/vehicle",
        icon: Car,
    },
    {
        label: "Financial",
        href: "/sources/financial",
        icon: Wallet,
    },
    {
        label: "Location",
        href: "/sources/location",
        icon: MapPin,
    },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden min-h-screen w-64 shrink-0 border-r border-white/10 bg-[#090e17] lg:flex lg:flex-col">
            {/* BRAND */}
            <div className="border-b border-white/10 p-6">
                <Link href="/" className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                        <Shield size={20} />
                    </div>

                    <div>
                        <div className="font-semibold text-white">
                            Criminal Network
                        </div>

                        <div className="text-xs text-slate-500">
                            Analyzer
                        </div>
                    </div>
                </Link>
            </div>

            {/* NAVIGATION */}
            <div className="flex-1 overflow-y-auto p-4">
                <div className="mb-3 px-3 text-[10px] font-semibold tracking-[0.18em] text-slate-600">
                    INVESTIGATION
                </div>

                <nav className="space-y-1">
                    {mainNavigation.map((item) => {
                        const Icon = item.icon;

                        const active =
                            item.href === "/"
                                ? pathname === "/"
                                : pathname.startsWith(item.href);

                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active
                                    ? "bg-white/10 text-white"
                                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                                    }`}
                            >
                                <Icon size={17} />

                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* SOURCES */}
                <div className="mb-3 mt-8 px-3 text-[10px] font-semibold tracking-[0.18em] text-slate-600">
                    DATA SOURCES
                </div>

                <nav className="space-y-1">
                    {sourceNavigation.map((item) => {
                        const Icon = item.icon;

                        const active = pathname.startsWith(item.href);

                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active
                                    ? "bg-white/10 text-white"
                                    : "text-slate-500 hover:bg-white/5 hover:text-slate-300"
                                    }`}
                            >
                                <Icon size={16} />

                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* STATUS */}
            <div className="border-t border-white/10 p-4">
                <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
                    <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-400" />

                        <span className="text-xs text-slate-400">
                            System Operational
                        </span>
                    </div>

                    <div className="mt-2 text-[10px] text-slate-600">
                        Neo4j • PostgreSQL • FastAPI
                    </div>
                </div>
            </div>
        </aside>
    );
}