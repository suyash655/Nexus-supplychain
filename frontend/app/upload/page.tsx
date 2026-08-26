"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { apiFetch } from "@/lib/api";
import { invalidateApi, forceRefreshApi, setReducedTtl } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";

const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";


/* ── Page ── */
export default function UploadPage() {
  const router = useRouter();
  const [file, setFile]         = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult]     = useState<any>(null);
  const [preview, setPreview]   = useState<any>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [missingColumns, setMissingColumns] = useState<string[]>([]);
  const [error, setError]       = useState<string | null>(null);

  const validateFile = (f: File): string | null => {
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const fileExtension = '.' + f.name.split('.').pop()?.toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
      return `Invalid file type: ${fileExtension}. Please upload .csv, .xlsx, or .xls files.`;
    }
    
    if (f.size === 0) {
      return 'File is empty. Please select a valid file.';
    }
    
    if (f.size > 50 * 1024 * 1024) { // 50MB limit
      return 'File is too large. Maximum size is 50MB.';
    }
    
    return null;
  };

  const checkRequiredColumns = (previewData: any): string[] => {
    const requiredColumns = ['supplier', 'product', 'cost', 'lead_time'];
    const availableColumns = previewData.columns || [];
    const missing = requiredColumns.filter(col => 
      !availableColumns.some((avail: string) => 
        avail.toLowerCase().includes(col.toLowerCase()) ||
        avail.toLowerCase().includes(col.replace('_', ''))
      )
    );
    return missing;
  };

  const handleFile = async (f: File) => {
    const error = validateFile(f);
    if (error) {
      setValidationError(error);
      setFile(null);
      setPreview(null);
      setMissingColumns([]);
      return;
    }
    
    setValidationError(null);
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
        
        // Check for required columns
        const missing = checkRequiredColumns(previewData);
        setMissingColumns(missing);
      }
    } catch { /* preview is optional */ }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, []);

  const pollStatus = () => {
    let pollCount = 0;
    const MAX_POLLS = 60; // max 2 minutes of polling
    const interval = setInterval(async () => {
      pollCount++;
      try {
        const res  = await apiFetch("/system/health");
        const data = await res.json();
        // Stop polling when:
        // - supply_row_count > 0 (data is in DB, dashboard can show live data), OR
        // - has_real_data (analysis saved), OR
        // - analysis finished AND we've polled at least once
        const dataReady = (data.supply_row_count > 0) || data.has_real_data;
        const analysisDone = !data.is_analyzing;
        if (dataReady || (analysisDone && pollCount > 2) || pollCount >= MAX_POLLS) {
          clearInterval(interval);
          setAnalyzing(false);
          // Force aggressive cache invalidation for all endpoints
          invalidateApi();
          // Invalidate specific dashboard endpoints to ensure fresh data
          invalidateApi("/analytics/kpi");
          invalidateApi("/analytics/trends");
          invalidateApi("/analytics/suppliers");
          invalidateApi("/analytics/regions");
          invalidateApi("/analytics/delays");
          invalidateApi("/system/health");
          // Invalidate graph endpoints so the network page reloads real data
          invalidateApi("/graph/visualization");
          invalidateApi("/graph/summary");
          invalidateApi("/graph/centrality");
          invalidateApi("/graph/critical-paths");
          invalidateApi("/graph/status");
          setProgress(100);
          setTimeout(() => router.push("/dashboard"), 800);
        } else {
          setProgress(p => Math.min(p + 5, 94));
        }
      } catch { /* ignore */ }
    }, 2000);
  };

  const handleUpload = async () => {
    if (!file) return;

    // Re-validate before upload
    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      return;
    }

    // Quick connectivity check before attempting full upload
    try {
      const ping = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/`, {
        method: "GET",
        signal: AbortSignal.timeout(3000),
      });
      if (!ping.ok) throw new Error("Backend unhealthy");
    } catch {
      setResult({
        status: "error",
        message: "Cannot reach the backend server. Start it with: cd backend && ..\\venv\\Scripts\\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
      });
      return;
    }

    setLoading(true);
    setProgress(15);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res  = await apiFetch("/upload", { method: "POST", body: formData });
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

        // Clear demo mode flag on successful upload
        if (typeof window !== "undefined") {
          localStorage.removeItem("nexus_demo_mode");
        }

        // Force aggressive cache invalidation immediately after upload
        invalidateApi();
        // Mark analytics endpoints for reduced TTL to ensure fresh data
        setReducedTtl();
        // Invalidate specific dashboard endpoints to ensure fresh data
        invalidateApi("/analytics/kpi");
        invalidateApi("/analytics/trends");
        invalidateApi("/analytics/suppliers");
        invalidateApi("/analytics/regions");
        invalidateApi("/analytics/delays");
        invalidateApi("/system/health");
        // Invalidate graph endpoints
        invalidateApi("/graph/visualization");
        invalidateApi("/graph/summary");
        invalidateApi("/graph/centrality");
        invalidateApi("/graph/critical-paths");
        invalidateApi("/graph/status");

        // Set a flag to indicate real data was uploaded
        if (typeof window !== "undefined") {
          localStorage.setItem("nexus_has_real_data", "true");
        }

        pollStatus();
      } else {
        setResult({ status: "error", message: data.detail || "Upload failed." });
        setLoading(false);
      }
    } catch (err) {
      console.error("Upload error:", err);
      const isNetworkError = err instanceof TypeError && err.message === "Failed to fetch";
      setResult({
        status: "error",
        message: isNetworkError
          ? "Cannot reach the backend server. Make sure it is running on http://localhost:8000 — see README for startup instructions."
          : "Upload failed. Check backend connectivity.",
      });
      setLoading(false);
    }
  };

  const isActive = !loading && !result;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">

          {/* ══ LAYER A — Page Header ══ */}
          <div style={{
            display: "flex", alignItems: "flex-start", justifyContent: "space-between",
            paddingBottom: 16, marginBottom: 24, borderBottom: "1px solid var(--color-border)",
          }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>Overview</div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                Upload Data
              </h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>
                Ingest CSV or Excel files. Columns are auto-detected and mapped to the canonical schema.
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              style={{
                display: "inline-flex", alignItems: "center", padding: "8px 16px",
                borderRadius: 4, fontSize: 13, fontWeight: 600, fontFamily: "var(--font-sans)",
                background: "transparent", border: "1px solid var(--color-border-hi)",
                color: "var(--color-text-1)", cursor: "pointer", flexShrink: 0,
                transition: `background 120ms ${EASE}`,
              }}
              onMouseEnter={e => (e.currentTarget.style.background = "var(--color-surface-2)")}
              onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
            >
              View Dashboard
            </button>
          </div>

          {/* ══ LAYER B — KPI Strip ══ */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
            <KpiCard label="Supported Formats" value="3" sub="CSV · XLSX · XLS" />
            <KpiCard label="Row Limit" value="1M+" sub="Auto-chunked for large files" />
            <KpiCard label="Auto-Mapping" value="Active" sub="Synonym-based column detection" />
            <KpiCard
              label="File Selected"
              value={file ? "1" : "—"}
              sub={file ? `${(file.size / 1024).toFixed(1)} KB · ${file.name}` : "No file chosen"}
            />
          </div>

          {/* ══ LAYER C — Upload UI ══ */}
          <div style={{ maxWidth: 720 }}>

            {/* Drop zone */}
            <label
              htmlFor="file-input"
              id="upload-dropzone"
              className="upload-dropzone"
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              style={{
                display:       "block",
                borderColor:   dragOver ? "var(--color-accent)" : file ? "var(--color-border-hi)" : "var(--color-border)",
                borderWidth:   1,
                borderStyle:   "dashed",
                borderRadius:  6,
                padding:       40,
                textAlign:     "center",
                cursor:        "pointer",
                background:    dragOver ? "rgba(232,255,71,0.04)" : "var(--color-surface)",
                transition:    `border-color 120ms ${EASE}, background 120ms ${EASE}`,
                position:      "relative"
              }}
            >
              <input
                id="file-input"
                className="file-input"
                type="file"
                accept=".csv,.xlsx,.xls"
                aria-label="Upload data file"
                aria-describedby="upload-instructions"
                style={{ 
                  opacity: 0, 
                  width: "0.1px", 
                  height: "0.1px", 
                  position: "absolute", 
                  zIndex: -1 
                }}
                onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
              />

              <div className="upload-dropzone-content">
                {file ? (
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)", marginBottom: 4 }}>
                      {file.name}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--color-text-3)" }}>
                      {(file.size / 1024).toFixed(1)} KB · Click to replace
                    </div>
                  </div>
                ) : (
                  <div id="upload-instructions">
                    <div style={{ fontSize: 15, fontWeight: 400, color: "var(--color-text-2)", marginBottom: 4 }}>
                      Drag &amp; drop your file here, or click to browse
                    </div>
                    <div style={{ fontSize: 12, color: "var(--color-text-3)" }}>
                      Supports .csv, .xlsx, .xls — up to 1M+ rows
                    </div>
                  </div>
                )}
              </div>
            </label>

            {/* Validation Error */}
            {validationError && (
              <div style={{
                marginTop: 16,
                padding: "12px 16px",
                background: "rgba(239, 68, 68, 0.08)",
                border: "1px solid rgba(239, 68, 68, 0.25)",
                borderRadius: 6,
                display: "flex",
                gap: 12,
                alignItems: "center",
              }}>
                <span style={{ fontSize: 13, color: "#ef4444" }}>
                  {validationError}
                </span>
              </div>
            )}

            {/* Missing Columns Warning */}
            {missingColumns.length > 0 && (
              <div style={{
                marginTop: 16,
                padding: "12px 16px",
                background: "rgba(245, 158, 11, 0.08)",
                border: "1px solid rgba(245, 158, 11, 0.25)",
                borderRadius: 6,
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}>
                <div style={{ fontSize: 13, color: "#f59e0b", fontWeight: 500 }}>
                  Missing required columns: {missingColumns.join(", ")}
                </div>
                <div style={{ fontSize: 12, color: "var(--color-text-3)" }}>
                  Your file may still work, but analysis quality may be reduced. Consider adding these columns for better results.
                </div>
              </div>
            )}

            {/* Error Notice */}
            {error && (
              <div style={{
                marginTop: 16,
                padding: "12px 16px",
                background: "rgba(239, 68, 68, 0.08)",
                border: "1px solid rgba(239, 68, 68, 0.25)",
                borderRadius: 6,
                display: "flex",
                gap: 12,
                alignItems: "center",
              }}>
                <span style={{ fontSize: 13, color: "#ef4444" }}>
                  {error}
                </span>
              </div>
            )}

            {/* Column preview */}
            {preview && (
              <div style={{
                marginTop: 16, background: "var(--color-surface)",
                border: "1px solid var(--color-border)", borderRadius: 6, overflow: "hidden",
              }}>
                <div style={{
                  padding: "12px 16px", borderBottom: "1px solid var(--color-border)",
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                }}>
                  <span style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "0.05em", color: "var(--color-text-2)" }}>
                    Pre-Commit Column Mapping Preview
                  </span>
                  <span style={{ fontSize: 11, color: "var(--color-text-3)" }}>
                    {Object.keys(preview.auto_mapping ?? {}).length} columns mapped · {preview.preview_rows?.length || 0} rows preview
                  </span>
                </div>

                {/* Mapping pills */}
                <div style={{ padding: "12px 16px", display: "flex", flexWrap: "wrap", gap: 6, borderBottom: "1px solid var(--color-border)" }}>
                  {Object.entries(preview.auto_mapping ?? {}).map(([target, source]: any) => (
                    <span
                      key={target}
                      style={{
                        background: "rgba(232,255,71,0.06)",
                        border: "1px solid rgba(232,255,71,0.18)",
                        borderRadius: 999,
                        padding: "2px 10px",
                        fontSize: 11,
                        fontWeight: 500,
                        color: "var(--color-accent)",
                      }}
                    >
                      {source?.mapped_to ?? source} → {target}
                    </span>
                  ))}
                </div>

                {/* Data preview table */}
                {preview.preview_rows?.length > 0 && (
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                      <thead>
                        <tr>
                          {preview.columns?.slice(0, 7).map((c: string) => (
                            <th key={c} style={{
                              textAlign: "left", padding: "8px 12px",
                              fontSize: 11, fontWeight: 500,
                              textTransform: "uppercase", letterSpacing: "0.05em",
                              color: "var(--color-text-3)",
                              borderBottom: "1px solid var(--color-border)",
                              background: "var(--color-surface)",
                            }}>
                              {c}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.preview_rows.slice(0, 4).map((row: any, i: number) => (
                          <tr key={i}>
                            {preview.columns?.slice(0, 7).map((c: string) => (
                              <td key={c} style={{
                                padding: "8px 12px", height: 36,
                                borderBottom: "1px solid var(--color-border)",
                                color: "var(--color-text-2)", fontSize: 12,
                                verticalAlign: "middle",
                                maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                              }}>
                                {String(row[c] ?? "—")}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Progress bar */}
            {(loading || analyzing) && (
              <div style={{ marginTop: 16 }}>
                <div style={{ height: 4, borderRadius: 999, background: "var(--color-surface-2)", overflow: "hidden" }}>
                  <div style={{
                    width: `${progress}%`, height: "100%", borderRadius: 999,
                    background: "var(--color-accent)",
                    transition: "width 400ms cubic-bezier(0.16,1,0.3,1)",
                  }} />
                </div>
                <div style={{ marginTop: 8, fontSize: 12, color: "var(--color-text-3)" }}>
                  {analyzing
                    ? `Running analysis pipeline... ${progress}%`
                    : `Uploading and validating... ${progress}%`}
                </div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div style={{
                marginTop: 16,
                background: "var(--color-surface)",
                border: `1px solid var(--color-border)`,
                borderLeft: `4px solid ${result.status === "success" ? "#22C55E" : "#FF4444"}`,
                borderRadius: 6,
                padding: 16,
              }}>
                <div style={{ fontWeight: 600, fontSize: 14, color: "var(--color-text-1)", marginBottom: 4 }}>
                  {result.status === "success"
                    ? `${result.rows_inserted?.toLocaleString()} rows imported successfully`
                    : "Upload failed"}
                </div>
                {result.message && (
                  <div style={{ fontSize: 12, color: "var(--color-text-2)", marginTop: 4 }}>
                    {typeof result.message === "string" ? result.message : JSON.stringify(result.message)}
                  </div>
                )}
                {(result.rows_rejected ?? 0) > 0 && (
                  <div style={{ fontSize: 12, color: "var(--color-text-3)", marginTop: 4 }}>
                    {result.rows_rejected} rows skipped — invalid or missing required fields
                  </div>
                )}
                {result.status === "success" && (
                  <div style={{ fontSize: 12, color: "#22C55E", marginTop: 8 }}>
                    Redirecting to dashboard…
                  </div>
                )}
              </div>
            )}

            {/* Upload button */}
            {file && isActive && (
              <button
                id="upload-submit-btn"
                onClick={handleUpload}
                disabled={!!validationError}
                style={{
                  marginTop: 20,
                  width: "100%",
                  background: validationError ? "var(--color-surface-2)" : "var(--color-accent)",
                  color: validationError ? "var(--color-text-3)" : "#0A0A0A",
                  border: missingColumns.length > 0 ? "1px solid #f59e0b" : "none",
                  borderRadius: 4,
                  padding: "10px 16px",
                  fontWeight: 600,
                  fontSize: 13,
                  fontFamily: "var(--font-sans)",
                  cursor: validationError ? "not-allowed" : "pointer",
                  transition: `opacity 120ms ${EASE}`,
                  opacity: validationError ? 0.6 : 1,
                }}
                onMouseEnter={e => !validationError && (e.currentTarget.style.opacity = "0.88")}
                onMouseLeave={e => !validationError && (e.currentTarget.style.opacity = "1")}
              >
                {missingColumns.length > 0 ? "Upload with Missing Columns" : "Upload & Analyze"}
              </button>
            )}

            {/* Format guide */}
            <div style={{
              marginTop: 24, padding: "14px 16px",
              border: "1px solid var(--color-border)", borderRadius: 6,
            }}>
              <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "0.05em", color: "var(--color-text-3)", marginBottom: 12 }}>
                Expected Column Schema
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                <thead>
                  <tr>
                    {["Column", "Type", "Required", "Description"].map(h => (
                      <th key={h} style={{
                        textAlign: "left", padding: "6px 8px",
                        fontSize: 11, fontWeight: 500,
                        textTransform: "uppercase" as const, letterSpacing: "0.05em",
                        color: "var(--color-text-3)",
                        borderBottom: "1px solid var(--color-border)",
                      }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["supplier_id",  "string", "Yes", "Unique supplier identifier"],
                    ["shipment_date","date",   "Yes", "ISO 8601 or YYYY-MM-DD"],
                    ["delay_days",   "number", "Yes", "Integer days late (0 = on time)"],
                    ["cost",         "number", "Yes", "Shipment cost in local currency"],
                    ["sku",          "string", "No",  "Product SKU"],
                    ["region",       "string", "No",  "Geographic region"],
                    ["warehouse_id", "string", "No",  "Destination warehouse"],
                    ["quality_score","number", "No",  "0.0–1.0 quality rating"],
                  ].map(([col, type, req, desc]) => (
                    <tr key={col}
                      style={{ transition: `background 120ms ${EASE}` }}
                      onMouseEnter={e => (e.currentTarget.style.background = "var(--color-surface-2)")}
                      onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                    >
                      <td style={{ padding: "8px 8px", height: 36, color: "var(--color-text-1)", fontWeight: 500, borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>{col}</td>
                      <td style={{ padding: "8px 8px", height: 36, color: "var(--color-text-3)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>{type}</td>
                      <td style={{ padding: "8px 8px", height: 36, borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                        <span style={{
                          padding: "1px 6px", borderRadius: 999, fontSize: 10, fontWeight: 500,
                          background: req === "Yes" ? "rgba(232,255,71,0.08)" : "transparent",
                          color: req === "Yes" ? "var(--color-accent)" : "var(--color-text-3)",
                          border: req === "Yes" ? "1px solid rgba(232,255,71,0.2)" : "1px solid var(--color-border)",
                        }}>
                          {req}
                        </span>
                      </td>
                      <td style={{ padding: "8px 8px", height: 36, color: "var(--color-text-2)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>{desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
