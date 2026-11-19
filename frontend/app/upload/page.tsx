"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Download, Lock, Upload } from "lucide-react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { apiFetch } from "@/lib/api";
import { invalidateApi, setReducedTtl } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";

const SCHEMA: [string, string, "Yes" | "No", string][] = [
  ["supplier_id", "string", "Yes", "Unique supplier identifier"],
  ["shipment_date", "date", "Yes", "ISO 8601 or YYYY-MM-DD"],
  ["delay_days", "number", "Yes", "Integer days late (0 = on time)"],
  ["cost", "number", "Yes", "Shipment cost in local currency"],
  ["sku", "string", "No", "Product SKU"],
  ["region", "string", "No", "Geographic region"],
  ["warehouse_id", "string", "No", "Destination warehouse"],
  ["quality_score", "number", "No", "0.0–1.0 quality rating"],
];

const REFRESH_ENDPOINTS = [
  "/analytics/kpi",
  "/analytics/trends",
  "/analytics/suppliers",
  "/analytics/regions",
  "/analytics/delays",
  "/system/health",
  "/graph/visualization",
  "/graph/summary",
  "/graph/centrality",
  "/graph/critical-paths",
  "/graph/status",
];

function refreshAllData() {
  invalidateApi();
  REFRESH_ENDPOINTS.forEach((e) => invalidateApi(e));
}

const NOTICE_BASE =
  "mt-4 rounded-[10px] border px-4 py-3 text-[13px] leading-relaxed";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [preview, setPreview] = useState<any>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [missingColumns, setMissingColumns] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sampleLoading, setSampleLoading] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const redirectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* Stop polling and pending redirects when leaving the page */
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (redirectRef.current) clearTimeout(redirectRef.current);
    };
  }, []);

  const validateFile = (f: File): string | null => {
    const validExtensions = [".csv", ".xlsx", ".xls"];
    const ext = "." + (f.name.split(".").pop()?.toLowerCase() ?? "");

    if (!validExtensions.includes(ext)) {
      return `Invalid file type: ${ext}. Please upload a .csv, .xlsx, or .xls file.`;
    }
    if (f.size === 0) {
      return "This file is empty. Please select a valid file.";
    }
    if (f.size > 50 * 1024 * 1024) {
      return "This file is too large. The maximum size is 50 MB.";
    }
    return null;
  };

  const checkRequiredColumns = (previewData: any): string[] => {
    const available = (previewData.columns || []).map((c: string) => c.toLowerCase());
    const has = (terms: string[]) =>
      available.some((c: string) => terms.some((t) => c.includes(t)));
    const missing: string[] = [];

    if (!has(["supplier", "vendor", "seller", "source"])) missing.push("supplier");
    if (!has(["product", "sku", "item", "part", "material"])) missing.push("product / sku");
    if (!has(["cost", "price", "amount", "rate", "value"])) missing.push("cost");
    if (!has(["lead_time", "leadtime", "delay", "late", "delivery"])) {
      missing.push("delay_days / lead_time");
    }
    return missing;
  };

  const pollStatus = () => {
    if (pollRef.current) clearInterval(pollRef.current);

    let pollCount = 0;
    const MAX_POLLS = 60; // about 2 minutes

    pollRef.current = setInterval(async () => {
      pollCount++;
      try {
        const res = await apiFetch("/system/health");
        const data = await res.json();

        const dataReady = data.supply_row_count > 0 || data.has_real_data;
        const analysisDone = !data.is_analyzing;

        if (dataReady || (analysisDone && pollCount > 2) || pollCount >= MAX_POLLS) {
          if (pollRef.current) clearInterval(pollRef.current);
          pollRef.current = null;
          setAnalyzing(false);
          refreshAllData();
          setProgress(100);
          redirectRef.current = setTimeout(() => router.push("/dashboard"), 800);
        } else {
          setProgress((p) => Math.min(p + 5, 94));
        }
      } catch {
        /* ignore transient polling errors */
      }
    }, 2000);
  };

  const handleLoadSample = async () => {
    setSampleLoading(true);
    setError(null);
    setValidationError(null);
    setMissingColumns([]);
    try {
      const res = await apiFetch("/upload/sample", { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setResult({
          status: "success",
          rows_inserted: data.rows_inserted,
          message: data.message || "Sample supply chain dataset loaded successfully.",
        });
        refreshAllData();
        if (typeof window !== "undefined") {
          localStorage.setItem("nexus_has_real_data", "true");
        }
        setAnalyzing(true);
        setProgress(40);
        pollStatus();
      } else {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "The sample dataset could not be loaded. Please try again."
        );
      }
    } catch {
      setError("Can't reach the server right now. Check your connection and try again.");
    } finally {
      setSampleLoading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    setError(null);
    try {
      const res = await apiFetch("/upload/template");
      if (!res.ok) throw new Error("template");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nexus_supply_chain_template.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("The CSV template could not be downloaded. Please try again.");
    }
  };

  const handleFile = async (f: File) => {
    const problem = validateFile(f);
    if (problem) {
      setValidationError(problem);
      setFile(null);
      setPreview(null);
      setMissingColumns([]);
      return;
    }

    setValidationError(null);
    setError(null);
    setFile(f);
    setResult(null);
    setPreview(null);
    setMissingColumns([]);

    const formData = new FormData();
    formData.append("file", f);
    try {
      const res = await apiFetch("/upload/preview", { method: "POST", body: formData });
      if (res.ok) {
        const previewData = await res.json();
        setPreview(previewData);
        setMissingColumns(checkRequiredColumns(previewData));
      }
    } catch {
      /* preview is optional */
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleUpload = async () => {
    if (!file) return;

    const problem = validateFile(file);
    if (problem) {
      setValidationError(problem);
      return;
    }

    // Quick connectivity check before attempting the full upload
    try {
      const ping = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/`,
        { method: "GET", signal: AbortSignal.timeout(3000) }
      );
      if (!ping.ok) throw new Error("unhealthy");
    } catch {
      setResult({
        status: "error",
        message: "Can't reach the server right now. Make sure the backend is running, then try again.",
      });
      return;
    }

    setLoading(true);
    setProgress(15);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiFetch("/upload", { method: "POST", body: formData });
      const data = await res.json();

      if (res.status === 422 && data.detail?.error === "ambiguous_column_mapping") {
        setLoading(false);
        router.push("/upload/map");
        return;
      }

      setResult(data);

      if (data.status === "success") {
        setLoading(false);
        setAnalyzing(true);
        setProgress(40);

        if (typeof window !== "undefined") {
          localStorage.removeItem("nexus_demo_mode");
          localStorage.setItem("nexus_has_real_data", "true");
        }

        refreshAllData();
        setReducedTtl();
        pollStatus();
      } else {
        setResult({
          status: "error",
          message: typeof data.detail === "string" ? data.detail : "Upload failed. Please try again.",
        });
        setLoading(false);
      }
    } catch (err) {
      console.error("Upload error:", err);
      const isNetworkError = err instanceof TypeError && err.message === "Failed to fetch";
      setResult({
        status: "error",
        message: isNetworkError
          ? "Can't reach the server right now. Make sure the backend is running, then try again."
          : "Upload failed. Please check your connection and try again.",
      });
      setLoading(false);
    }
  };

  const busy = loading || analyzing || sampleLoading;
  const canSubmit = !!file && !loading && !analyzing && result?.status !== "success";

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div className="mx-auto w-full max-w-[var(--max-content)]">
            {/* Page header */}
            <div className="page-header">
              <div>
                <div className="text-micro" style={{ marginBottom: 6 }}>
                  Overview
                </div>
                <h1 className="page-title">Upload Data</h1>
                <p className="page-subtitle">
                  Ingest CSV or Excel files. Columns are auto-detected and mapped to the
                  canonical schema.
                </p>
              </div>
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="btn btn-secondary"
              >
                View Dashboard
              </button>
            </div>

            {/* KPI strip */}
            <div className="kpi-grid">
              <KpiCard label="Supported Formats" value="3" sub="CSV · XLSX · XLS" />
              <KpiCard label="Row Limit" value="1M+" sub="Auto-chunked for large files" />
              <KpiCard label="Auto-Mapping" value="Active" sub="Synonym-based column detection" />
              <KpiCard
                label="File Selected"
                value={file ? "1" : "—"}
                sub={file ? `${(file.size / 1024).toFixed(1)} KB · ${file.name}` : "No file chosen"}
              />
            </div>

            {/* Two-column workspace */}
            <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_440px]">
              {/* ── Left: upload flow ── */}
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    id="load-sample-btn"
                    onClick={handleLoadSample}
                    disabled={busy}
                    className={`btn btn-primary ${sampleLoading ? "loading" : ""}`}
                  >
                    {sampleLoading ? "Loading sample data…" : "Load sample dataset"}
                  </button>

                  <button
                    type="button"
                    id="download-template-btn"
                    onClick={handleDownloadTemplate}
                    className="btn btn-secondary"
                  >
                    <Download size={15} strokeWidth={1.6} aria-hidden="true" />
                    Download CSV template
                  </button>

                  <span className="text-caption" style={{ color: "var(--color-text-3)" }}>
                    No setup needed to try it
                  </span>
                </div>

                {/* Drop zone */}
                <label
                  htmlFor="file-input"
                  id="upload-dropzone"
                  className="upload-dropzone mt-4 block"
                  onDragOver={(e) => {
                    e.preventDefault();
                    if (!busy) setDragOver(true);
                  }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => {
                    if (busy) {
                      e.preventDefault();
                      setDragOver(false);
                      return;
                    }
                    handleDrop(e);
                  }}
                  style={{
                    position: "relative",
                    cursor: busy ? "not-allowed" : "pointer",
                    padding: "44px 24px",
                    textAlign: "center",
                    border: "1px dashed",
                    borderColor: dragOver
                      ? "var(--color-text-1)"
                      : file
                        ? "var(--color-border-hi)"
                        : "var(--color-border)",
                    borderRadius: "var(--radius-lg)",
                    background: dragOver ? "rgba(243, 239, 228, 0.04)" : "var(--color-surface)",
                    transition:
                      "border-color 160ms var(--ease), background 160ms var(--ease)",
                    opacity: busy ? 0.6 : 1,
                  }}
                >
                  <input
                    id="file-input"
                    className="file-input"
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    aria-label="Upload data file"
                    aria-describedby="upload-instructions"
                    disabled={busy}
                    style={{
                      opacity: 0,
                      width: "0.1px",
                      height: "0.1px",
                      position: "absolute",
                      zIndex: -1,
                    }}
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleFile(f);
                    }}
                  />

                  <div className="upload-dropzone-content flex flex-col items-center gap-3">
                    <Upload
                      size={22}
                      strokeWidth={1.4}
                      aria-hidden="true"
                      style={{ color: "var(--color-text-3)" }}
                    />
                    {file ? (
                      <div>
                        <div
                          style={{
                            fontSize: 14,
                            fontWeight: 500,
                            color: "var(--color-text-1)",
                            overflowWrap: "anywhere",
                          }}
                        >
                          {file.name}
                        </div>
                        <div className="text-caption" style={{ marginTop: 4 }}>
                          {(file.size / 1024).toFixed(1)} KB · Click to replace
                        </div>
                      </div>
                    ) : (
                      <div id="upload-instructions">
                        <div style={{ fontSize: 15, color: "var(--color-text-1)", marginBottom: 4 }}>
                          Drag and drop your file here, or click to browse
                        </div>
                        <div className="text-caption">
                          Supports .csv, .xlsx, .xls up to 50 MB
                        </div>
                      </div>
                    )}
                  </div>
                </label>

                {/* Notices */}
                {validationError && (
                  <div
                    role="alert"
                    className={NOTICE_BASE}
                    style={{
                      background: "rgba(239, 107, 107, 0.08)",
                      borderColor: "rgba(239, 107, 107, 0.3)",
                      color: "var(--color-danger)",
                    }}
                  >
                    {validationError}
                  </div>
                )}

                {error && (
                  <div
                    role="alert"
                    className={NOTICE_BASE}
                    style={{
                      background: "rgba(239, 107, 107, 0.08)",
                      borderColor: "rgba(239, 107, 107, 0.3)",
                      color: "var(--color-danger)",
                    }}
                  >
                    {error}
                  </div>
                )}

                {missingColumns.length > 0 && (
                  <div
                    role="status"
                    className={NOTICE_BASE}
                    style={{
                      background: "rgba(224, 164, 88, 0.08)",
                      borderColor: "rgba(224, 164, 88, 0.3)",
                    }}
                  >
                    <div style={{ color: "var(--color-warn)", fontWeight: 500 }}>
                      Missing required columns: {missingColumns.join(", ")}
                    </div>
                    <div className="text-caption" style={{ marginTop: 4, color: "var(--color-text-3)" }}>
                      Your file may still work, but analysis quality may be reduced. Adding these
                      columns gives better results.
                    </div>
                  </div>
                )}

                {/* Column mapping preview */}
                {preview && (
                  <section
                    aria-label="Column mapping preview"
                    className="mt-4 overflow-hidden"
                    style={{
                      background: "var(--color-surface)",
                      border: "1px solid var(--color-border)",
                      borderRadius: "var(--radius-lg)",
                    }}
                  >
                    <div
                      className="flex flex-wrap items-center justify-between gap-2"
                      style={{
                        padding: "12px 16px",
                        borderBottom: "1px solid var(--color-border)",
                      }}
                    >
                      <span className="text-micro" style={{ color: "var(--color-text-2)" }}>
                        Column mapping preview
                      </span>
                      <span className="text-caption" style={{ color: "var(--color-text-3)" }}>
                        {Object.keys(preview.auto_mapping ?? {}).length} columns mapped ·{" "}
                        {preview.preview_rows?.length || 0} rows previewed
                      </span>
                    </div>

                    <div
                      className="flex flex-wrap gap-2"
                      style={{
                        padding: "12px 16px",
                        borderBottom: "1px solid var(--color-border)",
                      }}
                    >
                      {Object.entries(preview.auto_mapping ?? {}).map(([target, source]: any) => (
                        <span key={target} className="badge badge-info">
                          {source?.mapped_to ?? source} → {target}
                        </span>
                      ))}
                    </div>

                    {preview.preview_rows?.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="data-table">
                          <thead>
                            <tr>
                              {preview.columns?.slice(0, 7).map((c: string) => (
                                <th key={c}>{c}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {preview.preview_rows.slice(0, 4).map((row: any, i: number) => (
                              <tr key={i} style={{ cursor: "default" }}>
                                {preview.columns?.slice(0, 7).map((c: string) => (
                                  <td
                                    key={c}
                                    style={{
                                      height: 40,
                                      color: "var(--color-text-2)",
                                      maxWidth: 180,
                                      overflow: "hidden",
                                      textOverflow: "ellipsis",
                                      whiteSpace: "nowrap",
                                    }}
                                  >
                                    {String(row[c] ?? "—")}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>
                )}

                {/* Progress */}
                {(loading || analyzing) && (
                  <div className="mt-4">
                    <div
                      role="progressbar"
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={progress}
                      aria-label={analyzing ? "Running analysis" : "Uploading file"}
                      style={{
                        height: 4,
                        borderRadius: 999,
                        background: "var(--color-surface-3)",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${progress}%`,
                          height: "100%",
                          borderRadius: 999,
                          background: "var(--color-text-1)",
                          transition: "width 400ms var(--ease)",
                        }}
                      />
                    </div>
                    <div className="text-caption" style={{ marginTop: 8, color: "var(--color-text-3)" }}>
                      {analyzing
                        ? `Running analysis pipeline… ${progress}%`
                        : `Uploading and validating… ${progress}%`}
                    </div>
                  </div>
                )}

                {/* Result */}
                {result && (
                  <div
                    role={result.status === "success" ? "status" : "alert"}
                    className="mt-4"
                    style={{
                      background: "var(--color-surface)",
                      border: "1px solid var(--color-border)",
                      borderLeft: `3px solid ${result.status === "success" ? "var(--color-ok)" : "var(--color-danger)"
                        }`,
                      borderRadius: "var(--radius-md)",
                      padding: 16,
                    }}
                  >
                    <div style={{ fontWeight: 500, fontSize: 14, color: "var(--color-text-1)" }}>
                      {result.status === "success"
                        ? `${(result.rows_inserted ?? 0).toLocaleString()} rows imported successfully`
                        : "Upload failed"}
                    </div>
                    {result.message && (
                      <div className="text-small" style={{ marginTop: 4 }}>
                        {typeof result.message === "string"
                          ? result.message
                          : "Something went wrong while processing the file."}
                      </div>
                    )}
                    {(result.rows_rejected ?? 0) > 0 && (
                      <div className="text-caption" style={{ marginTop: 4, color: "var(--color-text-3)" }}>
                        {result.rows_rejected} rows skipped because of invalid or missing required
                        fields.
                      </div>
                    )}
                    {result.status === "success" && (
                      <div className="text-caption" style={{ marginTop: 8, color: "var(--color-ok)" }}>
                        Opening the dashboard once analysis finishes…
                      </div>
                    )}
                  </div>
                )}

                {/* Submit */}
                {canSubmit && (
                  <button
                    type="button"
                    id="upload-submit-btn"
                    onClick={handleUpload}
                    disabled={!!validationError}
                    className="btn btn-primary btn-lg mt-5 w-full"
                    style={
                      missingColumns.length > 0
                        ? { boxShadow: "inset 0 0 0 1px var(--color-warn)" }
                        : undefined
                    }
                  >
                    {result?.status === "error"
                      ? "Try again"
                      : missingColumns.length > 0
                        ? "Upload with missing columns"
                        : "Upload and analyze"}
                  </button>
                )}
              </div>

              {/* ── Right: reference ── */}
              <aside className="min-w-0 space-y-4" aria-label="Upload reference">
                <div
                  className="flex items-start gap-3"
                  style={{
                    padding: "14px 16px",
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-lg)",
                  }}
                >
                  <Lock
                    size={16}
                    strokeWidth={1.6}
                    aria-hidden="true"
                    style={{ color: "var(--color-text-2)", marginTop: 2, flexShrink: 0 }}
                  />
                  <p className="text-small" style={{ lineHeight: 1.6 }}>
                    <span style={{ color: "var(--color-text-1)", fontWeight: 500 }}>
                      Privacy.
                    </span>{" "}
                    Ingestion and ML analysis run in-memory on your instance. Supplier data is not
                    shared, logged externally, or used to train public models.
                  </p>
                </div>

                <section
                  aria-label="Expected column schema"
                  style={{
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-lg)",
                    overflow: "hidden",
                  }}
                >
                  <div
                    className="text-micro"
                    style={{ padding: "14px 16px", borderBottom: "1px solid var(--color-border)" }}
                  >
                    Expected column schema
                  </div>
                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          {["Column", "Type", "Required", "Description"].map((h) => (
                            <th key={h} style={{ padding: "10px 12px" }}>
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {SCHEMA.map(([col, type, req, desc]) => (
                          <tr key={col} style={{ cursor: "default" }}>
                            <td
                              style={{
                                padding: "10px 12px",
                                height: 44,
                                fontFamily: "var(--font-mono)",
                                fontSize: 12,
                                whiteSpace: "nowrap",
                              }}
                            >
                              {col}
                            </td>
                            <td
                              style={{
                                padding: "10px 12px",
                                color: "var(--color-text-3)",
                                whiteSpace: "nowrap",
                              }}
                            >
                              {type}
                            </td>
                            <td style={{ padding: "10px 12px" }}>
                              <span
                                className={req === "Yes" ? "badge badge-info" : "badge"}
                                style={
                                  req === "No"
                                    ? {
                                      color: "var(--color-text-3)",
                                      border: "1px solid var(--color-border)",
                                    }
                                    : undefined
                                }
                              >
                                {req}
                              </span>
                            </td>
                            <td style={{ padding: "10px 12px", color: "var(--color-text-2)", minWidth: 180 }}>
                              {desc}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </aside>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}