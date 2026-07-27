"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { AnimatedSection, StaggerGrid, StaggerItem } from "../components/Animated";
import {
  Dna, Zap, Target, Shield, ArrowRight, AlertTriangle, Search, History
} from "lucide-react";
import { apiFetchJSON, apiPostJSON } from "@/lib/api";
import { useToast } from "../components/feedback/ToastContext";

type CausalChain = {
  node: string; name: string; type: string;
  causal_strength: number; mechanism: string;
  causal_chain?: string;
  dependency_path?: string;
  estimated_dollar_impact: number;
};

type FragilityNode = {
  id: string; name: string; type: string;
  fragility_score: number; classification: string;
};

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
      const message = err instanceof Error ? err.message : "Unable to build causal graph";
      setError(message);
      showToast(message, "error");
    } finally {
      setBuilding(false);
    }
  };

  const runIntervention = async () => {
    const target = interventionTarget.trim();
    if (!target) {
      showToast("Enter a supplier name, node ID, or region first.", "warning");
      return;
    }
    setQuerying(true);
    setError(null);
    try {
      setInterventionResult(await apiFetchJSON(`/causal/intervene?target=${encodeURIComponent(target)}&action=remove`));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Intervention query failed";
      setError(message);
      showToast(message, "error");
    } finally {
      setQuerying(false);
    }
  };

  const classColors: Record<string, string> = {
    EXTREMELY_FRAGILE: "#ef4444",
    FRAGILE: "#f97316",
    ROBUST: "#22c55e",
    ANTIFRAGILE: "#06b6d4",
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Dna size={28} color="#06b6d4" />
              <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em" }}>Causal Supply Chain Genome</h1>
            </div>
            <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
              Downstream risk propagation — simulate disruptions and trace dependency exposure
            </p>
          </div>
          <button
            onClick={buildGenome}
            disabled={building}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "12px 24px",
              background: building ? "rgba(6, 182, 212, 0.2)" : "linear-gradient(135deg, #06b6d4, #0891b2)",
              border: "none", borderRadius: 10, color: "#fff", fontWeight: 700, fontSize: 13,
              cursor: building ? "wait" : "pointer",
              boxShadow: "0 0 25px rgba(6, 182, 212, 0.2)",
              textTransform: "uppercase", letterSpacing: "0.05em",
            }}
          >
            <Dna size={16} /> {building ? "Building graph..." : "Build Risk Graph"}
          </button>
        </div>

        {error && (
          <div className="card" style={{ marginBottom: 20, padding: 16, color: "#ef4444", border: "1px solid rgba(239,68,68,0.35)" }}>
            {error}
          </div>
        )}

        {/* Scenario Run History */}
        <div className="card" style={{ marginBottom: 28, border: "1px solid rgba(139, 92, 246, 0.15)", background: "rgba(139, 92, 246, 0.02)" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <History size={20} color="#8b5cf6" />
              <h2 style={{ fontSize: 16, fontWeight: 700 }}>Failure Scenario History</h2>
              <span style={{ fontSize: 10, color: "#8b5cf6", background: "rgba(139,92,246,0.1)", padding: "2px 8px", borderRadius: 20 }}>WHAT-IF ANALYSIS</span>
            </div>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", marginLeft: 20 }}>
              Historical runs of graph failure simulations triggered from the Graph UI.
            </p>
          </div>

          {loadingRuns ? (
            <div style={{ fontSize: 13, color: "var(--text-muted)", padding: 20, textAlign: "center" }}>Loading scenario history...</div>
          ) : scenarioRuns.length > 0 ? (
            <div style={{ overflowX: "auto" }}>
                <table className="data-table">
                <thead>
                    <tr>
                    <th>Time</th>
                    <th>Failed Node</th>
                    <th>Total Affected</th>
                    <th>Risk Level</th>
                    <th>Newly Critical</th>
                    <th>Unreachable SKUs</th>
                    </tr>
                </thead>
                <tbody>
                    {scenarioRuns.map(run => (
                    <tr key={run.id}>
                        <td style={{ color: "var(--text-muted)", fontSize: 12 }}>{new Date(run.created_at).toLocaleString()}</td>
                        <td><span style={{ fontWeight: 500 }}>{run.node_name}</span> <span style={{ color: "var(--text-muted)", fontSize: 11 }}>({run.node_type})</span></td>
                        <td>{run.total_affected}</td>
                        <td>
                        <span className={`risk-badge risk-${run.risk_assessment === 'catastrophic' ? 'critical' : run.risk_assessment === 'severe' ? 'elevated' : 'stable'}`}>
                            {run.risk_assessment || "unknown"}
                        </span>
                        </td>
                        <td>{run.newly_critical_nodes?.length || 0}</td>
                        <td>{run.unreachable_skus?.length || 0}</td>
                    </tr>
                    ))}
                </tbody>
                </table>
            </div>
          ) : (
            <div style={{ padding: 20, textAlign: "center", color: "var(--text-muted)", fontSize: 13, background: "rgba(0,0,0,0.2)", borderRadius: 8 }}>
              No failure scenarios have been run yet. Go to the Graph view and click "Simulate Failure" on a node.
            </div>
          )}
        </div>

        {/* Build Result Stats */}
        {buildResult && !buildResult.error && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
            {[
              { label: "Graph Nodes", value: buildResult.total_causal_nodes ?? buildResult.total_nodes, color: "#06b6d4" },
              { label: "Risk Edges", value: buildResult.total_causal_edges ?? buildResult.total_edges, color: "#a78bfa" },
              { label: "Root Sources", value: buildResult.root_causes?.length ?? buildResult.root_nodes?.length ?? 0, color: "#ef4444" },
              { label: "Leaf Nodes", value: buildResult.terminal_effects?.length ?? buildResult.leaf_nodes?.length ?? 0, color: "#f59e0b" },
            ].map(stat => (
              <div key={stat.label} className="card" style={{ textAlign: "center", padding: 20 }}>
                <div style={{ fontSize: 32, fontWeight: 800, color: stat.color }}>{stat.value}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em" }}>{stat.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Interventional Query — The X-Factor UI */}
        <div className="card" style={{ marginBottom: 28, border: "1px solid rgba(6, 182, 212, 0.15)", background: "rgba(6, 182, 212, 0.02)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <Target size={20} color="#06b6d4" />
            <h2 style={{ fontSize: 16, fontWeight: 700 }}>Interventional Query</h2>
            <span style={{ fontSize: 10, color: "#06b6d4", background: "rgba(6,182,212,0.1)", padding: "2px 8px", borderRadius: 20 }}>RISK PROPAGATION</span>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
            Ask: &quot;What would happen if we remove this supplier?&quot; — Get the full causal chain with dollar impact.
          </p>

          <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
            <div style={{ position: "relative", flex: 1 }}>
              <Search size={16} style={{ position: "absolute", left: 12, top: 12, color: "#64748b" }} />
              <input
                value={interventionTarget}
                onChange={e => setInterventionTarget(e.target.value)}
                placeholder="Enter supplier name, node ID, or region..."
                style={{
                  width: "100%", padding: "10px 14px 10px 36px",
                  background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-subtle)",
                  borderRadius: 10, color: "#f1f5f9", fontSize: 13, outline: "none",
                  boxSizing: "border-box",
                }}
              />
            </div>
            <button
              onClick={runIntervention}
              disabled={querying}
              style={{
                padding: "10px 20px", background: "#f59e0b", color: "#000",
                border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer",
                display: "flex", alignItems: "center", gap: 6, fontSize: 13,
              }}
            >
              <Zap size={14} /> {querying ? "Querying..." : "Run Intervention"}
            </button>
          </div>

          {/* Intervention Results */}
          {interventionResult && !interventionResult.error && (
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 16 }}>
                <div style={{ background: "rgba(239,68,68,0.08)", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 24, fontWeight: 800, color: "#ef4444" }}>{interventionResult.total_downstream_affected}</div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>Downstream Affected</div>
                </div>
                <div style={{ background: "rgba(245,158,11,0.08)", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 20, fontWeight: 800, color: "#f59e0b" }}>{interventionResult.total_estimated_impact}</div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>Est. Dollar Impact</div>
                </div>
                <div style={{ background: "rgba(34,197,94,0.08)", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 20, fontWeight: 800, color: "#22c55e" }}>{interventionResult.risk_reduction_if_mitigated}</div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>Risk Reduction</div>
                </div>
              </div>

              {/* Causal Chains */}
              <h3 style={{ fontSize: 13, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 10 }}>Causal Propagation Chains</h3>
              <div style={{ display: "grid", gap: 8 }}>
                {interventionResult.causal_chains?.slice(0, 8).map((chain: CausalChain, i: number) => (
                  <div key={i} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "10px 14px", background: "rgba(0,0,0,0.2)", borderRadius: 8,
                    border: "1px solid var(--border-subtle)",
                  }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>{chain.name}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{chain.mechanism}</div>
                      <div style={{ fontSize: 10, color: "#06b6d4", marginTop: 2 }}>
                        {chain.dependency_path ?? chain.causal_chain}
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: chain.causal_strength > 0.5 ? "#ef4444" : "#f59e0b" }}>
                          {(chain.causal_strength * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Strength</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 12, fontWeight: 700 }}>${chain.estimated_dollar_impact?.toLocaleString()}</div>
                        <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Impact</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {interventionResult?.error && (
            <div style={{ padding: 14, background: "rgba(239,68,68,0.1)", borderRadius: 8, color: "#ef4444", fontSize: 13 }}>
              {interventionResult.error}
            </div>
          )}
        </div>

        {/* Fragility Report — Taleb-Inspired */}
        {fragility && !fragility.error && (
          <div className="card" style={{ border: "1px solid rgba(236, 72, 153, 0.15)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <Shield size={20} color="#ec4899" />
              <h2 style={{ fontSize: 16, fontWeight: 700 }}>Fragility Report</h2>
              <span style={{ fontSize: 10, color: "#ec4899", background: "rgba(236,72,153,0.1)", padding: "2px 8px", borderRadius: 20 }}>TALEB FRAMEWORK</span>
            </div>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
              {[
                { label: "Fragile", value: fragility.fragile_count, color: "#ef4444" },
                { label: "Robust", value: fragility.robust_count, color: "#22c55e" },
                { label: "Antifragile", value: fragility.antifragile_count, color: "#06b6d4" },
                { label: "System Index", value: fragility.system_fragility_index?.toFixed(2), color: "#f59e0b" },
              ].map(s => (
                <div key={s.label} style={{ background: "rgba(0,0,0,0.2)", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>{s.label}</div>
                </div>
              ))}
            </div>

            <h3 style={{ fontSize: 13, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 10 }}>Most Fragile Nodes</h3>
            <div style={{ display: "grid", gap: 6 }}>
              {fragility.most_fragile?.slice(0, 6).map((n: FragilityNode) => (
                <div key={n.id} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "8px 14px", background: "rgba(0,0,0,0.15)", borderRadius: 8,
                }}>
                  <div>
                    <span style={{ fontSize: 13, fontWeight: 600 }}>{n.name}</span>
                    <span style={{ fontSize: 10, color: "var(--text-muted)", marginLeft: 8 }}>{n.type}</span>
                  </div>
                  <span style={{
                    fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 20,
                    background: `${classColors[n.classification] || "#64748b"}20`,
                    color: classColors[n.classification] || "#64748b",
                  }}>
                    {n.classification} ({n.fragility_score})
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {!buildResult && (
          <div className="card" style={{ textAlign: "center", padding: 60, color: "var(--text-muted)" }}>
            <Dna size={48} color="#1e293b" style={{ marginBottom: 16 }} />
            <p style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Risk Graph Not Built Yet</p>
            <p style={{ fontSize: 13 }}>Upload supply chain data, then click &quot;Build Risk Graph&quot; to map downstream exposure.</p>
          </div>
        )}
      </main>
      </div>
    </div>
  );
}
