"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import { AnimatedSection } from "../components/Animated";
import {
  GitBranch, CheckCircle, XCircle, Clock, BarChart3, ArrowDown, ArrowUp, Shield,
} from "lucide-react";
import { apiFetchJSON, apiPostJSON } from "@/lib/api";
import { useToast } from "../components/ToastContext";

type PipelineRun = {
  id: number; name: string; status: string;
  rows_ingested: number; rows_accepted: number;
  quality_score: number | null; duration_ms: number | null;
  created_at: string | null;
};

type QualityCheck = {
  name: string; score: number; status: string;
};

export default function PipelinePage() {
  const { showToast } = useToast();
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [qualityReport, setQualityReport] = useState<any>(null);
  const [lineage, setLineage] = useState<any[]>([]);
  const [checking, setChecking] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setError(null);
    try {
      const [runsRes, lineageRes] = await Promise.all([
        apiFetchJSON<{ runs?: PipelineRun[] }>(`/pipeline/history`),
        apiFetchJSON<{ lineage?: any[] }>(`/pipeline/lineage`),
      ]);
      setRuns(runsRes.runs || []);
      setLineage(lineageRes.lineage || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load pipeline data";
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const runQualityCheck = async () => {
    setChecking(true);
    setError(null);
    try {
      setQualityReport(await apiPostJSON(`/pipeline/quality-check`, {}));
      showToast("Quality check completed.", "success");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Quality check failed";
      setError(message);
      showToast(message, "error");
    } finally {
      setChecking(false);
    }
  };

  const gradeColors: Record<string, string> = {
    A: "#22c55e", B: "#06b6d4", C: "#f59e0b", D: "#f97316", F: "#ef4444",
  };

  const statusIcons: Record<string, React.ReactNode> = {
    success: <CheckCircle size={14} color="#22c55e" />,
    failed: <XCircle size={14} color="#ef4444" />,
    running: <Clock size={14} color="#f59e0b" />,
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
        {error && (
          <div className="card" style={{ marginBottom: 20, padding: 16, color: "#ef4444", border: "1px solid rgba(239,68,68,0.35)" }}>
            {error}
          </div>
        )}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <GitBranch size={28} color="#a78bfa" />
              <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em" }}>Pipeline Monitor</h1>
            </div>
            <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
              Data quality, lineage tracking, and pipeline execution history
            </p>
          </div>
          <button
            onClick={runQualityCheck}
            disabled={checking}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 20px", background: checking ? "rgba(167,139,250,0.2)" : "linear-gradient(135deg, #a78bfa, #7c3aed)",
              border: "none", borderRadius: 10, color: "#fff", fontWeight: 700, fontSize: 13,
              cursor: checking ? "wait" : "pointer", boxShadow: "0 0 20px rgba(167,139,250,0.2)",
            }}
          >
            <Shield size={16} /> {checking ? "Analyzing..." : "Run Quality Check"}
          </button>
        </div>

        {/* Quality Report */}
        {qualityReport && !qualityReport.error && (
          <div className="card" style={{ marginBottom: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700 }}>Data Quality Report</h2>
              <div style={{
                fontSize: 36, fontWeight: 900, color: gradeColors[qualityReport.grade] || "#64748b",
                lineHeight: 1,
              }}>
                {qualityReport.grade}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
              {qualityReport.checks?.map((check: QualityCheck) => (
                <div key={check.name} style={{
                  background: "rgba(0,0,0,0.2)", borderRadius: 10, padding: 14,
                  borderLeft: `3px solid ${check.status === "pass" ? "#22c55e" : check.status === "warn" ? "#f59e0b" : "#ef4444"}`,
                }}>
                  <div style={{ fontSize: 13, fontWeight: 700 }}>{check.name}</div>
                  <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4, color: check.status === "pass" ? "#22c55e" : check.status === "warn" ? "#f59e0b" : "#ef4444" }}>
                    {(check.score * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>{check.status}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pipeline History */}
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Pipeline Execution History</h2>
        {runs.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
            No pipeline runs recorded yet. Upload data to trigger the first pipeline.
          </div>
        ) : (
          <div style={{ display: "grid", gap: 8, marginBottom: 28 }}>
            {runs.map(r => (
              <div key={r.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 20px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  {statusIcons[r.status] || <Clock size={14} />}
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700 }}>{r.name}</div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{r.created_at || "Unknown"}</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{r.rows_ingested} <ArrowDown size={10} style={{ display: "inline" }} /></div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Ingested</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "#22c55e" }}>{r.rows_accepted} <ArrowUp size={10} style={{ display: "inline" }} /></div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Accepted</div>
                  </div>
                  {r.quality_score != null && (
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: r.quality_score > 0.8 ? "#22c55e" : "#f59e0b" }}>
                        {(r.quality_score * 100).toFixed(0)}%
                      </div>
                      <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Quality</div>
                    </div>
                  )}
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{r.duration_ms}ms</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Data Lineage */}
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Data Lineage</h2>
        {lineage.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
            No lineage records yet. Data is tracked automatically on ingestion.
          </div>
        ) : (
          <div className="card" style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Source Column</th>
                  <th>→</th>
                  <th>Target Table</th>
                  <th>Target Column</th>
                  <th>Transform</th>
                  <th>Hash</th>
                </tr>
              </thead>
              <tbody>
                {lineage.map((r: any) => (
                  <tr key={r.id}>
                    <td>{r.source}</td>
                    <td><code style={{ fontSize: 11, background: "rgba(6,182,212,0.1)", padding: "2px 6px", borderRadius: 4 }}>{r.source_col}</code></td>
                    <td><ArrowDown size={12} /></td>
                    <td>{r.target_table}</td>
                    <td><code style={{ fontSize: 11, background: "rgba(167,139,250,0.1)", padding: "2px 6px", borderRadius: 4 }}>{r.target_col}</code></td>
                    <td>{r.transform}</td>
                    <td style={{ fontSize: 10, color: "var(--text-muted)" }}>{r.hash}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
      </div>
    </div>
  );
}
