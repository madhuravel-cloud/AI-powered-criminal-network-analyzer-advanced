"use client";

import { useEffect, useMemo, useState } from "react";
import {
    ArrowLeft,
    Car,
    ChevronRight,
    CreditCard,
    Link2,
    MapPin,
    Network,
    Phone,
    Search,
    User,
    Building2,
    X,
} from "lucide-react";

import {
    getCaseEntities,
    getEntityGraph,
    type NetworkNode as ApiNetworkNode,
    type NetworkEdge as ApiNetworkEdge,
} from "../../lib/api";

import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    Handle,
    Position,
    MarkerType,
    type Node,
    type Edge,
    type NodeProps,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";


/* ============================================================
   TYPES
============================================================ */

type Entity = {
    id: string;
    label: string;
    type: string;
    properties?: Record<string, unknown>;
};

type GraphNode = {
    id: string;
    label: string;
    type: string;
    properties?: Record<string, unknown>;
};

type SelectedRelationship = {
    edge: ApiNetworkEdge;
    source?: GraphNode;
    target?: GraphNode;
};


/* ============================================================
   API CONVERSION
============================================================ */

function convertApiNode(
    node: ApiNetworkNode
): GraphNode {
    return {
        id: String(node.id),

        label:
            node.name ||
            node.canonical_id ||
            String(node.id),

        type:
            node.node_type ||
            "Entity",

        properties:
            node.properties,
    };
}


function convertApiEntity(
    node: ApiNetworkNode
): Entity {
    return {
        id: String(node.id),

        label:
            node.name ||
            node.canonical_id ||
            String(node.id),

        type:
            node.node_type ||
            "Entity",

        properties:
            node.properties,
    };
}


/* ============================================================
   ENTITY ICON
============================================================ */

function EntityIcon({
    type,
    size = 18,
}: {
    type: string;
    size?: number;
}) {
    const normalized =
        type.toLowerCase();

    if (normalized === "person") {
        return <User size={size} />;
    }

    if (normalized === "phone") {
        return <Phone size={size} />;
    }

    if (normalized === "vehicle") {
        return <Car size={size} />;
    }

    if (normalized === "location") {
        return <MapPin size={size} />;
    }

    if (normalized === "account") {
        return <CreditCard size={size} />;
    }

    if (
        normalized ===
        "organization"
    ) {
        return (
            <Building2
                size={size}
            />
        );
    }

    return <Network size={size} />;
}


/* ============================================================
   ENTITY STYLE
============================================================ */

function getEntityStyle(
    type: string
) {
    const normalized =
        type.toLowerCase();

    if (normalized === "person") {
        return {
            border:
                "border-cyan-400/40",
            bg:
                "bg-cyan-400/[0.08]",
            icon:
                "text-cyan-300",
        };
    }

    if (normalized === "phone") {
        return {
            border:
                "border-violet-400/40",
            bg:
                "bg-violet-400/[0.08]",
            icon:
                "text-violet-300",
        };
    }

    if (normalized === "vehicle") {
        return {
            border:
                "border-amber-400/40",
            bg:
                "bg-amber-400/[0.08]",
            icon:
                "text-amber-300",
        };
    }

    if (normalized === "location") {
        return {
            border:
                "border-emerald-400/40",
            bg:
                "bg-emerald-400/[0.08]",
            icon:
                "text-emerald-300",
        };
    }

    if (normalized === "account") {
        return {
            border:
                "border-pink-400/40",
            bg:
                "bg-pink-400/[0.08]",
            icon:
                "text-pink-300",
        };
    }

    if (
        normalized ===
        "organization"
    ) {
        return {
            border:
                "border-orange-400/40",
            bg:
                "bg-orange-400/[0.08]",
            icon:
                "text-orange-300",
        };
    }

    return {
        border:
            "border-white/20",
        bg:
            "bg-white/[0.05]",
        icon:
            "text-white/60",
    };
}


/* ============================================================
   GRAPH NODE
============================================================ */

function GraphEntityNode({
    data,
}: NodeProps) {

    const nodeData =
        data as {
            label: string;
            type: string;
        };

    const style =
        getEntityStyle(
            nodeData.type
        );

    return (
        <div
            className={`
                relative
                min-w-[170px]
                rounded-2xl
                border
                ${style.border}
                ${style.bg}
                px-4
                py-3
                shadow-2xl
                backdrop-blur-xl
            `}
        >

            <Handle
                type="target"
                position={
                    Position.Top
                }
                className="
                    !h-2
                    !w-2
                    !border-0
                    !bg-cyan-400
                "
            />

            <div className="flex items-center gap-3">

                <div
                    className={`
                        flex
                        h-9
                        w-9
                        shrink-0
                        items-center
                        justify-center
                        rounded-xl
                        bg-black/30
                        ${style.icon}
                    `}
                >
                    <EntityIcon
                        type={
                            nodeData.type
                        }
                        size={18}
                    />
                </div>

                <div className="min-w-0">

                    <p className="truncate text-sm font-semibold text-white">
                        {
                            nodeData.label
                        }
                    </p>

                    <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-white/40">
                        {
                            nodeData.type
                        }
                    </p>

                </div>

            </div>

            <Handle
                type="source"
                position={
                    Position.Bottom
                }
                className="
                    !h-2
                    !w-2
                    !border-0
                    !bg-cyan-400
                "
            />

        </div>
    );
}


const nodeTypes = {
    entity:
        GraphEntityNode,
};


/* ============================================================
   RELATIONSHIP FORMAT
============================================================ */

function formatRelationship(
    relationship: string
) {
    if (!relationship) {
        return "RELATED";
    }

    return relationship
        .replaceAll(
            "_",
            " "
        )
        .toLowerCase()
        .replace(
            /\b\w/g,
            (char) =>
                char.toUpperCase()
        );
}


/* ============================================================
   GRAPH BUILDER
============================================================ */

function buildGraph(
    apiNodes: GraphNode[],
    apiEdges: ApiNetworkEdge[],
    selectedId: string
) {

    const nodes: Node[] = [];
    const edges: Edge[] = [];

    const seenNodes =
        new Set<string>();

    const seenEdges =
        new Set<string>();


    const selectedNode =
        apiNodes.find(
            (node) =>
                String(node.id) ===
                String(selectedId)
        );


    const otherNodes =
        apiNodes.filter(
            (node) =>
                String(node.id) !==
                String(selectedId)
        );


    /* CENTER NODE */

    if (selectedNode) {

        nodes.push({
            id: String(
                selectedNode.id
            ),

            type: "entity",

            position: {
                x: 450,
                y: 250,
            },

            data: {
                label:
                    selectedNode.label,

                type:
                    selectedNode.type,
            },
        });

        seenNodes.add(
            String(
                selectedNode.id
            )
        );
    }


    /* OTHER NODES */

    otherNodes.forEach(
        (node, index) => {

            const angle =
                (
                    index /
                    Math.max(
                        otherNodes.length,
                        1
                    )
                ) *
                Math.PI *
                2;

            const radius =
                300;

            nodes.push({

                id: String(
                    node.id
                ),

                type: "entity",

                position: {
                    x:
                        450 +
                        Math.cos(angle) *
                        radius,

                    y:
                        250 +
                        Math.sin(angle) *
                        radius,
                },

                data: {
                    label:
                        node.label,

                    type:
                        node.type,
                },
            });

            seenNodes.add(
                String(
                    node.id
                )
            );
        }
    );


    /* EDGES */

    apiEdges.forEach(
        (edge, index) => {

            const source =
                String(
                    edge.source
                );

            const target =
                String(
                    edge.target
                );


            if (
                !seenNodes.has(
                    source
                ) ||
                !seenNodes.has(
                    target
                )
            ) {
                return;
            }


            const edgeId =
                String(
                    edge.id ||
                    `${source}-${target}-${index}`
                );


            if (
                seenEdges.has(
                    edgeId
                )
            ) {
                return;
            }


            seenEdges.add(
                edgeId
            );


            const relationship =
                edge.relationship_type ||
                "RELATED";


            const touchesSelected =
                source ===
                String(
                    selectedId
                ) ||
                target ===
                String(
                    selectedId
                );


            edges.push({

                id:
                    edgeId,

                source,

                target,

                type:
                    "smoothstep",

                animated:
                    touchesSelected,

                markerEnd: {
                    type:
                        MarkerType.ArrowClosed,

                    width: 18,

                    height: 18,
                },

                label:
                    formatRelationship(
                        relationship
                    ),

                labelStyle: {
                    fill:
                        "#cbd5e1",

                    fontSize:
                        10,

                    fontWeight:
                        600,
                },

                labelBgStyle: {
                    fill:
                        "#080b12",

                    fillOpacity:
                        0.95,
                },

                labelBgPadding: [
                    6,
                    4,
                ],

                labelBgBorderRadius:
                    6,

                style: {
                    stroke:
                        touchesSelected
                            ? "#22d3ee"
                            : "#64748b",

                    strokeWidth:
                        touchesSelected
                            ? 2.5
                            : 1.5,
                },

                data: {
                    relationship,
                },
            });
        }
    );


    return {
        nodes,
        edges,
    };
}


/* ============================================================
   MAIN
============================================================ */

export default function NetworkPage() {

    /*
     * IMPORTANT:
     * This is intentionally NOT string | null.
     *
     * Empty string means:
     * "No FIR has been selected yet."
     */
    const [
        selectedFir,
        setSelectedFir,
    ] =
        useState<string>("");


    const [
        entities,
        setEntities,
    ] =
        useState<Entity[]>(
            []
        );


    const [
        search,
        setSearch,
    ] =
        useState("");


    const [
        loading,
        setLoading,
    ] =
        useState(true);


    const [
        graphLoading,
        setGraphLoading,
    ] =
        useState(false);


    const [
        error,
        setError,
    ] =
        useState<string>("");


    const [
        graphVisible,
        setGraphVisible,
    ] =
        useState(false);


    const [
        selectedEntity,
        setSelectedEntity,
    ] =
        useState<
            GraphNode | null
        >(null);


    const [
        graphNodes,
        setGraphNodes,
    ] =
        useState<
            GraphNode[]
        >([]);


    const [
        graphEdges,
        setGraphEdges,
    ] =
        useState<
            ApiNetworkEdge[]
        >([]);


    const [
        selectedRelationship,
        setSelectedRelationship,
    ] =
        useState<
            SelectedRelationship | null
        >(null);


    /* ========================================================
       READ FIR
    ======================================================== */

    useEffect(() => {

        const storedFir =
            window.localStorage.getItem(
                "criminal-network-selected-fir"
            );


        if (
            storedFir &&
            storedFir.trim()
        ) {

            setSelectedFir(
                storedFir
            );

        } else {

            setLoading(
                false
            );

            setError(
                "No FIR selected. Please select an FIR from the Dashboard."
            );
        }

    }, []);


    /* ========================================================
       LOAD ENTITIES
    ======================================================== */

    useEffect(() => {

        /*
         * selectedFir is now ALWAYS a string.
         */

        if (!selectedFir) {
            return;
        }


        async function loadEntities() {

            try {

                setLoading(
                    true
                );

                setError(
                    ""
                );


                const response =
                    await getCaseEntities(
                        selectedFir
                    );


                const converted =
                    response.entities.map(
                        convertApiEntity
                    );


                setEntities(
                    converted
                );

            } catch (err) {

                console.error(
                    err
                );

                setError(
                    err instanceof Error
                        ? err.message
                        : "Failed to load FIR entities."
                );

            } finally {

                setLoading(
                    false
                );

            }
        }


        loadEntities();

    }, [
        selectedFir,
    ]);


    /* ========================================================
       FILTER
    ======================================================== */

    const filteredEntities =
        useMemo(() => {

            const query =
                search
                    .trim()
                    .toLowerCase();


            if (!query) {
                return entities;
            }


            return entities.filter(
                (entity) =>
                    entity.label
                        .toLowerCase()
                        .includes(
                            query
                        ) ||
                    entity.type
                        .toLowerCase()
                        .includes(
                            query
                        )
            );

        }, [
            entities,
            search,
        ]);


    /* ========================================================
       OPEN GRAPH
    ======================================================== */

    async function openEntityGraph(
        entity: Entity
    ) {

        /*
         * No nullable FIR anymore.
         */

        if (!selectedFir) {

            setError(
                "No FIR selected. Please select an FIR from the Dashboard."
            );

            return;
        }


        try {

            setGraphLoading(
                true
            );

            setError(
                ""
            );

            setSelectedRelationship(
                null
            );


            const response =
                await getEntityGraph(
                    selectedFir,
                    entity.id
                );


            const convertedNodes =
                response.nodes.map(
                    convertApiNode
                );


            const selected =
                convertApiNode(
                    response.selected_entity
                );


            setSelectedEntity(
                selected
            );


            setGraphNodes(
                convertedNodes
            );


            setGraphEdges(
                response.edges
            );


            setGraphVisible(
                true
            );

        } catch (err) {

            console.error(
                err
            );

            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load entity graph."
            );

        } finally {

            setGraphLoading(
                false
            );

        }
    }


    /* ========================================================
       GRAPH
    ======================================================== */

    const graph =
        useMemo(() => {

            if (
                !graphVisible ||
                !selectedEntity
            ) {

                return {
                    nodes: [],
                    edges: [],
                };
            }


            return buildGraph(
                graphNodes,
                graphEdges,
                selectedEntity.id
            );

        }, [
            graphVisible,
            selectedEntity,
            graphNodes,
            graphEdges,
        ]);


    /* ========================================================
       EDGE CLICK
    ======================================================== */

    function handleEdgeClick(
        _event: React.MouseEvent,
        edge: Edge
    ) {

        const apiEdge =
            graphEdges.find(
                (item) =>
                    String(
                        item.id
                    ) ===
                    String(
                        edge.id
                    )
            );


        if (!apiEdge) {
            return;
        }


        const source =
            graphNodes.find(
                (node) =>
                    String(
                        node.id
                    ) ===
                    String(
                        apiEdge.source
                    )
            );


        const target =
            graphNodes.find(
                (node) =>
                    String(
                        node.id
                    ) ===
                    String(
                        apiEdge.target
                    )
            );


        setSelectedRelationship({
            edge:
                apiEdge,

            source,

            target,
        });

    }


    /* ========================================================
       BACK
    ======================================================== */

    function showAllEntities() {

        setGraphVisible(
            false
        );

        setSelectedEntity(
            null
        );

        setGraphNodes(
            []
        );

        setGraphEdges(
            []
        );

        setSelectedRelationship(
            null
        );

    }


    /* ========================================================
       RENDER
    ======================================================== */

    return (

        <div className="min-h-screen bg-[#05070b]">

            {/* ==================================================
                HEADER
            ================================================== */}

            <header className="border-b border-white/10 bg-[#080b12]/80 px-8 py-6 backdrop-blur-xl">

                <div className="flex items-center justify-between">

                    <div>

                        <div className="flex items-center gap-3">

                            <Network
                                size={22}
                                className="text-cyan-400"
                            />

                            <h1 className="text-2xl font-bold text-white">
                                Network Analysis
                            </h1>

                        </div>

                        <p className="mt-1 text-sm text-white/40">
                            FIR-scoped temporal multilayer entity network
                        </p>

                    </div>


                    {selectedFir && (

                        <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.05] px-5 py-3">

                            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400/70">
                                Selected FIR
                            </p>

                            <p className="mt-1 font-mono text-sm text-cyan-300">
                                {
                                    selectedFir
                                }
                            </p>

                        </div>

                    )}

                </div>

            </header>


            {/* ==================================================
                ERROR
            ================================================== */}

            {error && (

                <div className="mx-8 mt-6 rounded-xl border border-red-400/20 bg-red-400/[0.05] px-5 py-4 text-sm text-red-300">

                    {
                        error
                    }

                </div>

            )}


            {/* ==================================================
                ENTITY VIEW
            ================================================== */}

            {!graphVisible && (

                <section className="p-8">

                    <div className="mb-6 flex items-center justify-between">

                        <div>

                            <h2 className="text-lg font-semibold text-white">
                                FIR Entities
                            </h2>

                            <p className="mt-1 text-sm text-white/40">
                                Select an entity to inspect its connected network.
                            </p>

                        </div>


                        <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">

                            <Search
                                size={16}
                                className="text-white/30"
                            />

                            <input
                                value={
                                    search
                                }
                                onChange={(
                                    e
                                ) =>
                                    setSearch(
                                        e.target.value
                                    )
                                }
                                placeholder="Search entities..."
                                className="w-56 bg-transparent text-sm text-white outline-none placeholder:text-white/25"
                            />

                        </div>

                    </div>


                    {loading ? (

                        <div className="flex min-h-[400px] items-center justify-center">

                            <div className="text-sm text-white/40">
                                Loading FIR entities...
                            </div>

                        </div>

                    ) : filteredEntities.length === 0 ? (

                        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-12 text-center">

                            <Network
                                size={36}
                                className="mx-auto text-white/20"
                            />

                            <p className="mt-4 text-white/50">
                                No entities found for this FIR.
                            </p>

                        </div>

                    ) : (

                        <div className="grid grid-cols-2 gap-5 xl:grid-cols-4">

                            {filteredEntities.map(
                                (
                                    entity
                                ) => {

                                    const style =
                                        getEntityStyle(
                                            entity.type
                                        );


                                    return (

                                        <button
                                            key={
                                                entity.id
                                            }
                                            onClick={() =>
                                                openEntityGraph(
                                                    entity
                                                )
                                            }
                                            className={`
                                                group
                                                rounded-2xl
                                                border
                                                ${style.border}
                                                ${style.bg}
                                                p-5
                                                text-left
                                                transition-all
                                                duration-200
                                                hover:-translate-y-1
                                                hover:bg-white/[0.07]
                                                hover:shadow-2xl
                                            `}
                                        >

                                            <div className="flex items-center justify-between">

                                                <div
                                                    className={`
                                                        flex
                                                        h-11
                                                        w-11
                                                        items-center
                                                        justify-center
                                                        rounded-xl
                                                        bg-black/30
                                                        ${style.icon}
                                                    `}
                                                >
                                                    <EntityIcon
                                                        type={
                                                            entity.type
                                                        }
                                                        size={
                                                            20
                                                        }
                                                    />
                                                </div>

                                                <ChevronRight
                                                    size={
                                                        18
                                                    }
                                                    className="text-white/20 transition-transform group-hover:translate-x-1 group-hover:text-cyan-400"
                                                />

                                            </div>


                                            <div className="mt-5">

                                                <p className="truncate text-base font-semibold text-white">
                                                    {
                                                        entity.label
                                                    }
                                                </p>

                                                <p className="mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white/35">
                                                    {
                                                        entity.type
                                                    }
                                                </p>

                                            </div>

                                        </button>

                                    );

                                }
                            )}

                        </div>

                    )}

                </section>

            )}


            {/* ==================================================
                GRAPH VIEW
            ================================================== */}

            {graphVisible && (

                <section className="relative h-[calc(100vh-105px)]">

                    {/* GRAPH TOOLBAR */}

                    <div className="absolute left-6 top-6 z-20 flex items-center gap-3">

                        <button
                            onClick={
                                showAllEntities
                            }
                            className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#080b12]/90 px-4 py-2.5 text-sm font-medium text-white/70 backdrop-blur-xl transition hover:bg-white/[0.08] hover:text-white"
                        >

                            <ArrowLeft
                                size={
                                    16
                                }
                            />

                            All FIR Entities

                        </button>


                        {selectedEntity && (

                            <div className="flex items-center gap-3 rounded-xl border border-cyan-400/20 bg-[#080b12]/90 px-4 py-2.5 backdrop-blur-xl">

                                <div className="text-cyan-400">

                                    <EntityIcon
                                        type={
                                            selectedEntity.type
                                        }
                                        size={
                                            17
                                        }
                                    />

                                </div>

                                <div>

                                    <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-white/35">
                                        Focus Entity
                                    </p>

                                    <p className="text-sm font-semibold text-white">
                                        {
                                            selectedEntity.label
                                        }
                                    </p>

                                </div>

                            </div>

                        )}

                    </div>


                    {/* RELATIONSHIP PANEL */}

                    {selectedRelationship && (

                        <div className="absolute right-6 top-6 z-30 w-80 rounded-2xl border border-cyan-400/20 bg-[#080b12]/95 p-5 shadow-2xl backdrop-blur-xl">

                            <div className="flex items-start justify-between">

                                <div>

                                    <div className="flex items-center gap-2">

                                        <Link2
                                            size={
                                                16
                                            }
                                            className="text-cyan-400"
                                        />

                                        <p className="text-sm font-semibold text-white">
                                            Relationship Details
                                        </p>

                                    </div>

                                    <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-white/30">
                                        Network connection
                                    </p>

                                </div>


                                <button
                                    onClick={() =>
                                        setSelectedRelationship(
                                            null
                                        )
                                    }
                                    className="rounded-lg p-1.5 text-white/30 transition hover:bg-white/10 hover:text-white"
                                >
                                    <X
                                        size={
                                            16
                                        }
                                    />
                                </button>

                            </div>


                            {/* TYPE */}

                            <div className="mt-5 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04] p-4">

                                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400/60">
                                    Relationship
                                </p>

                                <p className="mt-1 text-lg font-semibold text-cyan-300">
                                    {
                                        formatRelationship(
                                            selectedRelationship
                                                .edge
                                                .relationship_type
                                        )
                                    }
                                </p>

                            </div>


                            {/* SOURCE / TARGET */}

                            <div className="mt-5 space-y-4">

                                <div>

                                    <p className="text-[10px] uppercase tracking-[0.15em] text-white/30">
                                        Source
                                    </p>

                                    <div className="mt-1 flex items-center gap-2">

                                        <EntityIcon
                                            type={
                                                selectedRelationship
                                                    .source
                                                    ?.type ||
                                                "Entity"
                                            }
                                            size={
                                                14
                                            }
                                        />

                                        <p className="text-sm font-medium text-white">
                                            {
                                                selectedRelationship
                                                    .source
                                                    ?.label ||
                                                selectedRelationship
                                                    .edge
                                                    .source
                                            }
                                        </p>

                                    </div>

                                </div>


                                <div>

                                    <p className="text-[10px] uppercase tracking-[0.15em] text-white/30">
                                        Target
                                    </p>

                                    <div className="mt-1 flex items-center gap-2">

                                        <EntityIcon
                                            type={
                                                selectedRelationship
                                                    .target
                                                    ?.type ||
                                                "Entity"
                                            }
                                            size={
                                                14
                                            }
                                        />

                                        <p className="text-sm font-medium text-white">
                                            {
                                                selectedRelationship
                                                    .target
                                                    ?.label ||
                                                selectedRelationship
                                                    .edge
                                                    .target
                                            }
                                        </p>

                                    </div>

                                </div>

                            </div>


                            {/* PROPERTIES */}

                            {selectedRelationship
                                .edge
                                .properties &&
                                Object.keys(
                                    selectedRelationship
                                        .edge
                                        .properties
                                ).length >
                                0 && (

                                    <div className="mt-5 border-t border-white/10 pt-4">

                                        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-white/30">
                                            Properties
                                        </p>

                                        <div className="mt-3 space-y-2">

                                            {Object.entries(
                                                selectedRelationship
                                                    .edge
                                                    .properties
                                            )
                                                .slice(
                                                    0,
                                                    6
                                                )
                                                .map(
                                                    ([
                                                        key,
                                                        value,
                                                    ]) => (

                                                        <div
                                                            key={
                                                                key
                                                            }
                                                            className="flex items-start justify-between gap-4"
                                                        >

                                                            <span className="text-xs text-white/35">
                                                                {
                                                                    key
                                                                }
                                                            </span>

                                                            <span className="max-w-[170px] truncate text-right text-xs text-white/70">
                                                                {String(
                                                                    value
                                                                )}
                                                            </span>

                                                        </div>

                                                    )
                                                )}

                                        </div>

                                    </div>

                                )}

                        </div>

                    )}


                    {/* GRAPH */}

                    {graphLoading ? (

                        <div className="flex h-full items-center justify-center">

                            <div className="rounded-xl border border-white/10 bg-[#080b12]/90 px-6 py-4 text-sm text-white/50 backdrop-blur-xl">
                                Building entity network...
                            </div>

                        </div>

                    ) : (

                        <ReactFlow
                            nodes={
                                graph.nodes
                            }
                            edges={
                                graph.edges
                            }
                            nodeTypes={
                                nodeTypes
                            }
                            fitView
                            fitViewOptions={{
                                padding:
                                    0.25,
                            }}
                            onEdgeClick={
                                handleEdgeClick
                            }
                            onPaneClick={() =>
                                setSelectedRelationship(
                                    null
                                )
                            }
                            proOptions={{
                                hideAttribution:
                                    true,
                            }}
                            defaultEdgeOptions={{
                                type:
                                    "smoothstep",
                            }}
                        >

                            <Background
                                gap={
                                    24
                                }
                                size={
                                    1
                                }
                                color={
                                    "#1e293b"
                                }
                            />

                            <Controls
                                className="
                                    !border-white/10
                                    !bg-[#080b12]
                                "
                            />

                            <MiniMap
                                nodeColor={
                                    "#22d3ee"
                                }
                                maskColor="rgba(5,7,11,0.75)"
                                className="
                                    !border-white/10
                                    !bg-[#080b12]
                                "
                            />

                        </ReactFlow>

                    )}

                </section>

            )}

        </div>
    );
}