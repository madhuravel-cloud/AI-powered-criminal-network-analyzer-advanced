"use client";

import { useEffect, useState } from "react";
import {
    FileSearch,
    Plus,
    RefreshCw,
    Database,
} from "lucide-react";

import {
    getCases,
    getEvidence,
    createEvidence,
    type CaseData,
    type EvidenceData,
} from "@/lib/api";


export default function EvidencePage() {

    const [cases, setCases] = useState<CaseData[]>([]);
    const [evidence, setEvidence] = useState<EvidenceData[]>([]);

    const [selectedCase, setSelectedCase] =
        useState("");

    const [loading, setLoading] =
        useState(true);

    const [saving, setSaving] =
        useState(false);

    const [error, setError] =
        useState("");

    const [showForm, setShowForm] =
        useState(false);

    const [form, setForm] = useState({
        id: "",
        evidence_type: "FIR_DOCUMENT",
        source: "",
        storage_path: "",
        extracted_text: "",
        file_hash: "",
        layer_id: "",
    });


    async function loadCases() {

        try {

            const data = await getCases();

            setCases(data);

            if (data.length > 0 && !selectedCase) {
                setSelectedCase(data[0].id);
            }

        } catch (err) {

            console.error(err);

            setError(
                "Failed to load cases."
            );
        }
    }


    async function loadEvidence(caseId: string) {

        if (!caseId) {
            setEvidence([]);
            return;
        }

        try {

            setLoading(true);
            setError("");

            const data =
                await getEvidence(caseId);

            setEvidence(data);

        } catch (err) {

            console.error(err);

            setError(
                "Failed to load evidence."
            );

        } finally {

            setLoading(false);
        }
    }


    useEffect(() => {

        loadCases();

    }, []);


    useEffect(() => {

        if (selectedCase) {
            loadEvidence(selectedCase);
        }

    }, [selectedCase]);


    async function handleSubmit(
        event: React.FormEvent
    ) {

        event.preventDefault();

        if (!selectedCase) {
            setError("Select a case first.");
            return;
        }

        if (!form.id.trim()) {
            setError("Evidence ID is required.");
            return;
        }

        try {

            setSaving(true);
            setError("");

            await createEvidence({
                id: form.id.trim(),
                case_id: selectedCase,
                evidence_type:
                    form.evidence_type,
                source:
                    form.source || undefined,
                storage_path:
                    form.storage_path || undefined,
                extracted_text:
                    form.extracted_text || undefined,
                file_hash:
                    form.file_hash || undefined,
                layer_id:
                    form.layer_id || undefined,
            });

            setForm({
                id: "",
                evidence_type: "FIR_DOCUMENT",
                source: "",
                storage_path: "",
                extracted_text: "",
                file_hash: "",
                layer_id: "",
            });

            setShowForm(false);

            await loadEvidence(selectedCase);

        } catch (err) {

            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to add evidence."
            );

        } finally {

            setSaving(false);
        }
    }


    return (
        <div className="min-h-screen bg-[#05070b] p-8 text-white">

            <div className="flex items-start justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                        Evidence Intelligence
                    </div>

                    <h1 className="mt-2 text-3xl font-bold">
                        Evidence
                    </h1>

                    <p className="mt-2 text-sm text-white/40">
                        Evidence records stored in the investigation database
                    </p>

                </div>


                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-black transition hover:bg-cyan-400"
                >
                    <Plus size={17} />
                    Add Evidence
                </button>

            </div>


            {error && (
                <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
                    {error}
                </div>
            )}


            <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">

                <div className="flex items-center justify-between">

                    <div>

                        <h2 className="text-lg font-semibold">
                            Investigation Case
                        </h2>

                        <p className="mt-1 text-xs text-white/30">
                            Select the case whose evidence you want to inspect
                        </p>

                    </div>


                    <select
                        value={selectedCase}
                        onChange={(event) =>
                            setSelectedCase(
                                event.target.value
                            )
                        }
                        className="min-w-[280px] rounded-xl border border-white/10 bg-[#0b1018] px-4 py-3 text-sm text-white outline-none"
                    >

                        <option value="">
                            Select Case
                        </option>

                        {cases.map((item) => (
                            <option
                                key={item.id}
                                value={item.id}
                            >
                                {item.fir_number || item.id}
                            </option>
                        ))}

                    </select>

                </div>

            </div>


            {showForm && (

                <form
                    onSubmit={handleSubmit}
                    className="mt-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.03] p-6"
                >

                    <div className="flex items-center gap-3">

                        <div className="rounded-xl bg-cyan-500/10 p-3">
                            <Plus
                                size={20}
                                className="text-cyan-400"
                            />
                        </div>

                        <div>
                            <h2 className="font-semibold">
                                Add Evidence Record
                            </h2>

                            <p className="text-xs text-white/30">
                                This record will be written to PostgreSQL
                            </p>
                        </div>

                    </div>


                    <div className="mt-6 grid grid-cols-2 gap-4">

                        <Input
                            label="Evidence ID"
                            value={form.id}
                            onChange={(value) =>
                                setForm({
                                    ...form,
                                    id: value,
                                })
                            }
                            placeholder="EVIDENCE-001"
                        />


                        <div>

                            <label className="mb-2 block text-xs uppercase tracking-wider text-white/40">
                                Evidence Type
                            </label>

                            <select
                                value={form.evidence_type}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        evidence_type:
                                            event.target.value,
                                    })
                                }
                                className="w-full rounded-xl border border-white/10 bg-[#0b1018] px-4 py-3 text-sm text-white outline-none"
                            >

                                <option>
                                    FIR_DOCUMENT
                                </option>

                                <option>
                                    CDR_FILE
                                </option>

                                <option>
                                    CCTV_VIDEO
                                </option>

                                <option>
                                    VEHICLE_RECORD
                                </option>

                                <option>
                                    COURT_DOCUMENT
                                </option>

                                <option>
                                    BANK_TRANSACTION_FILE
                                </option>

                                <option>
                                    LOCATION_RECORD
                                </option>

                            </select>

                        </div>


                        <Input
                            label="Source"
                            value={form.source}
                            onChange={(value) =>
                                setForm({
                                    ...form,
                                    source: value,
                                })
                            }
                            placeholder="Police Station / CDR Provider"
                        />


                        <Input
                            label="Storage Path"
                            value={form.storage_path}
                            onChange={(value) =>
                                setForm({
                                    ...form,
                                    storage_path: value,
                                })
                            }
                            placeholder="minio://evidence/..."
                        />


                        <Input
                            label="File Hash"
                            value={form.file_hash}
                            onChange={(value) =>
                                setForm({
                                    ...form,
                                    file_hash: value,
                                })
                            }
                            placeholder="SHA-256 hash"
                        />


                        <Input
                            label="Layer ID"
                            value={form.layer_id}
                            onChange={(value) =>
                                setForm({
                                    ...form,
                                    layer_id: value,
                                })
                            }
                            placeholder="FIR / CDR / CCTV..."
                        />

                    </div>


                    <div className="mt-4">

                        <label className="mb-2 block text-xs uppercase tracking-wider text-white/40">
                            Extracted Text
                        </label>

                        <textarea
                            value={form.extracted_text}
                            onChange={(event) =>
                                setForm({
                                    ...form,
                                    extracted_text:
                                        event.target.value,
                                })
                            }
                            rows={5}
                            placeholder="Extracted or manually entered evidence information..."
                            className="w-full resize-none rounded-xl border border-white/10 bg-[#0b1018] px-4 py-3 text-sm text-white outline-none placeholder:text-white/20"
                        />

                    </div>


                    <div className="mt-5 flex justify-end">

                        <button
                            type="submit"
                            disabled={saving}
                            className="flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 text-sm font-semibold text-black disabled:opacity-50"
                        >

                            {saving ? (
                                <>
                                    <RefreshCw
                                        size={16}
                                        className="animate-spin"
                                    />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Database size={16} />
                                    Save Evidence
                                </>
                            )}

                        </button>

                    </div>

                </form>

            )}


            <div className="mt-8">

                <div className="mb-4 flex items-center justify-between">

                    <div>

                        <h2 className="text-lg font-semibold">
                            Evidence Records
                        </h2>

                        <p className="mt-1 text-xs text-white/30">
                            {evidence.length} records for selected case
                        </p>

                    </div>


                    <button
                        onClick={() =>
                            loadEvidence(selectedCase)
                        }
                        className="rounded-lg border border-white/10 p-2 text-white/40 hover:bg-white/[0.05] hover:text-white"
                    >
                        <RefreshCw size={16} />
                    </button>

                </div>


                {loading ? (

                    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-10 text-center text-sm text-white/30">
                        Loading evidence...
                    </div>

                ) : evidence.length === 0 ? (

                    <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-12 text-center">

                        <FileSearch
                            size={32}
                            className="mx-auto text-white/20"
                        />

                        <p className="mt-4 text-sm text-white/40">
                            No evidence records found for this case.
                        </p>

                    </div>

                ) : (

                    <div className="space-y-3">

                        {evidence.map((item) => (

                            <div
                                key={item.id}
                                className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-cyan-500/20"
                            >

                                <div className="flex items-start justify-between">

                                    <div className="flex items-start gap-4">

                                        <div className="rounded-xl bg-cyan-500/10 p-3">
                                            <FileSearch
                                                size={20}
                                                className="text-cyan-400"
                                            />
                                        </div>

                                        <div>

                                            <div className="font-semibold">
                                                {item.id}
                                            </div>

                                            <div className="mt-1 text-xs text-cyan-400">
                                                {item.evidence_type || "UNKNOWN"}
                                            </div>

                                        </div>

                                    </div>


                                    <div className="text-right">

                                        <div className="text-xs text-white/30">
                                            Source
                                        </div>

                                        <div className="mt-1 text-sm text-white/60">
                                            {item.source || "—"}
                                        </div>

                                    </div>

                                </div>


                                <div className="mt-5 grid grid-cols-4 gap-4 border-t border-white/10 pt-4">

                                    <Detail
                                        label="Layer"
                                        value={
                                            item.layer_id || "—"
                                        }
                                    />

                                    <Detail
                                        label="Storage"
                                        value={
                                            item.storage_path || "—"
                                        }
                                    />

                                    <Detail
                                        label="Hash"
                                        value={
                                            item.file_hash || "—"
                                        }
                                    />

                                    <Detail
                                        label="Created"
                                        value={
                                            item.created_at
                                                ? new Date(
                                                    item.created_at
                                                ).toLocaleString()
                                                : "—"
                                        }
                                    />

                                </div>


                                {item.extracted_text && (

                                    <div className="mt-4 rounded-xl bg-black/20 p-4">

                                        <div className="text-[10px] uppercase tracking-wider text-white/20">
                                            Extracted Text
                                        </div>

                                        <p className="mt-2 text-sm leading-6 text-white/50">
                                            {item.extracted_text}
                                        </p>

                                    </div>

                                )}

                            </div>

                        ))}

                    </div>

                )}

            </div>

        </div>
    );
}


function Input({
    label,
    value,
    onChange,
    placeholder,
}: {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
}) {

    return (
        <div>

            <label className="mb-2 block text-xs uppercase tracking-wider text-white/40">
                {label}
            </label>

            <input
                value={value}
                onChange={(event) =>
                    onChange(event.target.value)
                }
                placeholder={placeholder}
                className="w-full rounded-xl border border-white/10 bg-[#0b1018] px-4 py-3 text-sm text-white outline-none placeholder:text-white/20"
            />

        </div>
    );
}


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

            <div className="mt-1 truncate text-xs text-white/50">
                {value}
            </div>

        </div>
    );
}