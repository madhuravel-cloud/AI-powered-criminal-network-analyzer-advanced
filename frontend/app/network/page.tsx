"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Network,
    Search,
    RotateCcw,
    ChevronLeft,
    Database,
    ArrowRight,
    ExternalLink,
} from "lucide-react";

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

const CASE_ID = "case:FIR-101-2025";

type GraphNode = {
    id: string;
    label: string;
    type: string;
    source_layer?: string | null;
    properties?: Record<string, unknown>;
};

type GraphEdge = {
    id: string;
    source: string;
    target: string;
    relationship: string;
    properties?: Record<string, unknown>;
};

type NetworkResponse = {
    status: string;
    count: number;
    nodes: GraphNode[];
    edges: GraphEdge[];
};

type FocusResponse = {
    status: string;
    selected_entity: GraphNode;
    nodes: GraphNode[];
    edges: GraphEdge[];
    connection_count: number;
};

type HistoryItem = {
    node: GraphNode;
    graph: FocusResponse;
};

export default function NetworkPage() {
    const [mainGraph, setMainGraph] =
        useState<NetworkResponse | null>(null);

    const [focusedGraph, setFocusedGraph] =
        useState<FocusResponse | null>(null);

    const [selectedNode, setSelectedNode] =
        useState<GraphNode | null>(null);

    const [selectedEdge, setSelectedEdge] =
        useState<GraphEdge | null>(null);

    const [history, setHistory] =
        useState<HistoryItem[]>([]);

    const [loading, setLoading] =
        useState(true);

    const [focusLoading, setFocusLoading] =
        useState(false);

    const [search, setSearch] =
        useState("");

    // ==========================================================
    // MASTER GRAPH
    // ==========================================================

    async function loadMainGraph() {
        try {
            setLoading(true);

            const response = await fetch(
                `${API_BASE_URL}/network?case_id=${encodeURIComponent(
                    CASE_ID
                )}`,
                {
                    cache: "no-store",
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Network request failed: ${response.status}`
                );
            }

            const data: NetworkResponse =
                await response.json();

            setMainGraph(data);
        } catch (error) {
            console.error(
                "Network loading failed:",
                error
            );
        } finally {
            setLoading(false);
        }
    }

    // ==========================================================
    // ENTITY GRAPH
    // ==========================================================

    async function loadEntityGraph(
        node: GraphNode,
        addHistory = true
    ) {
        try {
            setFocusLoading(true);

            setSelectedNode(node);
            setSelectedEdge(null);

            const response = await fetch(
                `${API_BASE_URL}/network/entity/${encodeURIComponent(
                    node.id
                )}?limit=6`,
                {
                    cache: "no-store",
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Entity request failed: ${response.status}`
                );
            }

            const data: FocusResponse =
                await response.json();

            if (
                addHistory &&
                focusedGraph &&
                selectedNode
            ) {
                setHistory((previous) => [
                    ...previous,
                    {
                        node: selectedNode,
                        graph: focusedGraph,
                    },
                ]);
            }

            setFocusedGraph(data);
        } catch (error) {
            console.error(
                "Entity graph loading failed:",
                error
            );
        } finally {
            setFocusLoading(false);
        }
    }

    // ==========================================================
    // BACK
    // ==========================================================

    function goBack() {
        if (!history.length) {
            resetGraph();
            return;
        }

        const previous =
            history[history.length - 1];

        setHistory((items) =>
            items.slice(0, -1)
        );

        setFocusedGraph(previous.graph);
        setSelectedNode(previous.node);
        setSelectedEdge(null);
    }

    // ==========================================================
    // RESET
    // ==========================================================

    function resetGraph() {
        setFocusedGraph(null);
        setSelectedNode(null);
        setSelectedEdge(null);
        setHistory([]);
    }

    // ==========================================================
    // INITIAL LOAD
    // ==========================================================

    useEffect(() => {
        loadMainGraph();
    }, []);

    // ==========================================================
    // SEARCH
    // ==========================================================

    const filteredNodes = useMemo(() => {
        if (!mainGraph?.nodes) {
            return [];
        }

        const query =
            search.toLowerCase().trim();

        if (!query) {
            return mainGraph.nodes;
        }

        return mainGraph.nodes.filter(
            (node) =>
                node.label
                    ?.toLowerCase()
                    .includes(query) ||
                node.id
                    ?.toLowerCase()
                    .includes(query) ||
                node.type
                    ?.toLowerCase()
                    .includes(query)
        );
    }, [mainGraph, search]);

    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-[#05070b]">
                <div className="text-center">

                    <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />

                    <p className="text-sm text-white/50">
                        Loading investigation network...
                    </p>

                </div>
            </div>
        );
    }

    // ==========================================================
    // PAGE
    // ==========================================================

    return (
        <div className="min-h-screen bg-[#05070b] text-white">

            {/* HEADER */}

            <div className="border-b border-white/10 bg-[#080b12]">

                <div className="flex items-center justify-between px-8 py-6">

                    <div>

                        <div className="mb-2 flex items-center gap-3">

                            <Network
                                className="text-cyan-400"
                                size={24}
                            />

                            <h1 className="text-2xl font-bold">
                                Network Intelligence
                            </h1>

                        </div>

                        <p className="text-sm text-white/40">
                            Evidence-linked temporal investigation
                            network
                        </p>

                    </div>

                    <div className="flex items-center gap-3">

                        {focusedGraph && (
                            <button
                                onClick={
                                    history.length
                                        ? goBack
                                        : resetGraph
                                }
                                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/60 transition hover:bg-white/[0.08] hover:text-white"
                            >
                                <ChevronLeft size={16} />

                                {history.length
                                    ? "Previous"
                                    : "Full Network"}
                            </button>
                        )}

                        <button
                            onClick={loadMainGraph}
                            className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-white/50 transition hover:bg-white/[0.08] hover:text-white"
                        >
                            <RotateCcw size={17} />
                        </button>

                    </div>

                </div>

            </div>

            {/* CONTENT */}

            <div className="p-8">

                {focusedGraph ? (
                    <FocusedNetwork
                        graph={focusedGraph}
                        selectedNode={selectedNode}
                        selectedEdge={selectedEdge}
                        loading={focusLoading}
                        history={history}
                        onNodeClick={(node) =>
                            loadEntityGraph(node)
                        }
                        onEdgeClick={(edge) =>
                            setSelectedEdge(edge)
                        }
                    />
                ) : (
                    <MasterNetwork
                        nodes={filteredNodes}
                        edges={mainGraph?.edges || []}
                        search={search}
                        setSearch={setSearch}
                        onNodeClick={loadEntityGraph}
                    />
                )}

            </div>

        </div>
    );
}


// ============================================================
// MASTER NETWORK
// ============================================================

function MasterNetwork({
    nodes,
    edges,
    search,
    setSearch,
    onNodeClick,
}: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    search: string;
    setSearch: (value: string) => void;
    onNodeClick: (node: GraphNode) => void;
}) {
    const groups = {
        People: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "person"
        ),

        Phones: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "phone"
        ),

        Vehicles: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "vehicle"
        ),

        Locations: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "location"
        ),

        Accounts: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "account"
        ),

        Organizations: nodes.filter(
            (node) =>
                node.type?.toLowerCase() ===
                "organization"
        ),

        Other: nodes.filter((node) => {
            const type =
                node.type?.toLowerCase();

            return ![
                "person",
                "phone",
                "vehicle",
                "location",
                "account",
                "organization",
            ].includes(type);
        }),
    };

    return (
        <div>

            {/* TOP */}

            <div className="mb-6 flex items-center justify-between">

                <div>

                    <h2 className="text-lg font-semibold">
                        Investigation Network
                    </h2>

                    <p className="mt-1 text-xs text-white/35">
                        Select an entity to inspect its local
                        network
                    </p>

                </div>

                <div className="flex items-center gap-3">

                    <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">

                        <Search
                            size={15}
                            className="text-white/30"
                        />

                        <input
                            value={search}
                            onChange={(e) =>
                                setSearch(e.target.value)
                            }
                            placeholder="Search entity..."
                            className="w-52 bg-transparent text-sm text-white outline-none placeholder:text-white/25"
                        />

                    </div>

                    <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/[0.05] px-3 py-2 text-xs text-cyan-300">
                        {nodes.length} entities
                    </div>

                </div>

            </div>

            {/* GROUPS */}

            <div className="space-y-8">

                {Object.entries(groups).map(
                    ([group, groupNodes]) => {

                        if (!groupNodes.length) {
                            return null;
                        }

                        return (
                            <div key={group}>

                                <div className="mb-3 flex items-center gap-3">

                                    <h3 className="text-sm font-semibold text-white/70">
                                        {group}
                                    </h3>

                                    <span className="rounded-full bg-white/[0.06] px-2 py-0.5 text-[10px] text-white/30">
                                        {groupNodes.length}
                                    </span>

                                </div>

                                <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-6">

                                    {groupNodes.map((node) => {

                                        const connections =
                                            edges.filter(
                                                (edge) =>
                                                    edge.source === node.id ||
                                                    edge.target === node.id
                                            ).length;

                                        return (
                                            <button
                                                key={node.id}
                                                onClick={() =>
                                                    onNodeClick(node)
                                                }
                                                className="group rounded-xl border border-white/10 bg-[#0a0e16] p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-cyan-400/40 hover:bg-cyan-400/[0.04]"
                                            >

                                                <div className="mb-3 flex items-center justify-between">

                                                    <div className="h-2.5 w-2.5 rounded-full bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.65)]" />

                                                    <span className="text-[10px] text-white/25">
                                                        {connections} links
                                                    </span>

                                                </div>

                                                <div className="truncate text-sm font-medium text-white/80 group-hover:text-cyan-300">
                                                    {node.label}
                                                </div>

                                                <div className="mt-1 truncate text-[10px] text-white/25">
                                                    {node.id}
                                                </div>

                                            </button>
                                        );
                                    })}

                                </div>

                            </div>
                        );
                    }
                )}

            </div>

        </div>
    );
}


// ============================================================
// FOCUSED NETWORK
// ============================================================

function FocusedNetwork({
    graph,
    selectedNode,
    selectedEdge,
    loading,
    history,
    onNodeClick,
    onEdgeClick,
}: {
    graph: FocusResponse;
    selectedNode: GraphNode | null;
    selectedEdge: GraphEdge | null;
    loading: boolean;
    history: HistoryItem[];
    onNodeClick: (node: GraphNode) => void;
    onEdgeClick: (edge: GraphEdge) => void;
}) {
    const center =
        selectedNode ||
        graph.selected_entity;

    const neighbors =
        graph.nodes.filter(
            (node) =>
                node.id !== center.id
        );

    return (
        <div>

            {/* ======================================================
          FOCUS HEADER
      ====================================================== */}

            <div className="mb-5">

                <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-white/25">

                    <span>Master Network</span>

                    {history.map((item) => (
                        <span key={item.node.id}>
                            <ArrowRight
                                size={10}
                                className="mx-1 inline"
                            />

                            {item.node.label}
                        </span>
                    ))}

                    <ArrowRight
                        size={10}
                        className="mx-1 inline"
                    />

                    <span className="text-cyan-400">
                        {center.label}
                    </span>

                </div>

            </div>

            <div className="mb-6 flex items-center justify-between">

                <div>

                    <div className="mb-2 flex items-center gap-3">

                        <div className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.8)]" />

                        <h2 className="text-xl font-semibold">
                            {center.label}
                        </h2>

                        <span className="rounded-md border border-cyan-400/20 bg-cyan-400/[0.05] px-2 py-1 text-[10px] uppercase tracking-wider text-cyan-300">
                            {center.type}
                        </span>

                    </div>

                    <p className="text-xs text-white/35">
                        Focused local network ·{" "}
                        {graph.connection_count} connected
                        entities
                    </p>

                </div>

                {loading && (
                    <div className="flex items-center gap-2 text-xs text-cyan-300">

                        <div className="h-3 w-3 animate-spin rounded-full border border-cyan-400/30 border-t-cyan-400" />

                        Updating network...

                    </div>
                )}

            </div>

            {/* ======================================================
          MAIN AREA
      ====================================================== */}

            <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_330px]">

                {/* GRAPH */}

                <div className="relative h-[620px] overflow-hidden rounded-2xl border border-white/10 bg-[#080b12]">

                    {/* GRID */}

                    <div
                        className="absolute inset-0 opacity-20"
                        style={{
                            backgroundImage:
                                "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
                            backgroundSize:
                                "40px 40px",
                        }}
                    />

                    {/* CENTER */}

                    <div className="absolute left-1/2 top-1/2 z-20 -translate-x-1/2 -translate-y-1/2">

                        <div className="relative">

                            <div className="absolute inset-0 animate-pulse rounded-full bg-cyan-400/20 blur-xl" />

                            <div className="relative flex h-28 w-28 flex-col items-center justify-center rounded-full border-2 border-cyan-400 bg-[#07141b] shadow-[0_0_35px_rgba(34,211,238,0.35)]">

                                <div className="mb-2 h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,1)]" />

                                <span className="max-w-20 truncate text-sm font-semibold text-white">
                                    {center.label}
                                </span>

                                <span className="mt-1 text-[9px] uppercase tracking-wider text-cyan-300/70">
                                    {center.type}
                                </span>

                            </div>

                        </div>

                    </div>

                    {/* CONNECTIONS */}

                    {neighbors.map(
                        (node, index) => {

                            const angle =
                                (index /
                                    Math.max(
                                        neighbors.length,
                                        1
                                    )) *
                                Math.PI *
                                2 -
                                Math.PI / 2;

                            const radius = 215;

                            const x =
                                Math.cos(angle) *
                                radius;

                            const y =
                                Math.sin(angle) *
                                radius;

                            const relationship =
                                graph.edges.find(
                                    (edge) =>
                                        (edge.source ===
                                            center.id &&
                                            edge.target ===
                                            node.id) ||
                                        (edge.target ===
                                            center.id &&
                                            edge.source ===
                                            node.id)
                                );

                            return (
                                <div
                                    key={node.id}
                                    className="absolute left-1/2 top-1/2"
                                    style={{
                                        transform:
                                            `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                                    }}
                                >

                                    {/* LINE */}

                                    <div
                                        className="pointer-events-none absolute left-1/2 top-1/2 h-px origin-left bg-cyan-400/20"
                                        style={{
                                            width: `${radius}px`,
                                            transform:
                                                `rotate(${Math.atan2(
                                                    -y,
                                                    -x
                                                )}rad)`,
                                        }}
                                    />

                                    {/* RELATIONSHIP */}

                                    {relationship && (
                                        <button
                                            onClick={(event) => {
                                                event.stopPropagation();
                                                onEdgeClick(
                                                    relationship
                                                );
                                            }}
                                            className="absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap rounded-md border border-white/10 bg-[#080b12]/90 px-2 py-1 text-[8px] uppercase tracking-wider text-white/35 backdrop-blur transition hover:border-cyan-400/40 hover:text-cyan-300"
                                        >
                                            {relationship.relationship}
                                        </button>
                                    )}

                                    {/* NODE */}

                                    <button
                                        onClick={() =>
                                            onNodeClick(node)
                                        }
                                        className="group relative z-20 flex h-24 w-24 flex-col items-center justify-center rounded-full border border-white/15 bg-[#0c111b] shadow-xl transition-all duration-200 hover:scale-110 hover:border-cyan-400/60 hover:shadow-[0_0_25px_rgba(34,211,238,0.2)]"
                                    >

                                        <div className="mb-1 h-2.5 w-2.5 rounded-full bg-white/50 transition group-hover:bg-cyan-400 group-hover:shadow-[0_0_10px_rgba(34,211,238,0.8)]" />

                                        <span className="max-w-16 truncate text-xs font-medium text-white/80 group-hover:text-cyan-300">
                                            {node.label}
                                        </span>

                                        <span className="mt-1 max-w-16 truncate text-[8px] uppercase tracking-wider text-white/25">
                                            {node.type}
                                        </span>

                                    </button>

                                </div>
                            );
                        }
                    )}

                    {/* EMPTY */}

                    {!neighbors.length && (
                        <div className="absolute inset-0 flex items-center justify-center">

                            <div className="rounded-xl border border-white/10 bg-black/20 px-6 py-4 text-sm text-white/40">
                                No connected entities found.
                            </div>

                        </div>
                    )}

                    {/* LEGEND */}

                    <div className="absolute bottom-5 left-5 rounded-xl border border-white/10 bg-[#080b12]/90 p-4 backdrop-blur">

                        <div className="mb-2 flex items-center gap-2">

                            <Database
                                size={14}
                                className="text-cyan-400"
                            />

                            <span className="text-xs font-semibold text-white/70">
                                Local Network
                            </span>

                        </div>

                        <p className="text-[10px] text-white/30">
                            Selected entity + up to 6 direct
                            connections
                        </p>

                    </div>

                </div>

                {/* ====================================================
            RIGHT INVESTIGATION PANEL
            ==================================================== */}

                <div className="space-y-4">

                    {/* ENTITY */}

                    <div className="rounded-2xl border border-white/10 bg-[#080b12] p-5">

                        <div className="mb-4 flex items-center gap-2">

                            <div className="h-2.5 w-2.5 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.7)]" />

                            <span className="text-xs font-semibold uppercase tracking-wider text-white/50">
                                Selected Entity
                            </span>

                        </div>

                        <div className="text-lg font-semibold text-white">
                            {center.label}
                        </div>

                        <div className="mt-1 break-all text-[10px] text-white/25">
                            {center.id}
                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-2">

                            <SmallStat
                                title="Type"
                                value={center.type}
                            />

                            <SmallStat
                                title="Connections"
                                value={String(
                                    graph.connection_count
                                )}
                            />

                        </div>

                    </div>

                    {/* RELATIONSHIP */}

                    {selectedEdge ? (
                        <RelationshipPanel
                            edge={selectedEdge}
                            center={center}
                        />
                    ) : (
                        <div className="rounded-2xl border border-white/10 bg-[#080b12] p-5">

                            <div className="mb-3 flex items-center gap-2">

                                <Network
                                    size={14}
                                    className="text-cyan-400"
                                />

                                <span className="text-xs font-semibold uppercase tracking-wider text-white/50">
                                    Relationship
                                </span>

                            </div>

                            <p className="text-xs leading-5 text-white/30">
                                Click a relationship label in the
                                graph to inspect how the entities are
                                connected.
                            </p>

                        </div>
                    )}

                    {/* SOURCE */}

                    <div className="rounded-2xl border border-white/10 bg-[#080b12] p-5">

                        <div className="mb-3 flex items-center gap-2">

                            <Database
                                size={14}
                                className="text-cyan-400"
                            />

                            <span className="text-xs font-semibold uppercase tracking-wider text-white/50">
                                Source Layer
                            </span>

                        </div>

                        <div className="rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2 text-xs text-white/50">
                            {center.source_layer ||
                                "Master Graph"}
                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}


// ============================================================
// RELATIONSHIP PANEL
// ============================================================

function RelationshipPanel({
    edge,
    center,
}: {
    edge: GraphEdge;
    center: GraphNode;
}) {
    const properties =
        edge.properties || {};

    return (
        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.025] p-5">

            <div className="mb-4 flex items-center justify-between">

                <div className="flex items-center gap-2">

                    <ArrowRight
                        size={15}
                        className="text-cyan-400"
                    />

                    <span className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                        Relationship
                    </span>

                </div>

                <ExternalLink
                    size={13}
                    className="text-white/20"
                />

            </div>

            <div className="mb-4 rounded-lg border border-white/10 bg-[#080b12] p-3">

                <div className="text-sm font-semibold text-white">
                    {edge.relationship}
                </div>

                <div className="mt-1 text-[10px] text-white/30">
                    {center.label}
                    {" → "}
                    {edge.target === center.id
                        ? edge.source
                        : edge.target}
                </div>

            </div>

            <div className="mb-2 text-[10px] uppercase tracking-wider text-white/25">
                Relationship Properties
            </div>

            {Object.keys(properties).length ? (
                <div className="space-y-2">

                    {Object.entries(
                        properties
                    ).map(([key, value]) => (

                        <div
                            key={key}
                            className="rounded-lg border border-white/5 bg-white/[0.02] p-2"
                        >

                            <div className="text-[9px] uppercase tracking-wider text-white/25">
                                {key}
                            </div>

                            <div className="mt-1 break-all text-[11px] text-white/60">
                                {String(value)}
                            </div>

                        </div>

                    ))}

                </div>
            ) : (
                <p className="text-xs text-white/30">
                    No additional relationship properties
                    available.
                </p>
            )}

        </div>
    );
}


// ============================================================
// SMALL STAT
// ============================================================

function SmallStat({
    title,
    value,
}: {
    title: string;
    value: string;
}) {
    return (
        <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">

            <div className="text-[9px] uppercase tracking-wider text-white/25">
                {title}
            </div>

            <div className="mt-1 truncate text-xs font-medium text-white/70">
                {value}
            </div>

        </div>
    );
}