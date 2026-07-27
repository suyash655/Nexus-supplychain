"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { useToast } from "../components/feedback/ToastContext";
import { useApi } from "../../hooks/useApi";
import { KpiCard } from "../components/Cards/KpiCard";
import { SectionLabel } from "../components/Cards/SectionLabel";
import { NoData } from "../components/Cards/NoData";
import dynamic from "next/dynamic";

const SynBarChart = dynamic(() => import("../components/charts/Charts").then(m => ({ default: m.SynBarChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynLineChart = dynamic(() => import("../components/charts/Charts").then(m => ({ default: m.SynLineChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });
const SynPieChart = dynamic(() => import("../components/charts/Charts").then(m => ({ default: m.SynPieChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });

/* ── Types ── */
type SOPMetrics = {
  forecast_accuracy: number;
  demand_variance: number;
  supply_variance: number;
  inventory_turnover: number;
  customer_service_level: number;
  revenue_alignment: number;
};

type ConsensusData = {
  sales_forecast: number;
  marketing_forecast: number;
  finance_forecast: number;
  operations_forecast: number;
  consensus_forecast: number;
  actual_demand: number;
  period: string;
};

type Scenario = {
  id: string;
  name: string;
  type: string;
  status: string;
  probability: number;
  impact: string;
  created_at: string;
};

type ApprovalWorkflow = {
  step: string;
  status: string;
  assigned_to: string;
  completed_at?: string;
};

type FinancialIntegration = {
  revenue: number;
  cost: number;
  margin: number;
  budget_variance: number;
  period: string;
};

/* ── Demo Data ── */
const DEMO_SOP_METRICS: SOPMetrics = {
  forecast_accuracy: 87.5,
  demand_variance: 12.3,
  supply_variance: 8.7,
  inventory_turnover: 4.2,
  customer_service_level: 94.8,
  revenue_alignment: 92.1
};

const DEMO_CONSENSUS_DATA: ConsensusData[] = [
  { period: "2024-01", sales_forecast: 1000, marketing_forecast: 1100, finance_forecast: 950, operations_forecast: 1050, consensus_forecast: 1025, actual_demand: 1015 },
  { period: "2024-02", sales_forecast: 1050, marketing_forecast: 1150, finance_forecast: 1000, operations_forecast: 1100, consensus_forecast: 1075, actual_demand: 1080 },
  { period: "2024-03", sales_forecast: 1100, marketing_forecast: 1200, finance_forecast: 1050, operations_forecast: 1150, consensus_forecast: 1125, actual_demand: 1110 },
  { period: "2024-04", sales_forecast: 1150, marketing_forecast: 1250, finance_forecast: 1100, operations_forecast: 1200, consensus_forecast: 1175, actual_demand: 1190 },
  { period: "2024-05", sales_forecast: 1200, marketing_forecast: 1300, finance_forecast: 1150, operations_forecast: 1250, consensus_forecast: 1225, actual_demand: 1235 },
  { period: "2024-06", sales_forecast: 1250, marketing_forecast: 1350, finance_forecast: 1200, operations_forecast: 1300, consensus_forecast: 1275, actual_demand: 1280 },
];

const DEMO_SCENARIOS: Scenario[] = [
  { id: "SC1", name: "Demand Surge Q3", type: "demand", status: "active", probability: 0.75, impact: "high", created_at: "2024-06-01" },
  { id: "SC2", name: "Supply Disruption Asia", type: "supply", status: "monitoring", probability: 0.35, impact: "medium", created_at: "2024-06-05" },
  { id: "SC3", name: "New Product Launch", type: "product", status: "planning", probability: 0.90, impact: "high", created_at: "2024-06-10" },
];

const DEMO_WORKFLOW: ApprovalWorkflow[] = [
  { step: "Demand Review", status: "completed", assigned_to: "Sales Team", completed_at: "2024-06-15" },
  { step: "Supply Review", status: "completed", assigned_to: "Operations", completed_at: "2024-06-16" },
  { step: "Financial Review", status: "in_progress", assigned_to: "Finance Team" },
  { step: "Executive Approval", status: "pending", assigned_to: "CEO" },
];

const DEMO_FINANCIAL_DATA: FinancialIntegration[] = [
  { period: "2024-01", revenue: 1250000, cost: 850000, margin: 32.0, budget_variance: 2.5 },
  { period: "2024-02", revenue: 1320000, cost: 890000, margin: 32.6, budget_variance: 3.1 },
  { period: "2024-03", revenue: 1280000, cost: 870000, margin: 32.0, budget_variance: 1.8 },
  { period: "2024-04", revenue: 1350000, cost: 910000, margin: 32.6, budget_variance: 2.9 },
  { period: "2024-05", revenue: 1400000, cost: 940000, margin: 32.9, budget_variance: 3.5 },
];

/* ── Page ── */
export default function SOPDashboardPage() {
  const router = useRouter();
  const { showToast } = useToast();

  const { data: sopMetrics, loading: l1 } = useApi<SOPMetrics>("/sop/metrics", { fallback: DEMO_SOP_METRICS });
  const { data: consensusData, loading: l2 } = useApi<ConsensusData[]>("/sop/consensus", { fallback: DEMO_CONSENSUS_DATA });
  const { data: scenarios, loading: l3 } = useApi<Scenario[]>("/sop/scenarios", { fallback: DEMO_SCENARIOS });
  const { data: workflow, loading: l4 } = useApi<ApprovalWorkflow[]>("/sop/workflow", { fallback: DEMO_WORKFLOW });
  const { data: financialData, loading: l5 } = useApi<FinancialIntegration[]>("/sop/financial", { fallback: DEMO_FINANCIAL_DATA });

  const loading = l1 || l2 || l3 || l4 || l5;

  // Derived data for charts
  const consensusChartData = useMemo(() => {
    if (!consensusData) return [];
    return consensusData.map(d => ({
      period: d.period,
      Sales: d.sales_forecast,
      Marketing: d.marketing_forecast,
      Finance: d.finance_forecast,
      Operations: d.operations_forecast,
      Consensus: d.consensus_forecast,
      Actual: d.actual_demand
    }));
  }, [consensusData]);

  const varianceData = useMemo(() => {
    if (!consensusData) return [];
    return consensusData.map(d => ({
      period: d.period,
      Variance: Math.abs(d.consensus_forecast - d.actual_demand),
      Accuracy: ((1 - Math.abs(d.consensus_forecast - d.actual_demand) / d.actual_demand) * 100).toFixed(1)
    }));
  }, [consensusData]);

  const financialChartData = useMemo(() => {
    if (!financialData) return [];
    return financialData.map(d => ({
      period: d.period,
      Revenue: d.revenue,
      Cost: d.cost,
      Margin: d.margin
    }));
  }, [financialData]);

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            <div className="kpi-grid">
              {[...Array(6)].map((_, i) => (
                <div key={i} style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20, height: 96 }} />
              ))}
            </div>
            <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, height: 400 }} />
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

          {/* ══ Page Header ══ */}
          <div style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            paddingBottom: 16,
            marginBottom: 24,
            borderBottom: "1px solid var(--color-border)",
          }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>
                Sales & Operations Planning
              </div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                Executive Dashboard
              </h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>
                Cross-functional consensus planning and financial integration
              </p>
            </div>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <button
                className="btn btn-secondary"
                onClick={() => router.push("/dashboard")}
              >
                Back to Command Center
              </button>
              <button
                className="btn btn-primary"
                onClick={() => showToast("Creating new S&OP cycle...", "info")}
              >
                New Planning Cycle
              </button>
            </div>
          </div>

          {/* ══ KPI Grid ══ */}
          <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
            <KpiCard
              label="Forecast Accuracy"
              value={`${sopMetrics?.forecast_accuracy?.toFixed(1) ?? 0}%`}
              delta="Target: 90%"
              deltaDir={sopMetrics?.forecast_accuracy >= 90 ? "up" : "neutral"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
            <KpiCard
              label="Demand Variance"
              value={`${sopMetrics?.demand_variance?.toFixed(1) ?? 0}%`}
              delta="vs previous cycle"
              deltaDir={sopMetrics?.demand_variance <= 10 ? "up" : "down"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
            <KpiCard
              label="Supply Variance"
              value={`${sopMetrics?.supply_variance?.toFixed(1) ?? 0}%`}
              delta="capacity utilization"
              deltaDir={sopMetrics?.supply_variance <= 8 ? "up" : "neutral"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
            <KpiCard
              label="Inventory Turnover"
              value={sopMetrics?.inventory_turnover?.toFixed(1) ?? 0}
              delta="per annum"
              deltaDir={sopMetrics?.inventory_turnover >= 4 ? "up" : "neutral"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
            <KpiCard
              label="Service Level"
              value={`${sopMetrics?.customer_service_level?.toFixed(1) ?? 0}%`}
              delta="OTIF metric"
              deltaDir={sopMetrics?.customer_service_level >= 95 ? "up" : "neutral"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
            <KpiCard
              label="Revenue Alignment"
              value={`${sopMetrics?.revenue_alignment?.toFixed(1) ?? 0}%`}
              delta="budget alignment"
              deltaDir={sopMetrics?.revenue_alignment >= 90 ? "up" : "neutral"}
              loading={l1}
              noData={!sopMetrics && !l1}
            />
          </div>

          {/* ══ Main Content Grid ══ */}
          <div className="dashboard-layout">

            {/* ── Left Column ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Consensus Forecast Chart */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Consensus Forecast Comparison</SectionLabel>
                {consensusChartData.length > 0 ? (
                  <SynLineChart
                    data={consensusChartData}
                    lines={[
                      { key: "Sales", color: "#3B82F6", name: "Sales" },
                      { key: "Marketing", color: "#8B5CF6", name: "Marketing" },
                      { key: "Finance", color: "#10B981", name: "Finance" },
                      { key: "Operations", color: "#F59E0B", name: "Operations" },
                      { key: "Consensus", color: "#EF4444", name: "Consensus" },
                      { key: "Actual", color: "#000000", name: "Actual" },
                    ]}
                    xKey="period"
                    height={300}
                  />
                ) : (
                  <NoData msg="No consensus data available" />
                )}
              </div>

              {/* Variance Analysis */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Forecast Variance Analysis</SectionLabel>
                {varianceData.length > 0 ? (
                  <SynBarChart
                    data={varianceData}
                    dataKey="Variance"
                    nameKey="period"
                    color="#FF9500"
                    height={250}
                  />
                ) : (
                  <NoData msg="No variance data available" />
                )}
              </div>

              {/* Financial Integration */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Financial Performance</SectionLabel>
                {financialChartData.length > 0 ? (
                  <SynLineChart
                    data={financialChartData}
                    lines={[
                      { key: "Revenue", color: "#10B981", name: "Revenue" },
                      { key: "Cost", color: "#EF4444", name: "Cost" },
                      { key: "Margin", color: "#3B82F6", name: "Margin %" },
                    ]}
                    xKey="period"
                    height={250}
                  />
                ) : (
                  <NoData msg="No financial data available" />
                )}
              </div>

            </div>

            {/* ── Right Column ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Approval Workflow */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Approval Workflow</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {workflow?.map((step, index) => (
                    <div key={index} style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      padding: "12px",
                      background: step.status === "completed" ? "var(--color-surface-2)" : "transparent",
                      borderRadius: 4,
                      border: step.status === "in_progress" ? "1px solid var(--color-accent)" : "1px solid var(--color-border)",
                    }}>
                      <div style={{
                        width: 24,
                        height: 24,
                        borderRadius: "50%",
                        background: step.status === "completed" ? "#10B981" : step.status === "in_progress" ? "#FF9500" : "#E5E7EB",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontSize: 12,
                        fontWeight: 600,
                      }}>
                        {step.status === "completed" ? "✓" : index + 1}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                          {step.step}
                        </div>
                        <div style={{ fontSize: 11, color: "var(--color-text-3)" }}>
                          {step.assigned_to}
                        </div>
                      </div>
                      <div style={{
                        fontSize: 11,
                        padding: "4px 8px",
                        borderRadius: 4,
                        background: step.status === "completed" ? "#D1FAE5" : step.status === "in_progress" ? "#FEF3C7" : "#F3F4F6",
                        color: step.status === "completed" ? "#065F46" : step.status === "in_progress" ? "#92400E" : "#6B7280",
                        fontWeight: 500,
                      }}>
                        {step.status}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Scenarios */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Active Scenarios</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {scenarios?.map((scenario) => (
                    <div key={scenario.id} style={{
                      padding: "12px",
                      background: "var(--color-surface-2)",
                      borderRadius: 4,
                      border: "1px solid var(--color-border)",
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                        <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                          {scenario.name}
                        </div>
                        <div style={{
                          fontSize: 10,
                          padding: "2px 6px",
                          borderRadius: 3,
                          background: scenario.impact === "high" ? "#FEE2E2" : "#FEF3C7",
                          color: scenario.impact === "high" ? "#991B1B" : "#92400E",
                          fontWeight: 500,
                        }}>
                          {scenario.impact.toUpperCase()}
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 8, fontSize: 11, color: "var(--color-text-3)" }}>
                        <span>{scenario.type}</span>
                        <span>•</span>
                        <span>{(scenario.probability * 100).toFixed(0)}% probability</span>
                        <span>•</span>
                        <span>{scenario.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  className="btn btn-secondary btn-sm"
                  style={{ marginTop: 12, width: "100%" }}
                  onClick={() => showToast("Scenario management coming soon", "info")}
                >
                  Manage Scenarios
                </button>
              </div>

              {/* Performance Metrics */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Performance Tracking</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--color-text-2)" }}>Planning Cycle Time</span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-1)" }}>5 days</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--color-text-2)" }}>Cross-functional Alignment</span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-1)" }}>92%</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--color-text-2)" }}>Decision Quality Score</span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-1)" }}>8.5/10</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--color-text-2)" }}>Exception Rate</span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-1)" }}>3.2%</span>
                  </div>
                </div>
              </div>

            </div>

          </div>

        </main>
      </div>
    </div>
  );
}
