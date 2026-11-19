"use client";

import { FormEvent, useEffect, useState } from "react";
import { Search } from "lucide-react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { KpiCard } from "../components/Cards/KpiCard";
import { NoData } from "../components/Cards/NoData";
import { useToast } from "../components/feedback/ToastContext";
import { Notice, PageHeader, Panel, Pill, type Tone } from "../components/ui/Primitives";
import { apiFetchJSON, apiPostJSON } from "@/lib/api";
import { formatNumber } from "@/lib/ui";

type PropagationChain = {
  node: string;
  name: string;
  type: string;
  propagation_strength?: number;
  causal_strength?: number;
  mechanism: string;
  causal_chain?: string;
  dependency_path?: string;
  estimated_dollar_impact: number;
};

type FragilityNode = {
  id: string;
  name: string;
  type: string;
  fragility_score: number;
  classification: string;
};

const CLASS_TONE: Record<string, Tone> = {
  EXTREMELY_FRAGILE: "danger",
  FRAGILE: "warn",
  ROBUST: "success",
  ANTIFRAGILE: "info",
};

/* The backend reports impact in dollars; strings are passed through untouched */
const money = (v: unknown) =>
  typeof v === "number" ? `$${v.toLocaleString("en-US")}` : v == null ? "—" : String(v);

const runTone = (assessment?: string) =>
  assessment === "catastrophic" ? "critical" : assessment === "severe" ? "elevated" : "stable";

export default function CausalPage() {
  const { showToast } = useToast();
  const [buildResult, setBuildResult] = useState<any>(null);
  const [interventionTarget, setInterventionTarget] = useState("");
  const [interventionResult, setInterventionResult] = useState<any>(null);
  const [fragility, setFragility] = useState<any>(null);
  const [building, setBuilding] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scenarioRuns, setScenarioRuns] = useState<any[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(true);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const res = await apiFetchJSON(`/graph/scenario-runs`);
        setScenarioRuns((res as any).runs || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingRuns(false);
      }
    };
    fetchRuns();
  }, []);

  const buildGenome = async () => {
    setBuilding(true);
    setError(null);
    try {
      const result = await apiPostJSON(`/causal/build`, {});
      setBuildResult(result);
      const frag = await apiFetchJSON(`/causal/fragility`);
      setFragility(frag);
    } catch (err) {
      console.error(err);
      setError("The risk graph could not be built. Check that data has been uploaded and the server is running, then try again.");
      showToast("Could not build the risk graph.", "error");
    } finally {
      setBuilding(false);
    }
  };

  const runIntervention = async (e?: FormEvent) => {
    e?.preventDefault();
    const target = interventionTarget.trim();
    if (!target) {
      showToast("Enter a supplier name, node ID, or region first.", "warning");
      return;
    }
    setQuerying(true);
    setError(null);
    try {
      setInterventionResult(
        await apiFetchJSON(`/causal/intervene?target=${encodeURIComponent(target)}&action=remove`)
      );
    } catch (err) {
      console.error(err);
      setError("The disruption query failed. Check the target name and try again.");
      showToast("The disruption query failed.", "error");
    } finally {
      setQuerying(false);
    }
  };

  const chains: PropagationChain[] = interventionResult?.causal_chains ?? [];

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div className="page-wrap">
            <PageHeader
              eyebrow="Intelligence"
              title="Risk propagation"
              subtitle="Simulate disruptions and trace downstream dependency exposure"
              actions={
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={buildGenome}
                  disabled={building}
                >
                  {building ? "Building graph…" : "Build risk graph"}
                </button>
              }
            />

            {error && (
              <div style={{ marginBottom: 24 }}>
                <Notice tone="danger" title="Something went wrong">
                  {error}
                </Notice>
              </div>
            )}

            {buildResult && !buildResult.error && (
              <div className="kpi-grid">
                <KpiCard label="Graph nodes" value={buildResult.total_causal_nodes ?? buildResult.total_nodes ?? 0} />
                <KpiCard label="Risk edges" value={buildResult.total_causal_edges ?? buildResult.total_edges ?? 0} />
                <KpiCard label="Root sources" value={buildResult.root_causes?.length ?? buildResult.root_nodes?.length ?? 0} />
                <KpiCard label="Leaf nodes" value={buildResult.terminal_effects?.length ?? buildResult.leaf_nodes?.length ?? 0} />
              </div>
            )}

            <div className="stack">
              {/* Disruption query */}
              <Panel title="Disruption query">
                <p style={{ marginBottom: 16, fontSize: 13, color: "var(--color-text-2)" }}>
                  Ask what happens if a supplier, node, or region is removed, and trace the downstream exposure.
                </p>

                <form onSubmit={runIntervention} className="toolbar" style={{ flexWrap: "nowrap" }}>
                  <div style={{ position: "relative", flex: 1, minWidth: 0 }}>
                    <Search
                      size={15}
                      aria-hidden="true"
                      style={{ position: "absolute", left: 14, top: 13, color: "var(--color-text-3)" }}
                    />
                    <input
                      className="input"
                      aria-label="Disruption target"
                      value={interventionTarget}
                      onChange={(e) => setInterventionTarget(e.target.value)}
                      placeholder="Supplier name, node ID, or region"
                      style={{ paddingLeft: 38 }}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" disabled={querying}>
                    {querying ? "Running…" : "Run intervention"}
                  </button>
                </form>

                {interventionResult && !interventionResult.error && (
                  <div style={{ marginTop: 20 }}>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
                      <div className="stat-tile">
                        <div className="v" style={{ color: "var(--color-danger)" }}>
                          {interventionResult.total_downstream_affected ?? "—"}
                        </div>
                        <div className="l">Downstream affected</div>
                      </div>
                      <div className="stat-tile">
                        <div className="v" style={{ color: "var(--color-warn)" }}>
                          {money(interventionResult.total_estimated_impact)}
                        </div>
                        <div className="l">Est. dollar impact</div>
                      </div>
                      <div className="stat-tile">
                        <div className="v" style={{ color: "var(--color-ok)" }}>
                          {interventionResult.risk_reduction_if_mitigated ?? "—"}
                        </div>
                        <div className="l">Risk reduction</div>
                      </div>
                    </div>

                    <h3 className="text-micro" style={{ margin: "24px 0 8px" }}>Risk propagation chains</h3>
                    {chains.length > 0 ? (
                      <div>
                        {chains.slice(0, 8).map((chain, i) => {
                          const strength = chain.propagation_strength ?? chain.causal_strength ?? 0;
                          return (
                            <div
                              key={i}
                              className="list-row"
                              style={{ alignItems: "flex-start", borderBottom: "1px solid var(--color-border)", borderRadius: 0 }}
                            >
                              <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>{chain.name}</div>
                                <div style={{ marginTop: 2, fontSize: 12, color: "var(--color-text-2)" }}>{chain.mechanism}</div>
                                <div className="mono" style={{ marginTop: 4, fontSize: 11, color: "var(--color-text-3)", overflowWrap: "anywhere" }}>
                                  {chain.dependency_path ?? chain.causal_chain}
                                </div>
                              </div>
                              <div style={{ display: "flex", gap: 24, flexShrink: 0, textAlign: "right" }}>
                                <div>
                                  <div style={{ fontSize: 13, fontWeight: 500, color: strength > 0.5 ? "var(--color-danger)" : "var(--color-warn)" }}>
                                    {(strength * 100).toFixed(0)}%
                                  </div>
                                  <div className="text-micro">Strength</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                                    {money(chain.estimated_dollar_impact)}
                                  </div>
                                  <div className="text-micro">Impact</div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <NoData height={100} msg="No propagation chains were returned for this target." />
                    )}
                  </div>
                )}

                {interventionResult?.error && (
                  <div style={{ marginTop: 16 }}>
                    <Notice tone="danger" title="No result">
                      {String(interventionResult.error)}
                    </Notice>
                  </div>
                )}
              </Panel>

              {/* Fragility report */}
              {fragility && !fragility.error && (
                <Panel title="Fragility report" delay={0.05}>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
                    <div className="stat-tile"><div className="v" style={{ color: "var(--color-danger)" }}>{fragility.fragile_count ?? 0}</div><div className="l">Fragile</div></div>
                    <div className="stat-tile"><div className="v" style={{ color: "var(--color-ok)" }}>{fragility.robust_count ?? 0}</div><div className="l">Robust</div></div>
                    <div className="stat-tile"><div className="v" style={{ color: "#7fb0ff" }}>{fragility.antifragile_count ?? 0}</div><div className="l">Antifragile</div></div>
                    <div className="stat-tile"><div className="v">{fragility.system_fragility_index?.toFixed(2) ?? "—"}</div><div className="l">System index</div></div>
                  </div>

                  <h3 className="text-micro" style={{ margin: "24px 0 8px" }}>Most fragile nodes</h3>
                  <div>
                    {(fragility.most_fragile as FragilityNode[] | undefined)?.slice(0, 6).map((n) => (
                      <div key={n.id} className="list-row">
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>{n.name}</span>
                          <span style={{ marginLeft: 8, fontSize: 11, color: "var(--color-text-3)" }}>{n.type}</span>
                        </div>
                        <Pill tone={CLASS_TONE[n.classification] ?? "neutral"}>
                          {n.classification.replace(/_/g, " ").toLowerCase()} · {n.fragility_score}
                        </Pill>
                      </div>
                    ))}
                  </div>
                </Panel>
              )}

              {!buildResult && !building && (
                <Panel>
                  <NoData
                    height={220}
                    msg="The risk graph has not been built yet. Upload supply chain data, then choose Build risk graph to map downstream exposure."
                  />
                </Panel>
              )}

              {/* Scenario history */}
              <Panel title="Failure scenario history" flush delay={0.05}>
                {loadingRuns ? (
                  <div style={{ padding: 20, display: "grid", gap: 10 }}>
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={i} className="skeleton" style={{ height: 34 }} />
                    ))}
                  </div>
                ) : scenarioRuns.length > 0 ? (
                  <div className="t-wrap">
                    <table className="t">
                      <thead>
                        <tr>
                          <th>Time</th>
                          <th>Failed node</th>
                          <th className="num">Total affected</th>
                          <th>Risk level</th>
                          <th className="num">Newly critical</th>
                          <th className="num">Unreachable SKUs</th>
                        </tr>
                      </thead>
                      <tbody>
                        {scenarioRuns.map((run) => (
                          <tr key={run.id}>
                            <td style={{ color: "var(--color-text-2)" }}>{new Date(run.created_at).toLocaleString()}</td>
                            <td>
                              {run.node_name}
                              <span style={{ marginLeft: 8, fontSize: 11, color: "var(--color-text-3)" }}>{run.node_type}</span>
                            </td>
                            <td className="num">{formatNumber(run.total_affected)}</td>
                            <td>
                              <span className={`risk-badge risk-${runTone(run.risk_assessment)}`}>
                                {run.risk_assessment || "unknown"}
                              </span>
                            </td>
                            <td className="num">{run.newly_critical_nodes?.length || 0}</td>
                            <td className="num">{run.unreachable_skus?.length || 0}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ padding: 20 }}>
                    <NoData
                      height={120}
                      msg="No failure scenarios have been run yet. Open the Graph Network and choose Simulate failure on a node."
                      actionText="Open graph network"
                      actionHref="/graph"
                    />
                  </div>
                )}
              </Panel>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}