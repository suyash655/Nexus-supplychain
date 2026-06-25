"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";

import { SafeMarkdown } from "../components/SafeMarkdown";
import { useToast } from "../components/ToastContext";
import {
  DEMO_SUMMARY, DEMO_SUPPLIERS, DEMO_EXECUTIVE, DEMO_ANOMALIES,
  DEMO_TIME_SERIES, DEMO_RESILIENCE,
} from "../demo-data";
import dynamic from "next/dynamic";
import { useApi } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";
import { TierBadge } from "../components/Cards/TierBadge";
import { SectionLabel } from "../components/Cards/SectionLabel";
import { NoData } from "../components/Cards/NoData";

const SynBarChart = dynamic(() => import("../components/Charts").then(m => ({ default: m.SynBarChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynLineChart = dynamic(() => import("../components/Charts").then(m => ({ default: m.SynLineChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynPieChart = dynamic(() => import("../components/Charts").then(m => ({ default: m.SynPieChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynAreaChart = dynamic(() => import("../components/Charts").then(m => ({ default: m.SynAreaChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });

const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";

/* ── Types ── */
type Summary = {
  total_records: number;
  unique_suppliers: number;
  unique_skus: number;
  unique_regions: number;
  avg_delay_days: number;
  max_delay_days: number;
  total_cost: number;
  delayed_shipments_pct: number;
  avg_quality: number;
};

type RiskSupplier = {
  supplier: string;
  risk_score: number;
  tier: string;
  total_shipments: number;
  avg_delay: number;
  total_cost: number;
};

type Recommendation = {
  priority: string;
  action: string;
  detail: string;
  estimated_impact: string;
};

type ExecutiveSummary = {
  overall_risk_level: string;
  risk_color: string;
  narrative: string;
  recommendations: Recommendation[];
};

type AnomalyItem = {
  type: string;
  severity: string;
  supplier: string;
  risk_score: number;
};

type AnomalyData = {
  anomaly_count: number;
  methods_used: string[];
  anomalies: AnomalyItem[];
};

/* ── Palette-safe risk colour ── */
function riskLevelColor(level: string): string {
  const l = level?.toUpperCase();
  if (l === "CRITICAL" || l === "HIGH") return "#FF4444";
  if (l === "ELEVATED" || l === "MEDIUM") return "#F59E0B";
  return "#22C55E";
}


/* ── Page ── */
export default function DashboardPage() {
  const router     = useRouter();
  const { showToast } = useToast();

  const { data: summary, loading: l1 } = useApi<Summary | null>("/analytics/summary", { fallback: DEMO_SUMMARY });
  const { data: suppliers, loading: l2 } = useApi<RiskSupplier[]>("/analytics/suppliers", { fallback: DEMO_SUPPLIERS });
  const { data: executive, loading: l3 } = useApi<ExecutiveSummary | null>("/copilot/summary", { fallback: DEMO_EXECUTIVE });
  const { data: anomalies, loading: l4 } = useApi<AnomalyData | null>("/ml/anomalies", { fallback: DEMO_ANOMALIES });
  const { data: timeSeries, loading: l5 } = useApi<any>("/analytics/time-series", { fallback: DEMO_TIME_SERIES });
  const { data: resilience, loading: l6 } = useApi<any>("/graph/resilience", { fallback: DEMO_RESILIENCE });

  const loading = l1 || l2 || l3 || l4 || l5 || l6;
  const isDemo = summary === DEMO_SUMMARY || suppliers === DEMO_SUPPLIERS;

  /* ── Derived data ── */
  const riskTiers = useMemo(() => ({
    critical: suppliers.filter(s => s.tier === "critical").length,
    elevated: suppliers.filter(s => s.tier === "elevated").length,
    stable:   suppliers.filter(s => s.tier === "stable").length,
  }), [suppliers]);

  const tierData = useMemo(() => [
    { name: "Critical", value: riskTiers.critical },
    { name: "Elevated", value: riskTiers.elevated },
    { name: "Stable",   value: riskTiers.stable   },
  ].filter(d => d.value > 0), [riskTiers]);

  const topRiskSuppliers = useMemo(() => suppliers
    .slice(0, 8)
    .map(s => ({
      name:       s.supplier.length > 12 ? s.supplier.slice(0, 12) + "…" : s.supplier,
      risk_score: s.risk_score,
    })), [suppliers]);

  const resilScore   = resilience?.network_resilience_score ?? 50;
  const execRiskCol  = executive ? riskLevelColor(executive.overall_risk_level) : "#888888";

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            {/* Static skeleton — no shimmer per spec */}
            <div className="kpi-grid">
              {[...Array(4)].map((_, i) => (
                <div key={i} style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20, height: 96 }} />
              ))}
            </div>
            <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, height: 300 }} />
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">

          {/* ══ LAYER A — Page Header ══ */}
          <div style={{
            display:        "flex",
            alignItems:     "flex-start",
            justifyContent: "space-between",
            paddingBottom:  16,
            marginBottom:   24,
            borderBottom:   "1px solid var(--color-border)",
          }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>
                Overview
              </div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                Command Center
              </h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>
                Real-time intelligence across your supply chain network
              </p>
            </div>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <button
                className="btn btn-secondary"
                onClick={() => router.push("/analytics")}
              >
                Deep Analytics
              </button>
              <button
                className="btn btn-primary"
                onClick={() => router.push("/upload")}
              >
                Upload Data
              </button>
            </div>
          </div>

          {/* Demo mode notice */}
          {isDemo && (
            <div style={{
              marginBottom: 24,
              padding:      "10px 16px",
              background:   "var(--color-surface)",
              border:       "1px solid var(--color-border)",
              borderRadius: 6,
              display:      "flex",
              alignItems:   "center",
              justifyContent: "space-between",
              gap: 12,
            }}>
              <div>
                <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                  Demo data
                </span>
                <span style={{ fontSize: 13, color: "var(--color-text-2)", marginLeft: 8 }}>
                  — Backend offline or no data uploaded yet.
                </span>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => router.push("/upload")}
              >
                Upload Data
              </button>
            </div>
          )}

          {/* ══ LAYER B — KPI Strip ══ */}
          <div className="kpi-grid">
            <KpiCard
              label="Total Records"
              value={summary?.total_records?.toLocaleString() ?? "0"}
              delta={`${summary?.unique_skus ?? 0} unique SKUs`}
              deltaDir="neutral"
            />
            <KpiCard
              label="Active Suppliers"
              value={summary?.unique_suppliers ?? 0}
              delta={riskTiers.critical > 0 ? `${riskTiers.critical} critical` : "All stable"}
              deltaDir={riskTiers.critical > 0 ? "down" : "up"}
            />
            <KpiCard
              label="Avg Delay"
              value={`${summary?.avg_delay_days?.toFixed(1) ?? "0.0"}d`}
              delta={`Max ${summary?.max_delay_days ?? 0}d recorded`}
              deltaDir={
                (summary?.avg_delay_days ?? 0) > 5 ? "down" :
                (summary?.avg_delay_days ?? 0) > 2 ? "neutral" : "up"
              }
            />
            <KpiCard
              label="Anomalies Detected"
              value={anomalies?.anomaly_count ?? 0}
              delta={anomalies?.methods_used?.join(", ") ?? "—"}
              deltaDir={anomalies?.anomaly_count ?? 0 > 0 ? "down" : "up"}
            />
          </div>

          {/* ══ LAYER C — 2-column content ══ */}
          <div className="dashboard-layout">

            {/* ── LEFT: primary data ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Supplier Risk Table */}
              <div style={{
                background:   "var(--color-surface)",
                border:       "1px solid var(--color-border)",
                borderRadius: 6,
                overflow:     "hidden",
              }}>
                <div style={{
                  padding:      "14px 20px",
                  borderBottom: "1px solid var(--color-border)",
                  display:      "flex",
                  alignItems:   "center",
                  justifyContent: "space-between",
                }}>
                  <SectionLabel>Supplier Risk Leaderboard</SectionLabel>
                  <button
                    className="btn-text"
                    onClick={() => router.push("/analytics")}
                  >
                    View all →
                  </button>
                </div>

                {suppliers.length > 0 ? (
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                    <thead>
                      <tr>
                        {["SUPPLIER", "RISK SCORE", "TIER", "AVG DELAY", "SHIPMENTS", "TOTAL COST"].map(h => (
                          <th key={h} style={{
                            textAlign: "left", padding: "10px 16px",
                            fontSize: 11, fontWeight: 500,
                            textTransform: "uppercase", letterSpacing: "0.05em",
                            color: "var(--color-text-3)",
                            borderBottom: "1px solid var(--color-border)",
                            background: "var(--color-surface)",
                          }}>
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {suppliers.slice(0, 10).map((s, i) => (
                        <tr
                          key={i}
                          className="supplier-row"
                          onClick={() => router.push("/analytics")}
                        >
                          <td className="supplier-cell-primary">
                            {s.supplier}
                          </td>
                          <td className="supplier-cell">
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <span style={{ fontWeight: 600, minWidth: 28, fontSize: 13, color: "var(--color-text-1)" }}>
                                {s.risk_score}
                              </span>
                              <div className="risk-bar-container">
                                <div className="risk-bar-fill" style={{
                                  width: `${s.risk_score}%`,
                                  background: s.risk_score >= 70 ? "#FF4444" : s.risk_score >= 40 ? "#F59E0B" : "#22C55E",
                                }} />
                              </div>
                            </div>
                          </td>
                          <td className="supplier-cell">
                            <TierBadge tier={s.tier} />
                          </td>
                          <td className="supplier-cell-primary">
                            {s.avg_delay}d
                          </td>
                          <td className="supplier-cell-secondary">
                            {s.total_shipments}
                          </td>
                          <td className="supplier-cell-secondary">
                            ₹{s.total_cost?.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div style={{ padding: 20 }}>
                    <NoData msg="No suppliers found." actionText="Upload Supplier Data" actionHref="/upload" />
                  </div>
                )}
              </div>

              {/* Trend charts */}
              <div className="trend-charts-grid">
                <div style={{
                  background: "var(--color-surface)", border: "1px solid var(--color-border)",
                  borderRadius: 6, padding: 20,
                }}>
                  <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-2)", marginBottom: 16 }}>
                    Delay Trend
                  </div>
                  {timeSeries?.delay_trend?.length > 0 ? (
                    <SynAreaChart
                      data={timeSeries.delay_trend}
                      dataKey="avg_delay"
                      xKey="period"
                      color="#F59E0B"
                      height={180}
                    />
                  ) : (
                    <NoData msg="No historical data available." actionText="Upload Shipments" actionHref="/upload" />
                  )}
                </div>

                <div style={{
                  background: "var(--color-surface)", border: "1px solid var(--color-border)",
                  borderRadius: 6, padding: 20,
                }}>
                  <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-2)", marginBottom: 16 }}>
                    Cost Trend
                  </div>
                  {timeSeries?.cost_trend?.length > 0 ? (
                    <SynAreaChart
                      data={timeSeries.cost_trend}
                      dataKey="total_cost"
                      xKey="period"
                      color="#888888"
                      height={180}
                    />
                  ) : (
                    <NoData msg="No cost data available." actionText="Upload Shipments" actionHref="/upload" />
                  )}
                </div>
              </div>

              {/* Supplier risk bar chart */}
              <div style={{
                background: "var(--color-surface)", border: "1px solid var(--color-border)",
                borderRadius: 6, padding: 20,
              }}>
                <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-2)", marginBottom: 16 }}>
                  Supplier Risk Scores (0–100)
                </div>
                {topRiskSuppliers.length > 0 ? (
                  <SynBarChart
                    data={topRiskSuppliers}
                    dataKey="risk_score"
                    nameKey="name"
                    color="#E8FF47"
                    height={220}
                  />
                ) : (
                  <NoData msg="No geographical data available." actionText="Upload Locations" actionHref="/upload" />
                )}
              </div>
            </div>

            {/* ── RIGHT: contextual panel ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Executive Risk Assessment */}
              {executive && (
                <div style={{
                  background: "var(--color-surface)", border: "1px solid var(--color-border)",
                  borderRadius: 6, padding: 20,
                }}>
                  <SectionLabel>Risk Assessment</SectionLabel>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 12 }}>
                    <span style={{ fontSize: 22, fontWeight: 700, color: execRiskCol, lineHeight: 1 }}>
                      {executive.overall_risk_level}
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: "var(--color-text-2)", lineHeight: 1.6 }}>
                    <SafeMarkdown text={executive.narrative?.split("\n\n")[0] ?? ""} />
                  </div>

                  {executive.recommendations?.slice(0, 3).map((rec, i) => (
                    <div key={i} style={{
                      marginTop:  12,
                      paddingTop: 12,
                      borderTop:  "1px solid var(--color-border)",
                    }}>
                      <div style={{
                        fontSize: 11, fontWeight: 500,
                        color: rec.priority === "HIGH" ? "#FF4444" : rec.priority === "MEDIUM" ? "#F59E0B" : "#22C55E",
                        textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 4,
                      }}>
                        {rec.priority} — {rec.action}
                      </div>
                      <div style={{ fontSize: 12, color: "var(--color-text-2)", lineHeight: 1.5 }}>
                        {rec.detail}
                      </div>
                      {rec.estimated_impact && (
                        <div style={{ fontSize: 11, color: "var(--color-text-3)", marginTop: 4 }}>
                          Impact: {rec.estimated_impact}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Anomaly list */}
              <div style={{
                background: "var(--color-surface)", border: "1px solid var(--color-border)",
                borderRadius: 6, padding: 20,
              }}>
                <SectionLabel>Anomalies</SectionLabel>
                {(anomalies?.anomalies?.length ?? 0) > 0 ? (
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    {anomalies!.anomalies.slice(0, 7).map((a, i, arr) => (
                      <div
                        key={i}
                        style={{
                          display:      "flex",
                          alignItems:   "center",
                          gap:          12,
                          padding:      "9px 0",
                          borderBottom: i < arr.length - 1 ? "1px solid var(--color-border)" : "none",
                        }}
                      >
                        <span style={{
                          width: 6, height: 6, borderRadius: "50%", flexShrink: 0,
                          background: a.severity === "high" ? "#FF4444" : "#F59E0B",
                        }} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {a.supplier}
                          </div>
                          <div style={{ fontSize: 11, color: "var(--color-text-3)", marginTop: 1 }}>
                            {a.type}
                          </div>
                        </div>
                        <span style={{
                          fontSize: 11, fontWeight: 500, flexShrink: 0,
                          color: a.severity === "high" ? "#FF4444" : "#F59E0B",
                        }}>
                          {a.risk_score}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: 13, color: "var(--color-text-3)", lineHeight: 1.5 }}>
                    No anomalies detected. Agents are monitoring.
                  </p>
                )}
              </div>

              {/* Risk distribution pie */}
              <div style={{
                background: "var(--color-surface)", border: "1px solid var(--color-border)",
                borderRadius: 6, padding: 20,
              }}>
                <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-2)", marginBottom: 16 }}>
                  Risk Distribution
                </div>
                {tierData.length > 0 ? (
                  <SynPieChart data={tierData} dataKey="value" nameKey="name" height={180} />
                ) : (
                  <NoData msg="No alerts generated yet." actionText="Upload Data to Analyze" actionHref="/upload" />
                )}
              </div>

              {/* Network resilience */}
              <div style={{
                background: "var(--color-surface)", border: "1px solid var(--color-border)",
                borderRadius: 6, padding: 20,
              }}>
                <SectionLabel>Network Resilience</SectionLabel>
                <div style={{ fontSize: 32, fontWeight: 700, color: "var(--color-text-1)", lineHeight: 1.1, letterSpacing: "-0.02em" }}>
                  {resilScore}%
                </div>
                <div style={{ marginTop: 12 }}>
                  <div style={{ height: 4, borderRadius: 999, background: "var(--color-surface-2)", overflow: "hidden" }}>
                    <div style={{
                      width: `${resilScore}%`, height: "100%", borderRadius: 999,
                      background: resilScore >= 70 ? "#22C55E" : resilScore >= 40 ? "#F59E0B" : "#FF4444",
                      transition: "width 160ms cubic-bezier(0.16,1,0.3,1)",
                    }} />
                  </div>
                </div>
                {(resilience?.critical_nodes?.length ?? 0) > 0 && (
                  <div style={{ marginTop: 12, fontSize: 12, color: "var(--color-text-2)" }}>
                    <span style={{ color: "#FF4444", fontWeight: 500 }}>{resilience.critical_nodes.length}</span>
                    {" "}critical node{resilience.critical_nodes.length !== 1 ? "s" : ""} identified
                  </div>
                )}
                <div style={{ marginTop: 8 }}>
                  <button
                    className="btn-text"
                    style={{ fontSize: 12 }}
                    onClick={() => router.push("/graph")}
                  >
                    View graph network →
                  </button>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
