"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { Download, RefreshCw } from "lucide-react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { useApi } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";
import { NoData } from "../components/Cards/NoData";
import { Meter, Notice, PageHeader, Panel, Segmented } from "../components/ui/Primitives";
import {
  CHART,
  formatDecimal,
  formatDelay,
  formatInr,
  formatInrCompact,
  formatNumber,
  scoreVar,
  shortName,
} from "@/lib/ui";

const chartSkeleton = (h: number) => <div className="skeleton" style={{ height: h }} />;
const SynBarChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynBarChart })),
  { ssr: false, loading: () => chartSkeleton(260) }
);
const SynLineChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynLineChart })),
  { ssr: false, loading: () => chartSkeleton(240) }
);
const SynPieChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynPieChart })),
  { ssr: false, loading: () => chartSkeleton(220) }
);
const SynAreaChart = dynamic(
  () => import("../components/charts/Charts").then((m) => ({ default: m.SynAreaChart })),
  { ssr: false, loading: () => chartSkeleton(220) }
);

/* ── Demo data (shown only when the backend is unreachable) ── */
const DEMO_SUMMARY = { total_records: 2847, avg_delay_days: 4.7, max_delay_days: 21, total_cost: 4892500 };
const DEMO_SUPPLIERS = [
  { supplier: "Apex Materials", avg_delay: 8.3, total_cost: 892000, risk_score: 82, total_shipments: 187 },
  { supplier: "GlobalTech Co", avg_delay: 6.9, total_cost: 654000, risk_score: 76, total_shipments: 142 },
  { supplier: "SteelMax Inc", avg_delay: 5.2, total_cost: 521000, risk_score: 68, total_shipments: 98 },
  { supplier: "ProLogix Asia", avg_delay: 4.8, total_cost: 780000, risk_score: 65, total_shipments: 221 },
  { supplier: "NorthStar Parts", avg_delay: 4.1, total_cost: 445000, risk_score: 58, total_shipments: 167 },
  { supplier: "Delta Logistics", avg_delay: 2.8, total_cost: 356000, risk_score: 45, total_shipments: 312 },
];
const DEMO_TIME_SERIES = {
  delay_trend: [
    { period: "Jan", avg_delay: 3.2 },
    { period: "Feb", avg_delay: 3.8 },
    { period: "Mar", avg_delay: 4.1 },
    { period: "Apr", avg_delay: 5.2 },
    { period: "May", avg_delay: 4.7 },
    { period: "Jun", avg_delay: 4.9 },
  ],
  volume_trend: [
    { period: "Jan", count: 280 },
    { period: "Feb", count: 310 },
    { period: "Mar", count: 295 },
    { period: "Apr", count: 340 },
    { period: "May", count: 320 },
    { period: "Jun", count: 350 },
  ],
};
const DEMO_QUALITY = { completeness_pct: 94, columns: {} };

type RangeValue = "7d" | "30d" | "90d" | "1y";
type MetricValue = "all" | "high_risk" | "high_delay";

const RANGES: { value: RangeValue; label: string }[] = [
  { value: "7d", label: "7D" },
  { value: "30d", label: "30D" },
  { value: "90d", label: "90D" },
  { value: "1y", label: "1Y" },
];

const METRICS: { value: MetricValue; label: string }[] = [
  { value: "all", label: "All suppliers" },
  { value: "high_risk", label: "High risk (>70)" },
  { value: "high_delay", label: "High delay (>5d)" },
];

const NO_DATA = <NoData height={200} msg="Not enough data for this chart." actionText="Upload dataset" actionHref="/upload" />;

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<RangeValue>("30d");
  const [metric, setMetric] = useState<MetricValue>("all");
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [uploadedReal, setUploadedReal] = useState(false);

  useEffect(() => {
    setUploadedReal(localStorage.getItem("nexus_has_real_data") === "true");
  }, []);

  // The range goes into the request path, so changing it refetches automatically.
  // The backend must honour `date_range`; if it ignores it, the figures will not change.
  const rangeQuery = dateRange === "30d" ? "" : `?date_range=${dateRange}`;

  const { data: summary, loading: l1, error: e1, isDemoMode, retry: retrySummary } = useApi<any>(`/analytics/summary${rangeQuery}`, { fallback: DEMO_SUMMARY });
  const { data: suppliersResponse, loading: l2, error: e2, retry: retrySuppliers } = useApi<any[] | { data?: any[]; total?: number }>("/analytics/suppliers", {
    fallback: { data: DEMO_SUPPLIERS, total: DEMO_SUPPLIERS.length },
  });
  const { data: timeSeries, loading: l3, error: e3, retry: retrySeries } = useApi<any>(`/analytics/time-series${rangeQuery}`, { fallback: DEMO_TIME_SERIES });
  const { data: quality, loading: l4, error: e4, retry: retryQuality } = useApi<any>("/analytics/data-quality", { fallback: DEMO_QUALITY });

  const anyLoading = l1 || l2 || l3 || l4;
  const refreshAll = useCallback(() => {
    retrySummary();
    retrySuppliers();
    retrySeries();
    retryQuality();
  }, [retrySummary, retrySuppliers, retrySeries, retryQuality]);

  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(refreshAll, 30000);
    return () => clearInterval(id);
  }, [autoRefresh, refreshAll]);

  const allSuppliers = useMemo<any[]>(
    () => (Array.isArray(suppliersResponse) ? suppliersResponse : suppliersResponse?.data ?? []),
    [suppliersResponse]
  );

  const suppliers = useMemo(() => {
    if (metric === "high_risk") return allSuppliers.filter((s) => s.risk_score >= 70);
    if (metric === "high_delay") return allSuppliers.filter((s) => s.avg_delay >= 5);
    return allSuppliers;
  }, [allSuppliers, metric]);

  const rows = useMemo(
    () =>
      suppliers.map((s) => ({
        name: shortName(s.supplier, 11),
        avg_delay: s.avg_delay,
        risk_score: s.risk_score ?? 0,
        shipments: s.total_shipments ?? s.rows ?? 0,
      })),
    [suppliers]
  );

  const costRows = useMemo(() => suppliers.map((s) => ({ name: s.supplier, value: s.total_cost })), [suppliers]);

  const completeness = quality?.completeness_pct ?? 0;
  const qualityColumns = Object.entries(quality?.columns ?? {}) as [string, any][];

  const offline = [e1, e2, e3, e4].some((e) => e && (e.code === "network" || e.code === "timeout" || e.code === "server_5xx"));
  const initialLoading = anyLoading && !summary && !suppliersResponse;

  const header = (
    <PageHeader
      eyebrow="Intelligence"
      title="Analytics"
      subtitle="Supply chain metrics, trends, and data quality across all suppliers"
      actions={
        <>
          <Segmented label="Date range" value={dateRange} onChange={(v) => setDateRange(v as RangeValue)} options={RANGES} />
          <button type="button" className="btn btn-secondary btn-sm" onClick={refreshAll} disabled={anyLoading}>
            <RefreshCw size={14} className={anyLoading ? "animate-spin" : undefined} aria-hidden="true" />
            Refresh
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            aria-pressed={autoRefresh}
            onClick={() => setAutoRefresh((v) => !v)}
          >
            <span
              aria-hidden="true"
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: autoRefresh ? "var(--color-ok)" : "var(--color-text-3)",
              }}
            />
            Auto-refresh {autoRefresh ? "on" : "off"}
          </button>
          <Link href="/upload" className="btn btn-secondary btn-sm">Upload data</Link>
          <Link href="/export" className="btn btn-primary btn-sm">
            <Download size={14} aria-hidden="true" />
            Export
          </Link>
        </>
      }
    />
  );

  if (initialLoading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            <div className="page-wrap">
              {header}
              <div className="kpi-grid">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="skeleton" style={{ height: 132, borderRadius: 14 }} />
                ))}
              </div>
              <div className="skeleton" style={{ height: 320, borderRadius: 14 }} />
            </div>
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
          <div className="page-wrap">
            {header}

            {offline ? (
              <div style={{ marginBottom: 24 }}>
                <Notice
                  tone="danger"
                  title="Backend unavailable"
                  action={<button type="button" className="btn btn-secondary btn-sm" onClick={refreshAll}>Retry</button>}
                >
                  {uploadedReal
                    ? "Your data is safe, but the server is not responding. Figures may be out of date."
                    : "Showing demo data until the server is reachable."}
                </Notice>
              </div>
            ) : isDemoMode ? (
              <div style={{ marginBottom: 24 }}>
                <Notice
                  tone="info"
                  title="Demo data"
                  action={<Link href="/upload" className="btn btn-secondary btn-sm">Upload data</Link>}
                >
                  Upload a dataset to see your own suppliers here.
                </Notice>
              </div>
            ) : null}

            <div className="kpi-grid">
              <KpiCard label="Total records" value={summary?.total_records?.toLocaleString() ?? "0"} delta={`${suppliers.length} suppliers`} deltaDir="neutral" />
              <KpiCard
                label="Avg delay"
                value={`${(summary?.avg_delay_days ?? 0).toFixed(1)}d`}
                delta={(summary?.avg_delay_days ?? 0) > 5 ? "Above threshold" : "Within range"}
                deltaDir={(summary?.avg_delay_days ?? 0) > 5 ? "down" : "up"}
              />
              <KpiCard label="Max delay" value={`${summary?.max_delay_days ?? 0}d`} delta="Worst recorded shipment" deltaDir="down" />
              <KpiCard
                label="Data completeness"
                value={`${completeness}%`}
                delta={completeness >= 90 ? "Excellent quality" : completeness >= 70 ? "Acceptable" : "Review required"}
                deltaDir={completeness >= 90 ? "up" : completeness >= 70 ? "neutral" : "down"}
              />
            </div>

            <div className="toolbar" style={{ marginBottom: 16, justifyContent: "space-between" }}>
              <Segmented label="Supplier filter" value={metric} onChange={(v) => setMetric(v as MetricValue)} options={METRICS} />
              <span style={{ fontSize: 12, color: "var(--color-text-3)" }}>
                Showing {suppliers.length} of {allSuppliers.length} suppliers
              </span>
            </div>

            <div className="dashboard-layout">
              {/* ── Left ── */}
              <div className="stack">
                <Panel title="Average delay by supplier">
                  {rows.length > 0 ? (
                    <SynBarChart
                      data={rows}
                      dataKey="avg_delay"
                      nameKey="name"
                      height={260}
                      label="Avg delay"
                      colorBy={(r: Record<string, any>) => (r.avg_delay > 5 ? CHART.amber : CHART.blue)}
                      formatValue={(v: number) => `${formatDecimal(v)}d`}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>

                <Panel title="Delay trend over time" delay={0.05}>
                  {timeSeries?.delay_trend?.length > 0 ? (
                    <SynAreaChart
                      data={timeSeries.delay_trend}
                      dataKey="avg_delay"
                      xKey="period"
                      color={CHART.blue}
                      height={220}
                      label="Avg delay"
                      formatValue={(v: number) => `${formatDecimal(v)}d`}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>

                {qualityColumns.length > 0 && (
                  <Panel title="Data quality report" flush delay={0.05}>
                    <div className="t-wrap">
                      <table className="t">
                        <thead>
                          <tr>
                            <th>Column</th>
                            <th>Type</th>
                            <th className="num">Missing</th>
                            <th className="num">Unique values</th>
                            <th>Completeness</th>
                          </tr>
                        </thead>
                        <tbody>
                          {qualityColumns.map(([col, info]) => {
                            const missing = Number(info.missing_pct ?? 0);
                            const tone = missing > 10 ? "var(--color-danger)" : missing > 0 ? "var(--color-warn)" : "var(--color-ok)";
                            return (
                              <tr key={col}>
                                <td>{col}</td>
                                <td>{info.dtype}</td>
                                <td className="num" style={{ color: tone, fontWeight: 500 }}>{missing}%</td>
                                <td className="num">{formatNumber(info.unique_values)}</td>
                                <td>
                                  <Meter value={100 - missing} color={missing > 10 ? "var(--color-danger)" : "var(--color-ok)"} />
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </Panel>
                )}

                <Panel title="Supplier detail" flush delay={0.05}>
                  {suppliers.length > 0 ? (
                    <div className="t-wrap">
                      <table className="t">
                        <thead>
                          <tr>
                            <th>Supplier</th>
                            <th>Risk score</th>
                            <th className="num">Avg delay</th>
                            <th className="num">Shipments</th>
                            <th className="num">Total cost</th>
                          </tr>
                        </thead>
                        <tbody>
                          {suppliers.map((s, i) => (
                            <tr key={`${s.supplier}-${i}`}>
                              <td>{s.supplier}</td>
                              <td>
                                <div className="score">
                                  <span className="score-n" style={{ color: scoreVar(s.risk_score ?? 0) }}>{s.risk_score ?? 0}</span>
                                  <Meter value={s.risk_score ?? 0} color={scoreVar(s.risk_score ?? 0)} delay={i * 0.03} />
                                </div>
                              </td>
                              <td className="num">{formatDelay(s.avg_delay)}</td>
                              <td className="num">{formatNumber(s.total_shipments ?? s.rows)}</td>
                              <td className="num">{formatInr(s.total_cost)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div style={{ padding: 20 }}>
                      <NoData height={120} msg="No suppliers match this filter." />
                    </div>
                  )}
                </Panel>
              </div>

              {/* ── Right ── */}
              <div className="stack">
                <Panel title="Cost distribution">
                  {costRows.length > 0 ? (
                    <SynPieChart
                      data={costRows}
                      dataKey="value"
                      nameKey="name"
                      height={190}
                      centerCaption="total cost"
                      formatValue={formatInrCompact}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>

                <Panel title="Risk score vs avg delay" delay={0.05}>
                  {rows.length > 0 ? (
                    <SynLineChart
                      data={rows}
                      xKey="name"
                      height={220}
                      lines={[
                        { key: "risk_score", color: CHART.blue, name: "Risk score", axis: "left" },
                        { key: "avg_delay", color: CHART.brass, name: "Avg delay (days)", axis: "right" },
                      ]}
                      formatValue={(v: number) => formatDecimal(v)}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>

                <Panel title="Volume trend" delay={0.05}>
                  {timeSeries?.volume_trend?.length > 0 ? (
                    <SynAreaChart
                      data={timeSeries.volume_trend}
                      dataKey="count"
                      xKey="period"
                      color={CHART.brass}
                      height={180}
                      label="Shipments"
                      formatValue={(v: number) => formatNumber(v)}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>

                <Panel title="Shipment volume by supplier" delay={0.05}>
                  {rows.length > 0 ? (
                    <SynBarChart
                      data={rows}
                      dataKey="shipments"
                      nameKey="name"
                      color={CHART.brass}
                      height={200}
                      label="Shipments"
                      formatValue={(v: number) => formatNumber(v)}
                    />
                  ) : (
                    NO_DATA
                  )}
                </Panel>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}