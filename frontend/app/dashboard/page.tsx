"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { SafeMarkdown } from "../components/feedback/SafeMarkdown";
import {
  DEMO_SUMMARY,
  DEMO_SUPPLIERS,
  DEMO_EXECUTIVE,
  DEMO_ANOMALIES,
  DEMO_TIME_SERIES,
  DEMO_RESILIENCE,
} from "../demo-data";
import { useApi } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";
import { TierBadge } from "../components/Cards/TierBadge";
import { NoData } from "../components/Cards/NoData";
import { Meter, Notice, PageHeader, Panel, Pill } from "../components/ui/Primitives";
import { CHART, formatDelay, formatInr, formatInrCompact, formatNumber, scoreColor, scoreVar, shortName } from "@/lib/ui";

const SynBarChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynBarChart })),
  { ssr: false, loading: () => <div className="skeleton" style={{ height: 240 }} /> }
);
const SynPieChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynPieChart })),
  { ssr: false, loading: () => <div className="skeleton" style={{ height: 200 }} /> }
);
const SynAreaChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynAreaChart })),
  { ssr: false, loading: () => <div className="skeleton" style={{ height: 180 }} /> }
);

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
  is_demo_data: boolean;
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

function levelColor(level: string | undefined): string {
  const l = (level ?? "").toUpperCase();
  if (l === "CRITICAL" || l === "HIGH") return "var(--color-danger)";
  if (l === "ELEVATED" || l === "MEDIUM") return "var(--color-warn)";
  return "var(--color-ok)";
}

/* ── Page ── */
export default function DashboardPage() {
  const router = useRouter();
  const [uploadedReal, setUploadedReal] = useState(false);

  useEffect(() => {
    const hasData = localStorage.getItem("nexus_has_real_data") === "true";
    queueMicrotask(() => setUploadedReal(hasData));
  }, []);

  const { data: summary, loading: l1, isDemoMode: dSummary } = useApi<Summary | null>("/analytics/summary", { fallback: DEMO_SUMMARY });
  const { data: suppliersResponse, loading: l2, isDemoMode: dSuppliers } = useApi<{ data: RiskSupplier[]; total: number; skip: number; limit: number }>("/analytics/suppliers", {
    fallback: { data: DEMO_SUPPLIERS, total: DEMO_SUPPLIERS.length, skip: 0, limit: 50 },
  });
  const { data: executive, isDemoMode: dExecutive } = useApi<ExecutiveSummary | null>("/copilot/summary", { fallback: DEMO_EXECUTIVE });
  const { data: anomalies, loading: l4, isDemoMode: dAnomalies } = useApi<AnomalyData | null>("/ml/anomalies", { fallback: DEMO_ANOMALIES });
  const { data: timeSeries, isDemoMode: dSeries } = useApi<any>("/analytics/time-series", { fallback: DEMO_TIME_SERIES });
  const { data: resilience, isDemoMode: dResilience } = useApi<any>("/graph/resilience", { fallback: DEMO_RESILIENCE });

  const suppliers = useMemo(() => suppliersResponse?.data ?? [], [suppliersResponse]);

  // The backend's is_demo_data flag is the authoritative "real data" signal
  const summaryHasRealData = !!summary && summary.is_demo_data === false;
  const hasRealData = summaryHasRealData || suppliers.length > 0;
  // tier "unknown" means rows are loaded but ML scoring has not finished
  const analysisComplete = suppliers.some((s) => s.tier !== "unknown");
  const isDemo = !hasRealData && (dSummary || dSuppliers || dExecutive || dAnomalies || dSeries || dResilience);

  const dataTimestamp = useMemo(() => (hasRealData ? new Date() : null), [hasRealData]);

  const riskTiers = useMemo(
    () => ({
      critical: suppliers.filter((s) => s.tier === "critical").length,
      elevated: suppliers.filter((s) => s.tier === "elevated").length,
      stable: suppliers.filter((s) => s.tier === "stable").length,
    }),
    [suppliers]
  );

  const tierData = useMemo(
    () =>
      [
        { name: "Critical", value: riskTiers.critical },
        { name: "Elevated", value: riskTiers.elevated },
        { name: "Stable", value: riskTiers.stable },
      ].filter((d) => d.value > 0),
    [riskTiers]
  );

  const topRiskSuppliers = useMemo(
    () => suppliers.slice(0, 8).map((s) => ({ name: shortName(s.supplier, 12), risk_score: s.risk_score })),
    [suppliers]
  );

  const resilScore: number = resilience?.network_resilience_score ?? 50;
  const resilColor = resilScore >= 70 ? "var(--color-ok)" : resilScore >= 40 ? "var(--color-warn)" : "var(--color-danger)";
  const criticalNodes: number = resilience?.critical_nodes?.length ?? 0;

  const live = !isDemo && hasRealData;
  const anomalyCount = anomalies?.anomaly_count ?? 0;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div className="page-wrap">
            <PageHeader
              eyebrow="Overview"
              title="Command Center"
              subtitle="Real-time intelligence across your supply chain network"
              actions={
                <>
                  <Link href="/analytics" className="btn btn-secondary">Deep analytics</Link>
                  {!hasRealData && <Link href="/upload" className="btn btn-primary">Upload data</Link>}
                </>
              }
            />

            {isDemo && !uploadedReal && (
              <div style={{ marginBottom: 24 }}>
                <Notice
                  tone="info"
                  title="Demo data"
                  action={<Link href="/upload" className="btn btn-secondary btn-sm">Upload data</Link>}
                >
                  The backend is offline or no data has been uploaded yet.
                </Notice>
              </div>
            )}
            {isDemo && uploadedReal && (
              <div style={{ marginBottom: 24 }}>
                <Notice tone="danger" title="Backend unavailable">
                  Your data was uploaded, but the server is not responding. Figures shown may be out of date.
                </Notice>
              </div>
            )}

            {/* KPI strip */}
            <div className="kpi-grid">
              <KpiCard
                label="Total records"
                value={summary?.total_records?.toLocaleString() ?? "0"}
                delta={`${summary?.unique_skus ?? 0} unique SKUs`}
                deltaDir="neutral"
                onClick={() => router.push("/analytics")}
                loading={l1}
                noData={!summary && !l1}
                timestamp={dataTimestamp}
                isLive={live}
              />
              <KpiCard
                label="Active suppliers"
                value={summary?.unique_suppliers ?? suppliers.length}
                delta={
                  riskTiers.critical > 0
                    ? `${riskTiers.critical} critical`
                    : analysisComplete
                      ? "All stable"
                      : hasRealData
                        ? "Analysis running…"
                        : "All stable"
                }
                deltaDir={riskTiers.critical > 0 ? "down" : "up"}
                onClick={() => router.push("/graph")}
                loading={l2}
                noData={!hasRealData && !l2}
                timestamp={dataTimestamp}
                isLive={live}
              />
              <KpiCard
                label="Avg delay"
                value={`${summary?.avg_delay_days?.toFixed(1) ?? "0.0"}d`}
                delta={`Max ${summary?.max_delay_days ?? 0}d recorded`}
                deltaDir={(summary?.avg_delay_days ?? 0) > 5 ? "down" : (summary?.avg_delay_days ?? 0) > 2 ? "neutral" : "up"}
                onClick={() => router.push("/analytics")}
                loading={l1}
                noData={!summary && !l1}
                timestamp={dataTimestamp}
                isLive={live}
              />
              <KpiCard
                label="Anomalies detected"
                value={anomalyCount}
                delta={anomalies?.methods_used?.join(", ") ?? "—"}
                deltaDir={anomalyCount > 0 ? "down" : "up"}
                onClick={() => router.push("/analytics")}
                loading={l4}
                noData={!anomalies && !l4}
                timestamp={dataTimestamp}
                isLive={live}
              />
            </div>

            <div className="dashboard-layout">
              {/* ── Left: primary data ── */}
              <div className="stack">
                {!analysisComplete && suppliers.length > 0 && (
                  <Notice tone="info" title="Analysis in progress">
                    Risk scores will fill in shortly. Showing live supplier data in the meantime.
                  </Notice>
                )}

                <Panel
                  title="Supplier risk leaderboard"
                  flush
                  action={<Link href="/analytics" className="link-btn">View all</Link>}
                >
                  {suppliers.length > 0 ? (
                    <div className="t-wrap">
                      <table className="t">
                        <thead>
                          <tr>
                            <th>Supplier</th>
                            <th>Risk score</th>
                            <th>Tier</th>
                            <th className="num">Avg delay</th>
                            <th className="num">Shipments</th>
                            <th className="num">Total cost</th>
                          </tr>
                        </thead>
                        <tbody>
                          {suppliers.slice(0, 10).map((s, i) => (
                            <tr
                              key={`${s.supplier}-${i}`}
                              className="row-link"
                              tabIndex={0}
                              onClick={() => router.push("/analytics")}
                              onKeyDown={(e) => {
                                if (e.key === "Enter") router.push("/analytics");
                              }}
                            >
                              <td>{s.supplier}</td>
                              <td>
                                <div className="score">
                                  <span className="score-n">{s.risk_score}</span>
                                  <Meter value={s.risk_score} color={scoreVar(s.risk_score)} delay={i * 0.04} />
                                </div>
                              </td>
                              <td>
                                {s.tier === "unknown" ? <Pill>pending</Pill> : <TierBadge tier={s.tier} />}
                              </td>
                              <td className="num">{formatDelay(s.avg_delay)}</td>
                              <td className="num">{formatNumber(s.total_shipments)}</td>
                              <td className="num">{formatInr(s.total_cost)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : l2 ? (
                    <div style={{ padding: 20, display: "grid", gap: 10 }}>
                      {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="skeleton" style={{ height: 36 }} />
                      ))}
                    </div>
                  ) : (
                    <div style={{ padding: 20 }}>
                      <NoData msg="No suppliers found." actionText="Upload supplier data" actionHref="/upload" />
                    </div>
                  )}
                </Panel>

                <div className="trend-charts-grid">
                  <Panel title="Delay trend" delay={0.05}>
                    {timeSeries?.delay_trend?.length > 0 ? (
                      <SynAreaChart
                        data={timeSeries.delay_trend}
                        dataKey="avg_delay"
                        xKey="period"
                        color={CHART.blue}
                        height={180}
                        label="Avg delay"
                        formatValue={(v: number) => `${v}d`}
                      />
                    ) : (
                      <NoData msg="No historical data available." actionText="Upload shipments" actionHref="/upload" />
                    )}
                  </Panel>
                  <Panel title="Cost trend" delay={0.1}>
                    {timeSeries?.cost_trend?.length > 0 ? (
                      <SynAreaChart
                        data={timeSeries.cost_trend}
                        dataKey="total_cost"
                        xKey="period"
                        color={CHART.brass}
                        height={180}
                        label="Total cost"
                        formatValue={formatInrCompact}
                      />
                    ) : (
                      <NoData msg="No cost data available." actionText="Upload shipments" actionHref="/upload" />
                    )}
                  </Panel>
                </div>

                <div className="split">
                  <Panel title="Supplier risk scores (0–100)">
                    {topRiskSuppliers.length > 0 ? (
                      <SynBarChart
                        data={topRiskSuppliers}
                        dataKey="risk_score"
                        nameKey="name"
                        height={260}
                        label="Risk score"
                        colorBy={(r: Record<string, any>) => scoreColor(r.risk_score)}
                        formatValue={(v: number) => String(Math.round(v))}
                      />
                    ) : (
                      <NoData msg="No risk scores yet." actionText="Upload data to analyze" actionHref="/upload" />
                    )}
                  </Panel>
                  <Panel title="Risk distribution" delay={0.05}>
                    {tierData.length > 0 ? (
                      <SynPieChart
                        data={tierData}
                        dataKey="value"
                        nameKey="name"
                        height={170}
                        centerCaption="suppliers"
                        formatValue={(v: number) => String(Math.round(v))}
                      />
                    ) : (
                      <NoData msg="No alerts generated yet." actionText="Upload data to analyze" actionHref="/upload" />
                    )}
                  </Panel>
                </div>
              </div>

              {/* ── Right: contextual panels ── */}
              <div className="stack">
                {executive && (
                  <Panel title="Risk assessment">
                    <div
                      style={{
                        marginBottom: 12,
                        fontSize: 28,
                        fontWeight: 300,
                        lineHeight: 1,
                        letterSpacing: "0.02em",
                        textTransform: "uppercase",
                        color: levelColor(executive.overall_risk_level),
                      }}
                    >
                      {executive.overall_risk_level}
                    </div>
                    <div style={{ fontSize: 13, lineHeight: 1.65, color: "var(--color-text-2)" }}>
                      <SafeMarkdown text={executive.narrative?.split("\n\n")[0] ?? ""} />
                    </div>

                    {executive.recommendations?.slice(0, 3).map((rec, i) => (
                      <div
                        key={i}
                        style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--color-border)" }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
                          <Pill tone={rec.priority === "HIGH" || rec.priority === "CRITICAL" ? "danger" : rec.priority === "MEDIUM" ? "warn" : "success"}>
                            {rec.priority.toLowerCase()}
                          </Pill>
                          <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                            {rec.action}
                          </span>
                        </div>
                        <div style={{ fontSize: 12, lineHeight: 1.55, color: "var(--color-text-2)" }}>{rec.detail}</div>
                        {rec.estimated_impact && (
                          <div style={{ marginTop: 4, fontSize: 11, color: "var(--color-text-3)" }}>
                            Impact: {rec.estimated_impact}
                          </div>
                        )}
                      </div>
                    ))}
                  </Panel>
                )}

                <Panel title="Anomalies" delay={0.05}>
                  {(anomalies?.anomalies?.length ?? 0) > 0 ? (
                    <div>
                      {anomalies!.anomalies.slice(0, 7).map((a, i) => (
                        <div key={i} className="list-row">
                          <span
                            aria-hidden="true"
                            style={{
                              width: 6,
                              height: 6,
                              flexShrink: 0,
                              borderRadius: "50%",
                              background: a.severity === "high" ? "var(--color-danger)" : "var(--color-warn)",
                            }}
                          />
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div
                              style={{
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                fontSize: 13,
                                fontWeight: 500,
                                color: "var(--color-text-1)",
                              }}
                            >
                              {a.supplier}
                            </div>
                            <div style={{ marginTop: 1, fontSize: 11, color: "var(--color-text-3)" }}>
                              {a.type.replace(/_/g, " ")}
                            </div>
                          </div>
                          <span
                            style={{
                              flexShrink: 0,
                              fontSize: 12,
                              fontWeight: 500,
                              fontVariantNumeric: "tabular-nums",
                              color: a.severity === "high" ? "var(--color-danger)" : "var(--color-warn)",
                            }}
                          >
                            {a.risk_score}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: 13, lineHeight: 1.5, color: "var(--color-text-3)" }}>
                      No anomalies detected. Agents are monitoring.
                    </p>
                  )}
                </Panel>

                <Panel title="Network resilience" delay={0.1}>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 2, marginBottom: 14 }}>
                    <span style={{ fontSize: 40, fontWeight: 300, lineHeight: 1, letterSpacing: "-0.03em", color: "var(--color-text-1)" }}>
                      {resilScore}
                    </span>
                    <span style={{ fontSize: 18, color: "var(--color-text-3)" }}>%</span>
                  </div>
                  <Meter wide value={resilScore} color={resilColor} />
                  {criticalNodes > 0 && (
                    <div style={{ marginTop: 14, fontSize: 12, color: "var(--color-text-2)" }}>
                      <span style={{ fontWeight: 500, color: "var(--color-danger)" }}>{criticalNodes}</span>{" "}
                      critical node{criticalNodes !== 1 ? "s" : ""} identified
                    </div>
                  )}
                  <div style={{ marginTop: 12 }}>
                    <Link href="/graph" className="link-btn">View graph network</Link>
                  </div>
                </Panel>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}