"use client";

import React from "react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { useApi } from "../../hooks/useApi";
import { NoData } from "../components/Cards/NoData";

type AgentTrace = {
  id: number;
  run_id: string;
  step: number;
  node_name: string;
  input: any;
  output: any;
  duration_ms: number;
  error: string | null;
  created_at: string;
};

export default function AgentTracesPage() {
  const { data, loading } = useApi<{ total: number; traces: AgentTrace[] }>("/mitigation/traces?limit=100", { fallback: { total: 0, traces: [] } });
  
  const traces = data?.traces || [];

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div style={{ marginBottom: 24, borderBottom: "1px solid var(--color-border)", paddingBottom: 16 }}>
            <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)" }}>Agent Traces</h1>
            <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 4 }}>
              Execution logs and tool calls for the mitigation agent
            </p>
          </div>

          {loading ? (
            <div className="skeleton" style={{ height: 400, width: "100%", borderRadius: 6 }} />
          ) : traces.length === 0 ? (
            <NoData msg="No agent traces found." actionText="Go to Dashboard" actionHref="/dashboard" />
          ) : (
            <div style={{
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              borderRadius: 6,
              overflow: "hidden"
            }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                <thead>
                  <tr style={{ background: "var(--color-surface-2)" }}>
                    <th style={{ textAlign: "left", padding: "10px 16px", borderBottom: "1px solid var(--color-border)", color: "var(--color-text-3)", fontWeight: 500, width: "15%" }}>TIMESTAMP</th>
                    <th style={{ textAlign: "left", padding: "10px 16px", borderBottom: "1px solid var(--color-border)", color: "var(--color-text-3)", fontWeight: 500, width: "15%" }}>RUN ID / STEP</th>
                    <th style={{ textAlign: "left", padding: "10px 16px", borderBottom: "1px solid var(--color-border)", color: "var(--color-text-3)", fontWeight: 500, width: "15%" }}>NODE</th>
                    <th style={{ textAlign: "left", padding: "10px 16px", borderBottom: "1px solid var(--color-border)", color: "var(--color-text-3)", fontWeight: 500 }}>I/O SUMMARY</th>
                  </tr>
                </thead>
                <tbody>
                  {traces.map((t, idx) => (
                    <tr key={t.id || idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td style={{ padding: "12px 16px", color: "var(--color-text-2)", verticalAlign: "top" }}>
                        {t.created_at ? new Date(t.created_at).toLocaleString() : "Unknown"}
                      </td>
                      <td style={{ padding: "12px 16px", color: "var(--color-text-2)", verticalAlign: "top" }}>
                        <div style={{ fontFamily: "monospace", fontSize: 11, marginBottom: 4 }}>
                          {t.run_id ? t.run_id.substring(0, 8) + "..." : "none"}
                        </div>
                        <span style={{ background: "var(--color-surface-2)", padding: "2px 6px", borderRadius: 4, fontSize: 10 }}>Step {t.step}</span>
                      </td>
                      <td style={{ padding: "12px 16px", color: "var(--color-text-1)", fontWeight: 500, verticalAlign: "top" }}>
                        {t.node_name}
                        <div style={{ fontSize: 10, color: "var(--color-text-3)", marginTop: 4, fontWeight: "normal" }}>
                          {t.duration_ms} ms
                        </div>
                      </td>
                      <td style={{ padding: "12px 16px", verticalAlign: "top" }}>
                        {t.error ? (
                          <div style={{ color: "#FF4444", fontWeight: 500, marginBottom: 8 }}>Error: {t.error}</div>
                        ) : null}
                        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                          <details style={{ background: "var(--color-surface-2)", padding: "6px 10px", borderRadius: 4 }}>
                            <summary style={{ cursor: "pointer", color: "var(--color-text-2)", fontWeight: 500, userSelect: "none" }}>Input JSON</summary>
                            <pre style={{ margin: 0, marginTop: 8, overflowX: "auto", fontSize: 11, color: "var(--color-text-1)", padding: 8, background: "rgba(0,0,0,0.2)", borderRadius: 4 }}>
                              {JSON.stringify(t.input, null, 2)}
                            </pre>
                          </details>
                          <details style={{ background: "var(--color-surface-2)", padding: "6px 10px", borderRadius: 4 }}>
                            <summary style={{ cursor: "pointer", color: "var(--color-text-2)", fontWeight: 500, userSelect: "none" }}>Output JSON</summary>
                            <pre style={{ margin: 0, marginTop: 8, overflowX: "auto", fontSize: 11, color: "var(--color-text-1)", padding: 8, background: "rgba(0,0,0,0.2)", borderRadius: 4 }}>
                              {JSON.stringify(t.output, null, 2)}
                            </pre>
                          </details>
                        </div>
                      </td>
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
