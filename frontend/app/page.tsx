"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

import {
  Activity,
  Bell,
  BrainCircuit,
  Briefcase,
  Car,
  ChevronRight,
  Clock3,
  FileSearch,
  Fingerprint,
  FileText,
  MapPin,
  Network,
  Phone,
  Search,
  Shield,
  Users,
  Video,
  WalletCards,
} from "lucide-react";

import {
  analyzeInvestigation,
  type Candidate,
  type InvestigationAnalysis,
} from "@/lib/api";

const sources = [
  { name: "FIR", icon: FileText, count: 48 },
  { name: "CDR", icon: Phone, count: 71 },
  { name: "CCTV", icon: Video, count: 63 },
  { name: "Court", icon: Shield, count: 29 },
  { name: "Vehicle", icon: Car, count: 36 },
  { name: "Financial", icon: WalletCards, count: 31 },
  { name: "Location", icon: MapPin, count: 34 },
];

const activities = [
  {
    time: "10:42",
    title: "CDR evidence processed",
    description: "New communication relationship identified",
    icon: Phone,
  },
  {
    time: "10:31",
    title: "Entity resolved",
    description: "Person matched with existing graph entity",
    icon: Fingerprint,
  },
  {
    time: "10:18",
    title: "CCTV evidence linked",
    description: "Observation connected to FIR-101-2025",
    icon: Video,
  },
  {
    time: "09:56",
    title: "New relationship detected",
    description: "Cross-case connection discovered",
    icon: Network,
  },
];

function AnimatedBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-[#05080d]" />

      <motion.div
        animate={{
          opacity: [0.18, 0.28, 0.18],
          scale: [1, 1.08, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute left-[20%] top-[-20%] h-[600px] w-[600px] rounded-full bg-cyan-500/10 blur-[140px]"
      />

      <motion.div
        animate={{
          opacity: [0.08, 0.16, 0.08],
          scale: [1.05, 1, 1.05],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute right-[-10%] top-[30%] h-[500px] w-[500px] rounded-full bg-blue-500/10 blur-[140px]"
      />

      <div
        className="absolute inset-0 opacity-[0.08]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(148,163,184,0.25) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.25) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />
    </div>
  );
}

export default function Home() {
  const [analysis, setAnalysis] =
    useState<InvestigationAnalysis | null>(null);

  const [selectedPerson, setSelectedPerson] =
    useState<Candidate | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    async function loadAnalysis() {
      try {
        setLoading(true);
        setError(null);

        const response =
          await analyzeInvestigation("FIR-101-2025");

        setAnalysis(response.analysis);

        if (
          response.analysis.top_relevant_people.length > 0
        ) {
          setSelectedPerson(
            response.analysis.top_relevant_people[0]
          );
        }
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load investigation analysis"
        );
      } finally {
        setLoading(false);
      }
    }

    loadAnalysis();
  }, []);

  const candidates =
    analysis?.top_relevant_people ?? [];

  const selectedFeatures =
    selectedPerson?.features;

  const stats = [
    {
      label: "Candidates",
      value: analysis?.candidate_count?.toString() ?? "--",
      change: "Graph candidates",
      icon: Briefcase,
    },
    {
      label: "People",
      value:
        analysis?.seed_people.length?.toString() ?? "--",
      change: "Investigation seeds",
      icon: Users,
    },
    {
      label: "Evidence",
      value:
        selectedPerson?.evidence_ids.length?.toString() ??
        "--",
      change: "Linked evidence",
      icon: FileSearch,
    },
    {
      label: "Investigation Leads",
      value: candidates.length.toString(),
      change: "Top relevant people",
      icon: BrainCircuit,
    },
  ];

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05080d] text-slate-100">
        <AnimatedBackground />

        <div className="relative z-10 text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "linear",
            }}
            className="mx-auto h-10 w-10 rounded-full border-2 border-white/10 border-t-cyan-400"
          />

          <p className="mt-5 text-sm text-slate-400">
            Running investigation analysis...
          </p>

          <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-slate-600">
            Connecting to master graph
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05080d] text-slate-100">
        <AnimatedBackground />

        <div className="relative z-10 max-w-md rounded-2xl border border-red-400/10 bg-[#0a0f16]/90 p-7 text-center backdrop-blur-xl">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-red-400/20 bg-red-400/[0.06]">
            <Network className="h-5 w-5 text-red-400" />
          </div>

          <h2 className="mt-4 text-base font-semibold">
            Analysis unavailable
          </h2>

          <p className="mt-2 text-xs leading-6 text-slate-500">
            {error}
          </p>

          <p className="mt-4 text-[10px] uppercase tracking-[0.15em] text-slate-700">
            Check FastAPI and Neo4j services
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#05080d] text-slate-100">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen">

        {/* MAIN */}

        <section className="min-w-0 flex-1">

          {/* HEADER */}

          <header className="flex h-[78px] items-center justify-between border-b border-white/[0.06] bg-[#070b11]/60 px-5 backdrop-blur-xl md:px-8">

            <div>
              <p className="text-[10px] font-medium uppercase tracking-[0.25em] text-slate-600">
                Investigation Command Center
              </p>

              <h1 className="mt-1 text-lg font-semibold tracking-tight text-slate-100">
                Intelligence Overview
              </h1>
            </div>

            <div className="flex items-center gap-3">

              <button className="hidden rounded-xl border border-white/[0.07] bg-white/[0.02] p-2.5 text-slate-500 transition hover:border-cyan-400/20 hover:text-cyan-300 sm:block">
                <Search className="h-4 w-4" />
              </button>

              <button className="relative rounded-xl border border-white/[0.07] bg-white/[0.02] p-2.5 text-slate-500 transition hover:border-cyan-400/20 hover:text-cyan-300">
                <Bell className="h-4 w-4" />

                <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
              </button>

              <div className="hidden h-8 w-px bg-white/[0.07] sm:block" />

              <div className="flex items-center gap-3">

                <div className="hidden text-right sm:block">
                  <p className="text-xs font-medium text-slate-300">
                    Investigator
                  </p>

                  <p className="text-[10px] text-slate-600">
                    Intelligence Unit
                  </p>
                </div>

                <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.07]">
                  <Fingerprint className="h-4 w-4 text-cyan-300" />
                </div>

              </div>
            </div>
          </header>

          {/* CONTENT */}

          <div className="p-5 md:p-8">
            <div className="mx-auto max-w-[1600px]">

              {/* BREADCRUMB */}

              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 flex items-center gap-2 text-xs text-slate-600"
              >
                <span>Operations</span>

                <ChevronRight className="h-3 w-3" />

                <span className="text-cyan-400/80">
                  Overview
                </span>
              </motion.div>

              {/* STATS */}

              <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">

                {stats.map((stat, index) => {
                  const Icon = stat.icon;

                  return (
                    <motion.div
                      key={stat.label}
                      initial={{
                        opacity: 0,
                        y: 20,
                      }}
                      animate={{
                        opacity: 1,
                        y: 0,
                      }}
                      transition={{
                        delay: index * 0.08,
                        duration: 0.5,
                      }}
                      whileHover={{ y: -3 }}
                      className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0a0f16]/80 p-5 backdrop-blur-xl"
                    >

                      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-cyan-400/[0.04] blur-2xl transition duration-500 group-hover:bg-cyan-400/[0.1]" />

                      <div className="relative flex items-start justify-between">

                        <div>

                          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                            {stat.label}
                          </p>

                          <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="mt-3 text-3xl font-semibold tracking-tight text-slate-100"
                          >
                            {stat.value}
                          </motion.p>

                          <p className="mt-1 text-[11px] text-cyan-400/70">
                            {stat.change}
                          </p>

                        </div>

                        <div className="rounded-xl border border-white/[0.06] bg-white/[0.025] p-2.5 text-cyan-300/70">
                          <Icon className="h-4 w-4" />
                        </div>

                      </div>

                    </motion.div>
                  );
                })}

              </div>

              {/* ACTIVE INVESTIGATION */}

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.35 }}
                className="mt-5 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0a0f16]/80 backdrop-blur-xl"
              >

                <div className="flex flex-col justify-between gap-4 border-b border-white/[0.06] p-5 md:flex-row md:items-center md:px-6">

                  <div>

                    <div className="flex items-center gap-2">

                      <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />

                      <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                        Active Investigation
                      </span>

                    </div>

                    <h2 className="mt-2 text-xl font-semibold text-slate-100">
                      {analysis?.case_id.replace("case:", "") ??
                        "FIR-101-2025"}
                    </h2>

                    <p className="mt-1 text-xs text-slate-500">
                      Master Graph Investigation
                    </p>

                  </div>

                  <button className="flex items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-4 py-2.5 text-xs font-medium text-cyan-300 transition hover:border-cyan-400/40 hover:bg-cyan-400/[0.13]">
                    Analysis Ready
                    <ChevronRight className="h-3.5 w-3.5" />
                  </button>

                </div>

                <div className="grid grid-cols-2 divide-x divide-white/[0.05] md:grid-cols-4">

                  {[
                    [
                      "Seed People",
                      analysis?.seed_people.length.toString() ?? "--",
                    ],
                    [
                      "Candidates",
                      analysis?.candidate_count.toString() ?? "--",
                    ],
                    [
                      "Evidence",
                      selectedPerson?.evidence_ids.length.toString() ?? "--",
                    ],
                    [
                      "Connected Cases",
                      selectedPerson?.connected_cases.length.toString() ?? "--",
                    ],
                  ].map(([label, value]) => (
                    <div
                      key={label}
                      className="p-5 md:px-6"
                    >
                      <p className="text-[10px] uppercase tracking-[0.15em] text-slate-600">
                        {label}
                      </p>

                      <p className="mt-2 text-sm font-semibold text-slate-300">
                        {value}
                      </p>
                    </div>
                  ))}

                </div>
              </motion.div>

              {/* GRAPH + LEADS */}

              <div className="mt-5 grid gap-5 xl:grid-cols-[1.5fr_1fr]">

                {/* NETWORK */}

                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                  className="relative min-h-[430px] overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0a0f16]/80 backdrop-blur-xl"
                >

                  <div className="absolute inset-x-0 top-0 z-20 flex items-center justify-between border-b border-white/[0.06] p-5">

                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
                        Network Intelligence
                      </p>

                      <h3 className="mt-1 text-sm font-semibold text-slate-200">
                        Investigation Graph
                      </h3>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] text-slate-600">
                      <Activity className="h-3.5 w-3.5 text-cyan-400" />
                      Live graph
                    </div>

                  </div>

                  <div className="absolute inset-0 pt-[90px]">

                    <svg
                      viewBox="0 0 700 390"
                      className="h-full w-full opacity-90"
                    >

                      <defs>
                        <filter id="glow">
                          <feGaussianBlur
                            stdDeviation="5"
                            result="blur"
                          />

                          <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                          </feMerge>
                        </filter>
                      </defs>

                      <motion.g
                        animate={{
                          opacity: [
                            0.25,
                            0.6,
                            0.25,
                          ],
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      >

                        <line
                          x1="350"
                          y1="190"
                          x2="190"
                          y2="105"
                          stroke="rgba(34,211,238,0.3)"
                          strokeWidth="1"
                        />

                        <line
                          x1="350"
                          y1="190"
                          x2="525"
                          y2="110"
                          stroke="rgba(34,211,238,0.3)"
                          strokeWidth="1"
                        />

                        <line
                          x1="350"
                          y1="190"
                          x2="185"
                          y2="295"
                          stroke="rgba(34,211,238,0.3)"
                          strokeWidth="1"
                        />

                        <line
                          x1="350"
                          y1="190"
                          x2="535"
                          y2="295"
                          stroke="rgba(34,211,238,0.3)"
                          strokeWidth="1"
                        />

                        <line
                          x1="190"
                          y1="105"
                          x2="525"
                          y2="110"
                          stroke="rgba(59,130,246,0.18)"
                          strokeWidth="1"
                        />

                        <line
                          x1="185"
                          y1="295"
                          x2="535"
                          y2="295"
                          stroke="rgba(59,130,246,0.18)"
                          strokeWidth="1"
                        />

                      </motion.g>

                      {[
                        [
                          350,
                          190,
                          12,
                          selectedPerson?.name ?? "Ravi",
                          true,
                        ],
                        [190, 105, 7, "Kumar", false],
                        [525, 110, 7, "Joseph", false],
                        [185, 295, 7, "CDR", false],
                        [535, 295, 7, "CCTV", false],
                      ].map(
                        ([
                          cx,
                          cy,
                          r,
                          label,
                          primary,
                        ]) => (
                          <g key={String(label)}>

                            {primary && (
                              <motion.circle
                                cx={cx as number}
                                cy={cy as number}
                                r="25"
                                fill="rgba(34,211,238,0.05)"
                                animate={{
                                  r: [
                                    22,
                                    32,
                                    22,
                                  ],
                                  opacity: [
                                    0.3,
                                    0.05,
                                    0.3,
                                  ],
                                }}
                                transition={{
                                  duration: 2.5,
                                  repeat: Infinity,
                                }}
                              />
                            )}

                            <circle
                              cx={cx as number}
                              cy={cy as number}
                              r={r as number}
                              fill={
                                primary
                                  ? "rgba(34,211,238,0.9)"
                                  : "rgba(71,85,105,0.9)"
                              }
                              filter={
                                primary
                                  ? "url(#glow)"
                                  : undefined
                              }
                            />

                            <text
                              x={cx as number}
                              y={(cy as number) + 25}
                              textAnchor="middle"
                              fill={
                                primary
                                  ? "rgba(165,243,252,0.9)"
                                  : "rgba(148,163,184,0.6)"
                              }
                              fontSize="11"
                            >
                              {label as string}
                            </text>

                          </g>
                        )
                      )}

                    </svg>

                  </div>

                  <div className="absolute bottom-4 left-5 flex items-center gap-4 text-[9px] text-slate-600">

                    <span className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                      Person
                    </span>

                    <span className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-500" />
                      Related Entity
                    </span>

                  </div>

                </motion.div>

                {/* LEADS */}

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.55 }}
                  className="rounded-2xl border border-white/[0.07] bg-[#0a0f16]/80 p-5 backdrop-blur-xl"
                >

                  <div className="flex items-start justify-between">

                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
                        Analysis
                      </p>

                      <h3 className="mt-1 text-sm font-semibold text-slate-200">
                        Top Relevant People
                      </h3>
                    </div>

                    <BrainCircuit className="h-4 w-4 text-cyan-400/70" />

                  </div>

                  <div className="mt-5 space-y-3">

                    {candidates.map(
                      (lead, index) => (
                        <motion.button
                          key={lead.person_id}
                          initial={{
                            opacity: 0,
                            x: 15,
                          }}
                          animate={{
                            opacity: 1,
                            x: 0,
                          }}
                          transition={{
                            delay:
                              0.65 +
                              index * 0.08,
                          }}
                          whileHover={{ x: 4 }}
                          onClick={() =>
                            setSelectedPerson(
                              lead
                            )
                          }
                          className={`group w-full cursor-pointer rounded-xl border p-3 text-left transition ${selectedPerson?.person_id ===
                            lead.person_id
                            ? "border-cyan-400/20 bg-cyan-400/[0.05]"
                            : "border-white/[0.05] bg-white/[0.015] hover:border-cyan-400/10 hover:bg-cyan-400/[0.025]"
                            }`}
                        >

                          <div className="flex items-center gap-3">

                            <span className="font-mono text-[10px] text-slate-700">
                              {String(index + 1).padStart(
                                2,
                                "0"
                              )}
                            </span>

                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/[0.04] text-xs font-semibold text-slate-300">
                              {lead.name.charAt(0)}
                            </div>

                            <div className="min-w-0 flex-1">

                              <div className="flex items-center justify-between">

                                <span className="text-xs font-semibold text-slate-300">
                                  {lead.name}
                                </span>

                                <span className="text-xs font-semibold text-cyan-300">
                                  {lead.relevance_score.toFixed(
                                    1
                                  )}
                                </span>

                              </div>

                              <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/[0.05]">

                                <motion.div
                                  initial={{
                                    width: 0,
                                  }}
                                  animate={{
                                    width: `${Math.min(
                                      lead.relevance_score,
                                      100
                                    )}%`,
                                  }}
                                  transition={{
                                    delay:
                                      0.8 +
                                      index * 0.08,
                                    duration: 0.8,
                                    ease: "easeOut",
                                  }}
                                  className="h-full rounded-full bg-cyan-400/70"
                                />

                              </div>

                              <div className="mt-1.5 flex gap-3 text-[9px] text-slate-600">

                                <span>
                                  {
                                    lead.features
                                      .unique_connections
                                  }{" "}
                                  connections
                                </span>

                                <span>•</span>

                                <span>
                                  {
                                    lead.source_layers
                                      .length
                                  }{" "}
                                  sources
                                </span>

                              </div>

                            </div>

                          </div>

                        </motion.button>
                      )
                    )}

                  </div>

                  <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-white/[0.06] py-2.5 text-[10px] font-medium uppercase tracking-wider text-slate-500 transition hover:border-cyan-400/15 hover:text-cyan-300">
                    View Full Analysis
                    <ChevronRight className="h-3 w-3" />
                  </button>

                </motion.div>

              </div>

              {/* SELECTED PERSON DETAILS */}

              {selectedPerson && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 15,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  className="mt-5 rounded-2xl border border-cyan-400/10 bg-[#0a0f16]/80 p-6 backdrop-blur-xl"
                >

                  <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">

                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400/70">
                        Selected Candidate
                      </p>

                      <h3 className="mt-1 text-xl font-semibold text-slate-100">
                        {selectedPerson.name}
                      </h3>

                      <p className="mt-1 font-mono text-[10px] text-slate-600">
                        {selectedPerson.person_id}
                      </p>
                    </div>

                    <div className="text-left md:text-right">
                      <p className="text-3xl font-semibold text-cyan-300">
                        {selectedPerson.relevance_score.toFixed(
                          2
                        )}
                      </p>

                      <p className="text-[9px] uppercase tracking-[0.15em] text-slate-600">
                        Investigation Relevance
                      </p>
                    </div>

                  </div>

                  <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-5">

                    {[
                      [
                        "Connections",
                        selectedFeatures?.unique_connections ??
                        0,
                      ],
                      [
                        "Cross Cases",
                        selectedFeatures?.cross_case_connections ??
                        0,
                      ],
                      [
                        "Evidence",
                        selectedPerson.evidence_ids.length,
                      ],
                      [
                        "Sources",
                        selectedPerson.source_layers.length,
                      ],
                      [
                        "Relationships",
                        selectedFeatures?.total_relationships ??
                        0,
                      ],
                    ].map(([label, value]) => (
                      <div
                        key={label}
                        className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
                      >
                        <p className="text-[9px] uppercase tracking-[0.15em] text-slate-600">
                          {label}
                        </p>

                        <p className="mt-2 text-xl font-semibold text-slate-200">
                          {value}
                        </p>
                      </div>
                    ))}

                  </div>

                  <div className="mt-6 grid gap-5 lg:grid-cols-2">

                    <div>
                      <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                        Source Layers
                      </p>

                      <div className="flex flex-wrap gap-2">

                        {selectedPerson.source_layers.length >
                          0 ? (
                          selectedPerson.source_layers.map(
                            (source) => (
                              <span
                                key={source}
                                className="rounded-lg border border-cyan-400/10 bg-cyan-400/[0.04] px-3 py-2 text-[10px] font-medium text-cyan-300"
                              >
                                {source}
                              </span>
                            )
                          )
                        ) : (
                          <span className="text-xs text-slate-600">
                            No direct source-layer links
                          </span>
                        )}

                      </div>
                    </div>

                    <div>
                      <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                        Connected Cases
                      </p>

                      <div className="flex flex-wrap gap-2">

                        {selectedPerson.connected_cases
                          .slice(0, 8)
                          .map((caseId) => (
                            <span
                              key={caseId}
                              className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-3 py-2 font-mono text-[9px] text-slate-500"
                            >
                              {caseId.replace(
                                "case:",
                                ""
                              )}
                            </span>
                          ))}

                      </div>
                    </div>

                  </div>

                  <div className="mt-6">

                    <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                      Investigation Signals
                    </p>

                    <div className="grid gap-2 md:grid-cols-2">

                      {selectedPerson.signals.map(
                        (signal, index) => (
                          <div
                            key={index}
                            className="rounded-lg border border-white/[0.05] bg-white/[0.015] px-4 py-3 text-[11px] text-slate-500"
                          >
                            <span className="mr-2 text-cyan-400">
                              •
                            </span>

                            {signal}
                          </div>
                        )
                      )}

                    </div>

                  </div>

                </motion.div>
              )}

              {/* BOTTOM */}

              <div className="mt-5 grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">

                {/* AI */}

                <motion.div
                  initial={{
                    opacity: 0,
                    y: 20,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{ delay: 0.65 }}
                  className="relative overflow-hidden rounded-2xl border border-cyan-400/10 bg-gradient-to-br from-cyan-400/[0.06] to-transparent p-6"
                >

                  <div className="absolute right-[-80px] top-[-80px] h-48 w-48 rounded-full bg-cyan-400/[0.07] blur-3xl" />

                  <div className="relative">

                    <div className="flex items-center gap-2">
                      <BrainCircuit className="h-4 w-4 text-cyan-300" />

                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                        Investigation Intelligence
                      </p>
                    </div>

                    <h3 className="mt-4 text-base font-semibold text-slate-200">
                      Evidence-grounded analysis
                    </h3>

                    <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-500">
                      {selectedPerson
                        ? `${selectedPerson.name} currently has the strongest investigation relevance in the selected investigation based on graph connectivity, cross-case relationships and available evidence.`
                        : "The investigation analysis has been completed from the master graph."}
                    </p>

                    <div className="mt-5 flex flex-wrap gap-2">

                      {selectedPerson?.evidence_ids
                        .slice(0, 6)
                        .map((item) => (
                          <span
                            key={item}
                            className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1.5 text-[10px] font-medium text-slate-500"
                          >
                            {item.replace(
                              "evidence:",
                              ""
                            )}
                          </span>
                        ))}

                    </div>

                  </div>

                </motion.div>

                {/* ACTIVITY */}

                <motion.div
                  initial={{
                    opacity: 0,
                    y: 20,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{ delay: 0.7 }}
                  className="rounded-2xl border border-white/[0.07] bg-[#0a0f16]/80 p-5 backdrop-blur-xl"
                >

                  <div className="flex items-center justify-between">

                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
                        Activity
                      </p>

                      <h3 className="mt-1 text-sm font-semibold text-slate-200">
                        Recent Intelligence
                      </h3>
                    </div>

                    <Clock3 className="h-4 w-4 text-slate-600" />

                  </div>

                  <div className="mt-5 space-y-4">

                    {activities.map((activity) => {
                      const Icon = activity.icon;

                      return (
                        <div
                          key={
                            activity.time +
                            activity.title
                          }
                          className="flex gap-3"
                        >

                          <div className="relative flex w-10 shrink-0 justify-center">

                            <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.025]">
                              <Icon className="h-3.5 w-3.5 text-cyan-400/70" />
                            </div>

                          </div>

                          <div className="min-w-0 flex-1">

                            <div className="flex items-center justify-between gap-2">

                              <p className="truncate text-[11px] font-medium text-slate-400">
                                {activity.title}
                              </p>

                              <span className="text-[9px] text-slate-700">
                                {activity.time}
                              </span>

                            </div>

                            <p className="mt-0.5 text-[10px] text-slate-700">
                              {activity.description}
                            </p>

                          </div>

                        </div>
                      );
                    })}

                  </div>

                </motion.div>

              </div>

              {/* FOOTER STATUS */}

              <div className="mt-6 flex flex-col items-start justify-between gap-2 pb-4 text-[9px] uppercase tracking-[0.15em] text-slate-700 sm:flex-row sm:items-center">

                <span>
                  Criminal Network Analyzer · Intelligence Platform
                </span>

                <span className="flex items-center gap-2">

                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />

                  Graph Services Operational

                </span>

              </div>

            </div>
          </div>

        </section>
      </div>
    </main>
  );
}