"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { CalendarClock, FileText, MailPlus, Play, Plus, Trash2 } from "lucide-react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { KpiCard } from "../components/Cards/KpiCard";
import { SectionLabel } from "../components/Cards/SectionLabel";
import { NoData } from "../components/Cards/NoData";
import { useToast } from "../components/feedback/ToastContext";
import { useApi } from "../../hooks/useApi";
import { apiPostJSON } from "@/lib/api";

const SynLineChart = dynamic(() => import("../components/charts/Charts").then((m) => ({ default: m.SynLineChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynBarChart = dynamic(() => import("../components/charts/Charts").then((m) => ({ default: m.SynBarChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 240 }} /> });

type ReportSection = {
  id: string;
  type: "kpi_overview" | "trend_analysis" | "correlation_analysis" | "outlier_analysis" | "summary_statistics";
  title: string;
};

type DashboardData = typeof DEMO_DASHBOARD;
type ReportResultSection = { title?: string; type?: string };
type GeneratedReport = {
  report_id: string;
  title: string;
  sections?: ReportResultSection[];
  data_summary?: { total_rows?: number };
};
type TrendValue = {
  current_value?: number;
  next_period_forecast?: number;
  percent_change?: number;
  volatility?: number;
};
type CorrelationRow = {
  variable_1: string;
  variable_2: string;
  correlation_coefficient: number;
};
type TemplateResponse = { templates: Record<string, unknown> };
type CreateReportResponse = { report: GeneratedReport };
type ScheduleResponse = { next_run: string };

const DEMO_DASHBOARD = {
  summary: {
    rows: 2847,
    columns: 12,
    numeric_columns: ["delay_days", "cost", "quantity", "quality_score"],
    templates: 4,
    scheduled_reports: 2,
    subscriptions: 8,
  },
  trend_analysis: {
    trend_analysis: {
      delay_days: { current_value: 4.9, next_period_forecast: 5.3, trend_direction: "increasing", percent_change: 18.2, volatility: 0.24 },
      cost: { current_value: 812000, next_period_forecast: 845000, trend_direction: "increasing", percent_change: 9.4, volatility: 0.16 },
      quantity: { current_value: 350, next_period_forecast: 366, trend_direction: "increasing", percent_change: 12.1, volatility: 0.11 },
    },
  },
  correlation_analysis: {
    significant_correlations: [
      { variable_1: "delay_days", variable_2: "cost", correlation_coefficient: 0.73, correlation_strength: "strong" },
      { variable_1: "quantity", variable_2: "cost", correlation_coefficient: 0.68, correlation_strength: "moderate" },
      { variable_1: "quality_score", variable_2: "delay_days", correlation_coefficient: -0.52, correlation_strength: "moderate" },
    ],
  },
};

const SECTION_LABELS: Record<ReportSection["type"], string> = {
  kpi_overview: "KPI Overview",
  trend_analysis: "Trend Analysis",
  correlation_analysis: "Correlation Analysis",
  outlier_analysis: "Outlier Detection",
  summary_statistics: "Summary Statistics",
};

function Panel({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20, ...style }}>
      {children}
    </div>
  );
}

export default function AnalyticsReportsPage() {
  const { showToast } = useToast();
  const { data: dashboard, loading } = useApi<DashboardData>("/analytics-reporting/dashboard", { fallback: DEMO_DASHBOARD, timeout: 12000 });
  const { data: templates } = useApi<TemplateResponse>("/analytics-reporting/templates", { fallback: { templates: {} } });

  const [title, setTitle] = useState("Supply Chain Weekly Performance");
  const [format, setFormat] = useState("html");
  const [schedule, setSchedule] = useState("weekly");
  const [subscriber, setSubscriber] = useState("ops-team@nexus.ai");
  const [sections, setSections] = useState<ReportSection[]>([
    { id: "sec-1", type: "kpi_overview", title: "KPI Overview" },
    { id: "sec-2", type: "trend_analysis", title: "Trend Analysis" },
    { id: "sec-3", type: "correlation_analysis", title: "Correlation Analysis" },
  ]);
  const [selectedSection, setSelectedSection] = useState<ReportSection["type"]>("kpi_overview");
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null);
  const [busy, setBusy] = useState(false);

  const trendRows = useMemo(() => {
    const trend = dashboard?.trend_analysis?.trend_analysis ?? {};
    return Object.entries(trend).map(([metric, value]) => {
      const trendValue = value as TrendValue;
      return {
      metric,
      current: Number(trendValue.current_value ?? 0),
      forecast: Number(trendValue.next_period_forecast ?? 0),
      change: Number(trendValue.percent_change ?? 0),
      volatility: Number(trendValue.volatility ?? 0),
      };
    });
  }, [dashboard]);

  const correlations = (dashboard?.correlation_analysis?.significant_correlations ?? []) as CorrelationRow[];
  const reportPayload = {
    title,
    format,
    description: "Self-service analytics report generated from the reporting workspace.",
    sections: sections.map((section) => ({
      type: section.type,
      title: section.title,
      date_column: "order_date",
      value_columns: ["delay_days", "cost", "quantity"],
      columns: ["delay_days", "cost", "quantity"],
      method: "pearson",
      threshold: 0.5,
      kpis: [
        { name: "Total Cost", column: "cost", aggregation: "sum", format: "currency" },
        { name: "Average Delay", column: "delay_days", aggregation: "mean", unit: "days" },
        { name: "Total Quantity", column: "quantity", aggregation: "sum" },
      ],
    })),
  };

  const createReport = async () => {
    setBusy(true);
    try {
      const result = await apiPostJSON<CreateReportResponse>("/analytics-reporting/reports", reportPayload);
      setGeneratedReport(result.report);
      showToast("Report generated", "success");
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : "Unable to generate report", "error");
    } finally {
      setBusy(false);
    }
  };

  const scheduleReport = async () => {
    setBusy(true);
    try {
      const result = await apiPostJSON<ScheduleResponse>("/analytics-reporting/reports/schedule", { report_config: reportPayload, schedule });
      showToast(`Scheduled. Next run: ${new Date(result.next_run).toLocaleString()}`, "success");
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : "Unable to schedule report", "error");
    } finally {
      setBusy(false);
    }
  };

  const subscribe = async () => {
    const reportId = generatedReport?.report_id ?? "draft-report";
    try {
      await apiPostJSON(`/analytics-reporting/reports/${reportId}/subscriptions`, { email: subscriber, format, delivery_method: "email" });
      showToast("Subscription added", "success");
    } catch (error: unknown) {
      showToast(error instanceof Error ? error.message : "Unable to add subscription", "error");
    }
  };

  const addSection = () => {
    setSections((prev) => [...prev, { id: `sec-${Date.now()}`, type: selectedSection, title: SECTION_LABELS[selectedSection] }]);
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, paddingBottom: 16, marginBottom: 24, borderBottom: "1px solid var(--color-border)", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>Advanced Analytics</div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>Analytics Reports</h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>Build, schedule, and distribute operational reports.</p>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <button className="btn btn-secondary btn-sm" onClick={scheduleReport} disabled={busy}><CalendarClock size={14} /> Schedule</button>
              <button className="btn btn-secondary btn-sm" onClick={subscribe}><MailPlus size={14} /> Subscribe</button>
              <button className="btn btn-primary btn-sm" onClick={createReport} disabled={busy}><Play size={14} /> Generate</button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginBottom: 24 }}>
            <KpiCard label="Rows Analyzed" value={(dashboard?.summary?.rows ?? 0).toLocaleString()} delta={`${dashboard?.summary?.columns ?? 0} columns`} deltaDir="neutral" />
            <KpiCard label="Templates" value={dashboard?.summary?.templates ?? 0} delta={`${Object.keys(templates?.templates ?? {}).length} available`} deltaDir="up" />
            <KpiCard label="Schedules" value={dashboard?.summary?.scheduled_reports ?? 0} delta="Automated reports" deltaDir="neutral" />
            <KpiCard label="Subscriptions" value={dashboard?.summary?.subscriptions ?? 0} delta="Distribution list" deltaDir="up" />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 360px) 1fr", gap: 16, alignItems: "start" }}>
            <Panel>
              <SectionLabel>Report Builder</SectionLabel>
              <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 16 }}>
                <input value={title} onChange={(e) => setTitle(e.target.value)} style={{ height: 36, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)", padding: "0 10px" }} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  <select value={format} onChange={(e) => setFormat(e.target.value)} style={{ height: 36, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)" }}>
                    {["html", "pdf", "excel", "csv"].map((option) => <option key={option}>{option}</option>)}
                  </select>
                  <select value={schedule} onChange={(e) => setSchedule(e.target.value)} style={{ height: 36, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)" }}>
                    {["hourly", "daily", "weekly", "monthly"].map((option) => <option key={option}>{option}</option>)}
                  </select>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <select value={selectedSection} onChange={(e) => setSelectedSection(e.target.value as ReportSection["type"])} style={{ flex: 1, height: 36, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)" }}>
                    {Object.entries(SECTION_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
                  </select>
                  <button className="btn btn-secondary btn-sm" onClick={addSection} aria-label="Add section"><Plus size={14} /></button>
                </div>
                <input value={subscriber} onChange={(e) => setSubscriber(e.target.value)} style={{ height: 36, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)", padding: "0 10px" }} />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 16 }}>
                {sections.map((section) => (
                  <div key={section.id} draggable style={{ display: "flex", alignItems: "center", gap: 8, padding: 10, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)" }}>
                    <FileText size={14} color="var(--color-text-3)" />
                    <span style={{ flex: 1, fontSize: 13, color: "var(--color-text-1)" }}>{section.title}</span>
                    <button className="btn-text" onClick={() => setSections((prev) => prev.filter((item) => item.id !== section.id))} aria-label="Remove section"><Trash2 size={14} /></button>
                  </div>
                ))}
              </div>
            </Panel>

            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <Panel>
                <SectionLabel>Trend Forecast</SectionLabel>
                {trendRows.length ? <SynLineChart data={trendRows} xKey="metric" lines={[{ key: "current", name: "Current", color: "#3B82F6" }, { key: "forecast", name: "Forecast", color: "#10B981" }]} height={240} /> : <NoData msg="No trend data available" />}
              </Panel>

              <Panel>
                <SectionLabel>Correlation Strength</SectionLabel>
                {correlations.length ? (
                  <SynBarChart data={correlations.map((c) => ({ name: `${c.variable_1}/${c.variable_2}`, score: Math.abs(c.correlation_coefficient) }))} dataKey="score" nameKey="name" color="#F59E0B" height={220} />
                ) : <NoData msg="No significant correlations found" />}
              </Panel>

              <Panel>
                <SectionLabel>Generated Report</SectionLabel>
                {generatedReport ? (
                  <div style={{ display: "grid", gap: 10, fontSize: 13, color: "var(--color-text-2)" }}>
                    <strong style={{ color: "var(--color-text-1)" }}>{generatedReport.title}</strong>
                    <span>{generatedReport.report_id} · {generatedReport.sections?.length ?? 0} sections · {generatedReport.data_summary?.total_rows?.toLocaleString()} rows</span>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      {generatedReport.sections?.map((section, index: number) => (
                        <span key={index} style={{ padding: "4px 8px", borderRadius: 4, border: "1px solid var(--color-border)", color: "var(--color-text-2)" }}>{section.title ?? section.type}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <NoData msg={loading ? "Loading analytics data" : "Generate a report to preview the output"} />
                )}
              </Panel>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
