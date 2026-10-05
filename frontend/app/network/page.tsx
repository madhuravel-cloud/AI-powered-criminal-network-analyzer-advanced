"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Network as NetworkIcon,
    RefreshCw,
    Search,
    X,
} from "lucide-react";

import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    Handle,
    Position,
    type Node,
    type Edge,
    type NodeProps,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";


const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

const CASE_ID = "case:FIR-101-2025";


type GraphNode = {
    id: string;
    type: string;
    label: string;
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
    network: {
        case_id: string;
        focused_entity?: string;
        nodes: GraphNode[];
        edges: GraphEdge[];
    };
};


const typeStyles: Record<string, string> = {
    Case: "border-red-400 bg-red-500/20",
    Person: "border-cyan-400 bg-cyan-500/20",
    Phone: "border-blue-400 bg-blue-500/20",
    Vehicle: "border-yellow-400 bg-yellow-500/20",
    Location: "border-green-400 bg-green-500/20",
    Account: "border-purple-400 bg-purple-500/20",
    Organization: "border-orange-400 bg-orange-500/20",
    CourtCase: "border-pink-400 bg-pink-500/20",
    Evidence: "border-slate-400 bg-slate-500/20",
};


function GraphNodeCard({
    data,
}: NodeProps) {
    const nodeType = String(data.type || "Unknown");

    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
                className="!bg-cyan-400"
            />

            <div
                className={`
                    min-w-[150px]
                    max-w-[190px]
                    rounded-xl
                    border
                    px-4
                    py-3
                    shadow-2xl
                    backdrop-blur-xl
                    ${typeStyles[nodeType] || "border-white/20 bg-white/10"}
                `}
            >
                <div className="mb-1 text-[10px] font-bold uppercase tracking-[0.18em] text-white/40">
                    {nodeType}
                </div>

                <div className="truncate text-sm font-semibold text-white">
                    {String(data.label)}
                </div>

                <div className="mt-1 truncate text-[10px] text-white/40">
                    {String(data.id)}
                </div>
            </div>

            <Handle
                type="source"
                position={Position.Bottom}
                className="!bg-cyan-400"
            />
        </>
    );
}


const nodeTypes = {
    graphNode: GraphNodeCard,
};


function convertNodes(
    nodes: GraphNode[],
): Node[] {
    const count = nodes.length;

    return nodes.map((node, index) => {
        const angle =
            (index / Math.max(count, 1)) *
            Math.PI *
            2;

        const radius =
            count > 30
                ? 550
                : 430;

        return {
            id: node.id,
            type: "graphNode",
            position: {
                x:
                    Math.cos(angle) *
                    radius +
                    650,
                y:
                    Math.sin(angle) *
                    radius +
                    400,
            },
            data: {
                id: node.id,
                label: node.label,
                type: node.type,
            },
        };
    });
}


function convertEdges(
    edges: GraphEdge[],
): Edge[] {
    return edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.relationship,
        animated: false,
        style: {
            strokeWidth: 1.5,
        },
        labelStyle: {
            fill: "#94a3b8",
            fontSize: 9,
        },
        labelBgStyle: {
            fill: "#080b12",
            fillOpacity: 0.85,
        },
    }));
}


export default function NetworkPage() {
    const [graph, setGraph] =
        useState<NetworkResponse["network"] | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    const [selectedNode, setSelectedNode] =
        useState<GraphNode | null>(null);

    const [search, setSearch] =
        useState("");

    const [subgraphLoading, setSubgraphLoading] =
        useState(false);

    const [history, setHistory] =
        useState<GraphNode[]>([]);


    async function loadGraph() {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(
                `${API_BASE_URL}/network?case_id=${encodeURIComponent(
                    CASE_ID,
                )}`,
                {
                    cache: "no-store",
                },
            );

            if (!response.ok) {
                throw new Error(
                    await response.text(),
                );
            }

            const data: NetworkResponse =
                await response.json();

            setGraph(data.network);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load network",
            );
        } finally {
            setLoading(false);
        }
    }


    async function selectNode(
        node: GraphNode,
    ) {
        try {
            setSelectedNode(node);
            setSubgraphLoading(true);
            setError(null);

            setHistory((previous) => [
                ...previous,
                node,
            ]);

            const response = await fetch(
                `${API_BASE_URL}/network/entity/${encodeURIComponent(
                    node.id,
                )}?case_id=${encodeURIComponent(
                    CASE_ID,
                )}`,
                {
                    cache: "no-store",
                },
            );

            if (!response.ok) {
                const text =
                    await response.text();

                throw new Error(
                    `Entity request failed (${response.status}): ${text}`,
                );
            }

            const data: NetworkResponse =
                await response.json();

            setGraph(data.network);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load subgraph",
            );
        } finally {
            setSubgraphLoading(false);
        }
    }


    function resetGraph() {
        setSelectedNode(null);
        setHistory([]);
        loadGraph();
    }


    useEffect(() => {
        loadGraph();
    }, []);


    const filteredNodes = useMemo(() => {
        if (!graph) {
            return [];
        }

        if (!search.trim()) {
            return graph.nodes;
        }

        const value =
            search.toLowerCase();

        return graph.nodes.filter(
            (node) =>
                node.label
                    .toLowerCase()
                    .includes(value) ||
                node.id
                    .toLowerCase()
                    .includes(value) ||
                node.type
                    .toLowerCase()
                    .includes(value),
        );
    }, [graph, search]);


    const flowNodes =
        useMemo(
            () =>
                convertNodes(
                    filteredNodes,
                ),
            [filteredNodes],
        );


    const visibleIds =
        new Set(
            filteredNodes.map(
                (node) => node.id,
            ),
        );


    const flowEdges =
        useMemo(
            () =>
                convertEdges(
                    graph?.edges.filter(
                        (edge) =>
                            visibleIds.has(
                                edge.source,
                            ) &&
                            visibleIds.has(
                                edge.target,
                            ),
                    ) || [],
                ),
            [graph, filteredNodes],
        );


    return (
        <div className="min-h-screen bg-[#05070b] text-white">

            <div className="border-b border-white/10 bg-[#080b12]/95 px-8 py-6">

                <div className="flex items-center justify-between">

                    <div>
                        <div className="flex items-center gap-3">
                            <NetworkIcon
                                size={22}
                                className="text-cyan-400"
                            />

                            <h1 className="text-2xl font-bold">
                                Investigation Network
                            </h1>
                        </div>

                        <p className="mt-1 text-sm text-white/40">
                            Backend-powered temporal evidence graph
                        </p>
                    </div>

                    <div className="flex items-center gap-3">

                        <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">

                            <Search
                                size={15}
                                className="text-white/30"
                            />

                            <input
                                value={search}
                                onChange={(event) =>
                                    setSearch(
                                        event.target.value,
                                    )
                                }
                                placeholder="Search entity..."
                                className="w-48 bg-transparent text-sm outline-none placeholder:text-white/20"
                            />

                            {search && (
                                <button
                                    onClick={() =>
                                        setSearch("")
                                    }
                                >
                                    <X
                                        size={14}
                                        className="text-white/30"
                                    />
                                </button>
                            )}

                        </div>

                        <button
                            onClick={resetGraph}
                            className="rounded-xl border border-white/10 bg-white/[0.03] p-3 transition hover:bg-white/[0.08]"
                        >
                            <RefreshCw
                                size={17}
                            />
                        </button>

                    </div>
                </div>


                <div className="mt-5 flex items-center gap-3 text-xs">

                    <span className="rounded-lg bg-cyan-500/10 px-3 py-1.5 text-cyan-400">
                        FIR-101-2025
                    </span>

                    {selectedNode && (
                        <>
                            <span className="text-white/20">
                                /
                            </span>

                            <span className="rounded-lg bg-white/[0.05] px-3 py-1.5 text-white/60">
                                {selectedNode.label}
                            </span>
                        </>
                    )}

                    {subgraphLoading && (
                        <span className="text-cyan-400">
                            Loading subgraph...
                        </span>
                    )}

                </div>

            </div>


            {error && (
                <div className="mx-8 mt-5 rounded-xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-300">
                    {error}
                </div>
            )}


            <div className="grid grid-cols-[1fr_300px] gap-0">

                <div
                    className="relative h-[calc(100vh-150px)]"
                    style={{
                        background:
                            "radial-gradient(circle at center, rgba(8,145,178,0.08), transparent 45%)",
                    }}
                >

                    {loading ? (
                        <div className="flex h-full items-center justify-center">
                            <div className="text-sm text-white/40">
                                Loading investigation graph...
                            </div>
                        </div>
                    ) : (
                        <ReactFlow
                            nodes={flowNodes}
                            edges={flowEdges}
                            nodeTypes={nodeTypes}
                            fitView
                            fitViewOptions={{
                                padding: 0.25,
                            }}
                            onNodeClick={(
                                _event,
                                node,
                            ) => {
                                const sourceNode =
                                    graph?.nodes.find(
                                        (item) =>
                                            item.id ===
                                            node.id,
                                    );

                                if (
                                    sourceNode
                                ) {
                                    selectNode(
                                        sourceNode,
                                    );
                                }
                            }}
                        >
                            <Background
                                gap={24}
                                size={1}
                            />

                            <Controls />

                            <MiniMap
                                nodeColor={(node) => {
                                    const type =
                                        String(
                                            node.data
                                                ?.type ||
                                            "",
                                        );

                                    if (
                                        type ===
                                        "Person"
                                    ) {
                                        return "#22d3ee";
                                    }

                                    if (
                                        type ===
                                        "Case"
                                    ) {
                                        return "#ef4444";
                                    }

                                    if (
                                        type ===
                                        "Evidence"
                                    ) {
                                        return "#64748b";
                                    }

                                    return "#8b5cf6";
                                }}
                            />
                        </ReactFlow>
                    )}

                </div>


                <aside className="border-l border-white/10 bg-[#080b12]">

                    <div className="border-b border-white/10 p-5">

                        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-white/30">
                            Network Statistics
                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-3">

                            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                                <div className="text-2xl font-bold">
                                    {graph?.nodes.length || 0}
                                </div>

                                <div className="mt-1 text-xs text-white/30">
                                    Entities
                                </div>
                            </div>

                            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                                <div className="text-2xl font-bold">
                                    {graph?.edges.length || 0}
                                </div>

                                <div className="mt-1 text-xs text-white/30">
                                    Connections
                                </div>
                            </div>

                        </div>

                    </div>


                    <div className="border-b border-white/10 p-5">

                        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-white/30">
                            Selected Entity
                        </div>

                        {selectedNode ? (
                            <div className="mt-4">

                                <div
                                    className={`
                                        inline-flex
                                        rounded-lg
                                        border
                                        px-3
                                        py-1
                                        text-[10px]
                                        font-bold
                                        uppercase
                                        tracking-wider
                                        ${typeStyles[
                                        selectedNode.type
                                        ] ||
                                        "border-white/20"
                                        }
                                    `}
                                >
                                    {selectedNode.type}
                                </div>

                                <div className="mt-3 text-lg font-semibold">
                                    {selectedNode.label}
                                </div>

                                <div className="mt-1 break-all text-xs text-white/30">
                                    {selectedNode.id}
                                </div>

                                <button
                                    onClick={
                                        resetGraph
                                    }
                                    className="mt-5 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white/60 transition hover:bg-white/[0.08] hover:text-white"
                                >
                                    Back to Investigation Graph
                                </button>

                            </div>
                        ) : (
                            <div className="mt-4 text-sm leading-6 text-white/30">
                                Select any entity in the graph to load its backend-generated subgraph.
                            </div>
                        )}

                    </div>


                    <div className="p-5">

                        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-white/30">
                            Entity Types
                        </div>

                        <div className="mt-4 space-y-2">

                            {[
                                "Person",
                                "Phone",
                                "Vehicle",
                                "Location",
                                "Account",
                                "Evidence",
                                "CourtCase",
                            ].map(
                                (type) => {
                                    const count =
                                        graph?.nodes.filter(
                                            (node) =>
                                                node.type ===
                                                type,
                                        ).length || 0;

                                    return (
                                        <div
                                            key={type}
                                            className="flex items-center justify-between rounded-lg bg-white/[0.025] px-3 py-2"
                                        >
                                            <span className="text-xs text-white/50">
                                                {type}
                                            </span>

                                            <span className="text-xs font-semibold text-white/70">
                                                {count}
                                            </span>
                                        </div>
                                    );
                                },
                            )}

                        </div>

                    </div>

                </aside>

            </div>

        </div>
    );
}