"use client";

import { useMemo, useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { useApi } from "../../hooks/useApi";
import { NoData } from "../components/Cards/NoData";
import { Notice, PageHeader, Panel, Pill, Segmented } from "../components/ui/Primitives";

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

type TraceResponse = { total: number; traces: AgentTrace[] };

/* Module-level so its identity never changes between renders */
const EMPTY: TraceResponse = { total: 0, traces: [] };

type Filter = "all" | "errors";

const FILTERS: { value: Filter; label: string }[] = [
  { value: "all", label: "All steps" },
  { value: "errors", label: "Errors only" },
];

function Json({ title, value }: { title: string; value: unknown }) {
  return (
    <details className="disclosure">
      <summary>{title}</summary>
      <pre className="json-block">{JSON.stringify(value, null, 2)}</pre>
    </details>
  );
}

export default function AgentTracesPage() {
  const [filter, setFilter] = useState<Filter>("all");
  const { data, loading, error, retry } = useApi<TraceResponse>("/mitigation/traces?limit=100", { fallback: EMPTY });

  const traces = useMemo(() => data?.traces ?? [], [data]);
  const visible = useMemo(
    () => (filter === "errors" ? traces.filter((t) => t.error) : traces),
    [traces, filter]
  );
  const errorCount = useMemo(() => traces.filter((t) => t.error).length, [traces]);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div className="page-wrap">
            <PageHeader
              eyebrow="Operations"
              title="Agent traces"
              subtitle="Execution logs and tool calls for the mitigation agent"
              actions={<Segmented label="Trace filter" value={filter} onChange={(v) => setFilter(v as Filter)} options={FILTERS} />}
            />

            {error && (
              <div style={{ marginBottom: 24 }}>
                <Notice
                  tone="danger"
                  title="Could not load traces"
                  action={<button type="button" className="btn btn-secondary btn-sm" onClick={retry}>Retry</button>}
                >
                  The server did not respond. Check that the backend is running.
                </Notice>
              </div>
            )}

            {loading && traces.length === 0 ? (
              <div className="skeleton" style={{ height: 400, borderRadius: 14 }} />
            ) : visible.length === 0 ? (
              <Panel>
                <NoData
                  height={220}
                  msg={filter === "errors" ? "No failed steps in the latest traces." : "No agent traces found yet."}
                  actionText="Go to Command Center"
                  actionHref="/dashboard"
                />
              </Panel>
            ) : (
              <Panel
                title="Latest steps"
                flush
                action={
                  <span style={{ fontSize: 12, color: "var(--color-text-3)" }}>
                    {visible.length} shown · {errorCount} with errors
                  </span>
                }
              >
                <div className="t-wrap">
                  <table className="t t-loose">
                    <thead>
                      <tr>
                        <th style={{ width: "18%" }}>Time</th>
                        <th style={{ width: "16%" }}>Run / step</th>
                        <th style={{ width: "16%" }}>Node</th>
                        <th>Input and output</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visible.map((t, idx) => (
                        <tr key={t.id ?? idx}>
                          <td style={{ color: "var(--color-text-2)" }}>
                            {t.created_at ? new Date(t.created_at).toLocaleString() : "Unknown"}
                          </td>
                          <td>
                            <div className="mono" style={{ marginBottom: 6, fontSize: 11, color: "var(--color-text-2)" }}>
                              {t.run_id ? `${t.run_id.substring(0, 8)}…` : "none"}
                            </div>
                            <Pill>Step {t.step}</Pill>
                          </td>
                          <td>
                            <div style={{ fontWeight: 500, color: "var(--color-text-1)" }}>{t.node_name}</div>
                            <div style={{ marginTop: 4, fontSize: 11, color: "var(--color-text-3)" }}>{t.duration_ms} ms</div>
                          </td>
                          <td>
                            {t.error && (
                              <div style={{ marginBottom: 8 }}>
                                <Pill tone="danger">Error</Pill>
                                <div style={{ marginTop: 6, fontSize: 12, color: "var(--color-danger)", overflowWrap: "anywhere" }}>
                                  {t.error}
                                </div>
                              </div>
                            )}
                            <div style={{ display: "grid", gap: 8 }}>
                              <Json title="Input JSON" value={t.input} />
                              <Json title="Output JSON" value={t.output} />
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}