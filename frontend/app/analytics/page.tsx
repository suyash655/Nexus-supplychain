"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import dynamic from "next/dynamic";
import { useApi } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";
import { NoData } from "../components/Cards/NoData";

const SynBarChart = dynamic(() => import("../components/Charts").then((m) => ({ default: m.SynBarChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 300 }} /> });
const SynLineChart = dynamic(() => import("../components/Charts").then((m) => ({ default: m.SynLineChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 300 }} /> });
const SynPieChart = dynamic(() => import("../components/Charts").then((m) => ({ default: m.SynPieChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 300 }} /> });
const SynAreaChart = dynamic(() => import("../components/Charts").then((m) => ({ default: m.SynAreaChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 300 }} /> });

const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";

/* ── Demo data ── */
const DEMO_SUMMARY = {
  total_records: 2847, avg_delay_days: 4.7, max_delay_days: 21, total_cost: 4892500,
};
const DEMO_SUPPLIERS = [
  { supplier: "Apex Materials",  avg_delay: 8.3, total_cost: 892000,  risk_score: 82, total_shipments: 187 },
  { supplier: "GlobalTech Co",   avg_delay: 6.9, total_cost: 654000,  risk_score: 76, total_shipments: 142 },
  { supplier: "SteelMax Inc",    avg_delay: 5.2, total_cost: 521000,  risk_score: 68, total_shipments: 98  },
  { supplier: "ProLogix Asia",   avg_delay: 4.8, total_cost: 780000,  risk_score: 65, total_shipments: 221 },
  { supplier: "NorthStar Parts", avg_delay: 4.1, total_cost: 445000,  risk_score: 58, total_shipments: 167 },
  { supplier: "Delta Logistics", avg_delay: 2.8, total_cost: 356000,  risk_score: 45, total_shipments: 312 },
];
const DEMO_TIME_SERIES = {
  delay_trend:  [
    { period: "Jan", avg_delay: 3.2 }, { period: "Feb", avg_delay: 3.8 },
    { period: "Mar", avg_delay: 4.1 }, { period: "Apr", avg_delay: 5.2 },
    { period: "May", avg_delay: 4.7 }, { period: "Jun", avg_delay: 4.9 },
  ],
  volume_trend: [
    { period: "Jan", count: 280 }, { period: "Feb", count: 310 },
    { period: "Mar", count: 295 }, { period: "Apr", count: 340 },
    { period: "May", count: 320 }, { period: "Jun", count: 350 },
  ],
};
const DEMO_QUALITY = { completeness_pct: 94, columns: {} };

/* ── Sub-components ── */

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: "var(--color-surface)", border: "1px solid var(--color-border)",
      borderRadius: 6, padding: 20,
    }}>
      <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "0.05em", color: "var(--color-text-2)", marginBottom: 16 }}>
        {title}
      </div>
      {children}
    </div>
  );
}



/* ── Page ── */
export default function AnalyticsPage() {
  const router = useRouter();

  const { data: summary, loading: l1 } = useApi<any>("/analytics/summary", { fallback: DEMO_SUMMARY });
  const { data: suppliers, loading: l2 } = useApi<any[]>("/analytics/suppliers", { fallback: DEMO_SUPPLIERS });
  const { data: timeSeries, loading: l3 } = useApi<any>("/analytics/time-series", { fallback: DEMO_TIME_SERIES });
  const { data: quality, loading: l4 } = useApi<any>("/analytics/data-quality", { fallback: DEMO_QUALITY });

  const loading = l1 || l2 || l3 || l4;

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 24 }}>
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

  /* ── Derived series ── */
  const delayDist = suppliers.map((s: any) => ({
    name:       s.supplier?.length > 11 ? s.supplier.slice(0, 11) + "…" : s.supplier,
    avg_delay:  s.avg_delay,
    total_cost: s.total_cost,
    risk_score: s.risk_score ?? 0,
    shipments:  s.total_shipments ?? s.rows ?? 0,
  }));

  const costBySupplier = suppliers.map((s: any) => ({
    name:  s.supplier?.length > 11 ? s.supplier.slice(0, 11) + "…" : s.supplier,
    value: s.total_cost,
  }));

  const completeness = quality?.completeness_pct ?? 0;
  const qualityColumns = Object.entries(quality?.columns ?? {}) as [string, any][];

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
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>Intelligence</div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                Analytics
              </h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>
                Supply chain metrics, trends, and data quality across all suppliers
              </p>
            </div>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <button
                onClick={() => router.push("/upload")}
                style={{
                  display: "inline-flex", alignItems: "center", padding: "8px 16px",
                  borderRadius: 4, fontSize: 13, fontWeight: 600, fontFamily: "var(--font-sans)",
                  background: "transparent", border: "1px solid var(--color-border-hi)",
                  color: "var(--color-text-1)", cursor: "pointer",
                  transition: `background 120ms ${EASE}`,
                }}
                onMouseEnter={e => (e.currentTarget.style.background = "var(--color-surface-2)")}
                onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
              >
                Upload New Data
              </button>
              <button
                onClick={() => router.push("/export")}
                style={{
                  display: "inline-flex", alignItems: "center", padding: "8px 16px",
                  borderRadius: 4, fontSize: 13, fontWeight: 600, fontFamily: "var(--font-sans)",
                  background: "var(--color-accent)", color: "#0A0A0A",
                  border: "none", cursor: "pointer",
                  transition: `opacity 120ms ${EASE}`,
                }}
                onMouseEnter={e => (e.currentTarget.style.opacity = "0.88")}
                onMouseLeave={e => (e.currentTarget.style.opacity = "1")}
              >
                Export CSV
              </button>
            </div>
          </div>

          {/* ══ LAYER B — KPI Strip ══ */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
            <KpiCard
              label="Total Records"
              value={summary?.total_records?.toLocaleString() ?? "0"}
              delta={`${suppliers.length} suppliers`}
              deltaDir="neutral"
            />
            <KpiCard
              label="Avg Delay"
              value={`${(summary?.avg_delay_days ?? 0).toFixed(1)}d`}
              delta={(summary?.avg_delay_days ?? 0) > 5 ? "Above threshold" : "Within range"}
              deltaDir={(summary?.avg_delay_days ?? 0) > 5 ? "down" : "up"}
            />
            <KpiCard
              label="Max Delay"
              value={`${summary?.max_delay_days ?? 0}d`}
              delta="Worst recorded shipment"
              deltaDir="down"
            />
            <KpiCard
              label="Data Completeness"
              value={`${completeness}%`}
              delta={completeness >= 90 ? "Excellent quality" : completeness >= 70 ? "Acceptable" : "Review required"}
              deltaDir={completeness >= 90 ? "up" : completeness >= 70 ? "neutral" : "down"}
            />
          </div>

          {/* ══ LAYER C — 2-column content ══ */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 16, alignItems: "start" }}>

            {/* ── LEFT ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Delay by Supplier bar chart */}
              <ChartCard title="Average Delay by Supplier">
                {delayDist.length > 0 ? (
                  <SynBarChart data={delayDist} dataKey="avg_delay" nameKey="name" color="#F59E0B" height={260} />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

              {/* Delay trend */}
              <ChartCard title="Delay Trend Over Time">
                {timeSeries?.delay_trend?.length > 0 ? (
                  <SynAreaChart data={timeSeries.delay_trend} dataKey="avg_delay" xKey="period" color="#F59E0B" height={220} />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

              {/* Data Quality table */}
              {qualityColumns.length > 0 && (
                <div style={{
                  background: "var(--color-surface)", border: "1px solid var(--color-border)",
                  borderRadius: 6, overflow: "hidden",
                }}>
                  <div style={{
                    padding: "14px 20px", borderBottom: "1px solid var(--color-border)",
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "0.05em", color: "var(--color-text-2)" }}>
                      Data Quality Report
                    </div>
                  </div>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                    <thead>
                      <tr>
                        {["COLUMN", "TYPE", "MISSING", "UNIQUE VALUES", "QUALITY"].map(h => (
                          <th key={h} style={{
                            textAlign: "left", padding: "10px 16px",
                            fontSize: 11, fontWeight: 500,
                            textTransform: "uppercase" as const, letterSpacing: "0.05em",
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
                      {qualityColumns.map(([col, info]) => (
                        <tr
                          key={col}
                          style={{ transition: `background 120ms ${EASE}` }}
                          onMouseEnter={e => (e.currentTarget.style.background = "var(--color-surface-2)")}
                          onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                        >
                          <td style={{ padding: "0 16px", height: 44, fontWeight: 500, color: "var(--color-text-1)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                            {col}
                          </td>
                          <td style={{ padding: "0 16px", height: 44, color: "var(--color-text-3)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                            {info.dtype}
                          </td>
                          <td style={{ padding: "0 16px", height: 44, borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                            <span style={{ fontWeight: 500, color: info.missing_pct > 10 ? "#FF4444" : info.missing_pct > 0 ? "#F59E0B" : "#22C55E" }}>
                              {info.missing_pct}%
                            </span>
                          </td>
                          <td style={{ padding: "0 16px", height: 44, color: "var(--color-text-2)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                            {info.unique_values}
                          </td>
                          <td style={{ padding: "0 16px", height: 44, borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                            <div style={{ width: 64, height: 4, borderRadius: 999, background: "var(--color-surface-2)", overflow: "hidden" }}>
                              <div style={{
                                width: `${100 - info.missing_pct}%`, height: "100%", borderRadius: 999,
                                background: info.missing_pct > 10 ? "#FF4444" : "#22C55E",
                                transition: `width 160ms ${EASE}`,
                              }} />
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Full supplier detail table */}
              <div style={{
                background: "var(--color-surface)", border: "1px solid var(--color-border)",
                borderRadius: 6, overflow: "hidden",
              }}>
                <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--color-border)" }}>
                  <div style={{ fontSize: 11, fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "0.05em", color: "var(--color-text-2)" }}>
                    Supplier Detail
                  </div>
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr>
                      {["SUPPLIER", "RISK SCORE", "AVG DELAY", "SHIPMENTS", "TOTAL COST"].map(h => (
                        <th key={h} style={{
                          textAlign: "left", padding: "10px 16px",
                          fontSize: 11, fontWeight: 500,
                          textTransform: "uppercase" as const, letterSpacing: "0.05em",
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
                    {delayDist.map((s: any, i: number) => (
                      <tr
                        key={i}
                        style={{ transition: `background 120ms ${EASE}` }}
                        onMouseEnter={e => (e.currentTarget.style.background = "var(--color-surface-2)")}
                        onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                      >
                        <td style={{ padding: "0 16px", height: 44, fontWeight: 500, color: "var(--color-text-1)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                          {suppliers[i]?.supplier}
                        </td>
                        <td style={{ padding: "0 16px", height: 44, borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ fontWeight: 600, minWidth: 28, color: s.risk_score >= 70 ? "#FF4444" : s.risk_score >= 40 ? "#F59E0B" : "#22C55E" }}>
                              {s.risk_score}
                            </span>
                            <div style={{ width: 64, height: 4, borderRadius: 999, background: "var(--color-surface-2)", overflow: "hidden" }}>
                              <div style={{
                                width: `${s.risk_score}%`, height: "100%", borderRadius: 999,
                                background: s.risk_score >= 70 ? "#FF4444" : s.risk_score >= 40 ? "#F59E0B" : "#22C55E",
                              }} />
                            </div>
                          </div>
                        </td>
                        <td style={{ padding: "0 16px", height: 44, color: "var(--color-text-1)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                          {s.avg_delay}d
                        </td>
                        <td style={{ padding: "0 16px", height: 44, color: "var(--color-text-2)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                          {s.shipments}
                        </td>
                        <td style={{ padding: "0 16px", height: 44, color: "var(--color-text-2)", borderBottom: "1px solid var(--color-border)", verticalAlign: "middle" }}>
                          ₹{s.total_cost?.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>

            {/* ── RIGHT ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Cost distribution pie */}
              <ChartCard title="Cost Distribution">
                {costBySupplier.length > 0 ? (
                  <SynPieChart data={costBySupplier} dataKey="value" nameKey="name" height={220} />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

              {/* Risk vs Delay line */}
              <ChartCard title="Risk Score vs Avg Delay">
                {delayDist.length > 0 ? (
                  <SynLineChart
                    data={delayDist}
                    lines={[
                      { key: "risk_score", color: "#FF4444", name: "Risk Score" },
                      { key: "avg_delay",  color: "#F59E0B", name: "Avg Delay"  },
                    ]}
                    xKey="name"
                    height={220}
                  />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

              {/* Shipment volume trend */}
              <ChartCard title="Volume Trend">
                {timeSeries?.volume_trend?.length > 0 ? (
                  <SynAreaChart data={timeSeries.volume_trend} dataKey="count" xKey="period" color="#888888" height={180} />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

              {/* Shipment volume bar */}
              <ChartCard title="Shipment Volume by Supplier">
                {delayDist.length > 0 ? (
                  <SynBarChart data={delayDist} dataKey="shipments" nameKey="name" color="#22C55E" height={200} />
                ) : (
                  <NoData height={200} msg="Insufficient data for this chart." actionText="Upload Dataset" actionHref="/upload" />
                )}
              </ChartCard>

            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
