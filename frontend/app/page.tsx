"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  FileText,
  Network,
  Users,
  RefreshCw,
} from "lucide-react";

import {
  analyzeInvestigation,
  getCases,
  getDashboard,
  type CaseData,
  type DashboardStatistics,
  type InvestigationAnalysis,
} from "@/lib/api";


const SELECTED_FIR_KEY =
  "criminal-network-selected-fir";


export default function DashboardPage() {

  const [stats, setStats] =
    useState<DashboardStatistics | null>(null);

  const [cases, setCases] =
    useState<CaseData[]>([]);

  const [selectedFir, setSelectedFir] =
    useState("");

  const [analysis, setAnalysis] =
    useState<InvestigationAnalysis | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [analysisLoading, setAnalysisLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  // --------------------------------------------------------
  // INITIAL LOAD
  // --------------------------------------------------------

  useEffect(() => {

    async function loadDashboard() {

      try {

        setLoading(true);
        setError("");

        const [
          dashboardData,
          caseData,
        ] = await Promise.all([
          getDashboard(),
          getCases(),
        ]);

        setStats(
          dashboardData.statistics
        );

        setCases(caseData);

        const savedFir =
          window.localStorage.getItem(
            SELECTED_FIR_KEY
          );

        const savedExists =
          savedFir &&
          caseData.some(
            (item) =>
              item.id === savedFir
          );

        if (savedExists) {

          setSelectedFir(
            savedFir
          );

        } else {

          const firstFir =
            caseData.find(
              (item) =>
                item.fir_number
            );

          if (firstFir) {

            setSelectedFir(
              firstFir.id
            );

            window.localStorage.setItem(
              SELECTED_FIR_KEY,
              firstFir.id
            );
          }
        }

      } catch (err) {

        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load dashboard."
        );

      } finally {

        setLoading(false);
      }
    }

    loadDashboard();

  }, []);


  // --------------------------------------------------------
  // ANALYSE SELECTED FIR
  // --------------------------------------------------------

  useEffect(() => {

    if (!selectedFir) {
      return;
    }

    window.localStorage.setItem(
      SELECTED_FIR_KEY,
      selectedFir
    );

    async function runAnalysis() {

      try {

        setAnalysisLoading(true);

        const result =
          await analyzeInvestigation(
            selectedFir
          );

        setAnalysis(result);

      } catch (err) {

        console.error(err);

        setAnalysis(null);

      } finally {

        setAnalysisLoading(false);
      }
    }

    runAnalysis();

  }, [selectedFir]);


  // --------------------------------------------------------
  // SELECTED CASE
  // --------------------------------------------------------

  const selectedCase =
    useMemo(
      () =>
        cases.find(
          (item) =>
            item.id === selectedFir
        ),
      [cases, selectedFir]
    );


  const selectedFirNumber =
    selectedCase?.fir_number ||
    selectedFir.replace("case:", "") ||
    "Select FIR";


  const topPeople =
    analysis?.top_relevant_people?.slice(
      0,
      5
    ) || [];


  // --------------------------------------------------------
  // UI
  // --------------------------------------------------------

  return (
    <div className="min-h-screen bg-[#05070b] p-8 text-white">

      {/* HEADER */}

      <div>

        <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
          Investigation Intelligence
        </div>

        <h1 className="mt-2 text-3xl font-bold">
          Criminal Network Analyzer
        </h1>

        <p className="mt-2 text-sm text-white/40">
          Evidence-driven investigation intelligence dashboard
        </p>

      </div>


      {/* ERROR */}

      {error && (

        <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>

      )}


      {/* STATISTICS */}

      <div className="mt-8 grid grid-cols-5 gap-4">

        <Stat
          icon={
            <FileText size={18} />
          }
          label="Cases"
          value={
            stats?.total_cases ?? "-"
          }
        />

        <Stat
          icon={
            <Activity size={18} />
          }
          label="Active"
          value={
            stats?.active_cases ?? "-"
          }
        />

        <Stat
          icon={
            <Users size={18} />
          }
          label="Entities"
          value={
            stats?.total_entities ?? "-"
          }
        />

        <Stat
          icon={
            <FileText size={18} />
          }
          label="Evidence"
          value={
            stats?.total_evidence ?? "-"
          }
        />

        <Stat
          icon={
            <Network size={18} />
          }
          label="Relationships"
          value={
            stats?.total_relationships ?? "-"
          }
        />

      </div>


      {/* MAIN GRID */}

      <div className="mt-8 grid grid-cols-[1.3fr_1fr] gap-6">

        {/* LEFT */}

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-lg font-semibold">
                Investigation Target
              </h2>

              <p className="mt-1 text-xs text-white/30">
                Select an existing FIR
              </p>

            </div>


            <select
              value={selectedFir}
              disabled={loading}
              onChange={(event) => {

                const value =
                  event.target.value;

                setSelectedFir(value);

                window.localStorage.setItem(
                  SELECTED_FIR_KEY,
                  value
                );

              }}
              className="min-w-[250px] rounded-xl border border-white/10 bg-[#0b1018] px-4 py-3 text-sm text-white outline-none"
            >

              {loading && (
                <option>
                  Loading FIRs...
                </option>
              )}

              {!loading &&
                cases.length === 0 && (
                  <option>
                    No FIRs available
                  </option>
                )}

              {cases
                .filter(
                  (item) =>
                    item.fir_number
                )
                .map((item) => (

                  <option
                    key={item.id}
                    value={item.id}
                  >
                    {item.fir_number}
                  </option>

                ))}

            </select>

          </div>


          {/* SELECTED FIR */}

          <div className="mt-8 rounded-xl border border-cyan-500/20 bg-cyan-500/[0.04] p-5">

            <div className="text-xs uppercase tracking-wider text-cyan-400">
              Selected FIR
            </div>

            <div className="mt-2 text-2xl font-bold">
              {selectedFirNumber}
            </div>

            <div className="mt-2 text-sm text-white/40">
              Investigation relevance
            </div>

            <div className="mt-4 text-4xl font-bold text-cyan-400">

              {analysisLoading ? (
                <span className="text-2xl">
                  Analysing...
                </span>
              ) : (
                `${getOverallRelevance(
                  analysis
                ).toFixed(1)}%`
              )}

            </div>

          </div>


          {/* AI SUMMARY */}

          <div className="mt-6">

            <div className="flex items-center gap-2">

              <BrainCircuit
                size={18}
                className="text-purple-400"
              />

              <h3 className="font-semibold">
                AI Investigation Summary
              </h3>

            </div>


            <p className="mt-3 text-sm leading-7 text-white/50">

              {getInvestigationSummary(
                selectedFirNumber,
                analysis
              )}

            </p>

          </div>


          {/* RELEVANT CASES BUTTON */}

          <div className="mt-6">

            <Link
              href={`/cases?fir=${encodeURIComponent(
                selectedFir
              )}`}
              className="flex items-center justify-between rounded-xl border border-cyan-500/20 bg-cyan-500/[0.04] p-4 transition hover:border-cyan-400/40 hover:bg-cyan-500/[0.08]"
            >

              <div>

                <div className="text-sm font-semibold text-white">
                  View Relevant Cases
                </div>

                <div className="mt-1 text-xs text-white/30">
                  Cases connected to {selectedFirNumber}
                </div>

              </div>

              <ArrowRight
                size={18}
                className="text-cyan-400"
              />

            </Link>

          </div>

        </div>


        {/* RIGHT */}

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">

          <h2 className="text-lg font-semibold">
            Top 5 Relevant People
          </h2>

          <p className="mt-1 text-xs text-white/30">
            Real Layer 1 investigation relevance
          </p>


          <div className="mt-6 space-y-3">

            {analysisLoading ? (

              <div className="flex items-center justify-center py-16 text-sm text-white/30">

                <RefreshCw
                  size={18}
                  className="mr-2 animate-spin"
                />

                Analysing selected FIR...

              </div>

            ) : topPeople.length === 0 ? (

              <div className="py-16 text-center text-sm text-white/30">
                No relevant people found.
              </div>

            ) : (

              topPeople.map(
                (person, index) => (

                  <div
                    key={
                      person.person_id ||
                      person.name ||
                      index
                    }
                    className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.025] p-4"
                  >

                    <div className="flex items-center gap-4">

                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/10 text-sm font-bold text-cyan-400">
                        {index + 1}
                      </div>

                      <div>

                        <div className="font-semibold">
                          {
                            person.name ||
                            "Unknown"
                          }
                        </div>

                        <div className="text-xs text-white/30">
                          Person entity
                        </div>

                      </div>

                    </div>


                    <div className="text-right">

                      <div className="font-bold text-cyan-400">
                        {(
                          person.relevance_score ??
                          0
                        ).toFixed(1)}
                        %
                      </div>

                      <div className="text-[10px] uppercase tracking-wider text-white/20">
                        relevance
                      </div>

                    </div>

                  </div>

                )
              )

            )}

          </div>

        </div>

      </div>

    </div>
  );
}


// ============================================================
// HELPERS
// ============================================================

function getOverallRelevance(
  analysis: InvestigationAnalysis | null
): number {

  if (
    !analysis ||
    !analysis.top_relevant_people ||
    analysis.top_relevant_people.length === 0
  ) {
    return 0;
  }

  const scores =
    analysis.top_relevant_people
      .slice(0, 5)
      .map(
        (person) =>
          person.relevance_score ?? 0
      );

  if (scores.length === 0) {
    return 0;
  }

  const total =
    scores.reduce(
      (sum, value) =>
        sum + value,
      0
    );

  return total / scores.length;
}


function getInvestigationSummary(
  firNumber: string,
  analysis: InvestigationAnalysis | null
): string {

  if (!analysis) {

    return `Select ${firNumber} to generate the Layer 1 investigation analysis from the master graph.`;
  }

  const people =
    analysis.top_relevant_people?.length || 0;

  const candidateCount =
    analysis.candidate_count || 0;

  if (people === 0) {

    return `The selected investigation ${firNumber} does not currently produce enough connected person entities for a Layer 1 relevance assessment.`;
  }

  return `Layer 1 analysis of ${firNumber} identified ${candidateCount} connected investigative candidates. The highest-ranked people are prioritized using graph-derived relationship, cross-case, communication, vehicle, location and account connectivity. These are investigative relevance signals and must be validated against the underlying evidence.`;
}


function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) {

  return (

    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">

      <div className="flex items-center gap-2 text-white/30">

        {icon}

        <span className="text-xs uppercase tracking-wider">
          {label}
        </span>

      </div>

      <div className="mt-3 text-2xl font-bold">
        {value}
      </div>

    </div>
  );
}