"use client";

import { useMemo, useState } from "react";
import { GitBranch, Play, Plus, Workflow } from "lucide-react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { KpiCard } from "../components/Cards/KpiCard";
import { SectionLabel } from "../components/Cards/SectionLabel";
import { useApi } from "../../hooks/useApi";
import { apiPostJSON } from "@/lib/api";
import { useToast } from "../components/feedback/ToastContext";
import Link from "next/link";

type Template = { name: string; steps: string[]; cadence: string };
type Overview = {
  data_flow: { records_available: number; automation_state: string; sources: string[] };
  process_templates: Record<string, Template>;
  scenario_count: number;
  ui_modules: { name: string; path: string; status: string }[];
};

const FALLBACK: Overview = {
  data_flow: { records_available: 0, automation_state: "waiting_for_data", sources: [] },
  process_templates: {
    monthly_ibp: { name: "Monthly IBP Cycle", cadence: "monthly", steps: ["data_refresh", "demand_review", "supply_review", "executive_sop"] },
  },
  scenario_count: 0,
  ui_modules: [],
};

export default function IBPUnifiedPage() {
  const { showToast } = useToast();
  const { data: overview, retry } = useApi<Overview>("/ibp-orchestrator/overview", { fallback: FALLBACK });
  const [templateId, setTemplateId] = useState("monthly_ibp");
  const [scenarioName, setScenarioName] = useState("Demand upside scenario");
  const [runResult, setRunResult] = useState<{ steps?: { step: string; status: string }[] } | null>(null);
  const [runningFlow, setRunningFlow] = useState(false);
  const [creatingScenario, setCreatingScenario] = useState(false);

  const templates = overview?.process_templates ?? {};
  const selectedTemplate = templates[templateId] ?? Object.values(templates)[0];
  const sourcesLabel = useMemo(() => (overview?.data_flow.sources ?? []).slice(0, 3).join(", ") || "No sources connected", [overview]);
  const displaySteps = runResult?.steps ?? selectedTemplate?.steps.map((step) => ({ step, status: "not_started" })) ?? [];

  const runFlow = async () => {
    setRunningFlow(true);
    try {
      const result = await apiPostJSON<{ steps: { step: string; status: string }[] }>("/ibp-orchestrator/data-flow/run", { template_id: templateId });
      setRunResult(result);
      showToast("IBP data flow completed", "success");
    } catch (error) {
      showToast(error instanceof Error ? error.message : "Unable to run IBP data flow", "error");
    } finally {
      setRunningFlow(false);
    }
  };

  const createScenario = async () => {
    const name = scenarioName.trim();
    if (!name) {
      showToast("Scenario name is required.", "warning");
      return;
    }
    setCreatingScenario(true);
    try {
      await apiPostJSON("/ibp-orchestrator/scenarios", {
        name,
        scenario_type: "what_if",
        assumptions: { demand_change_pct: 8, supply_change_pct: 3, cost_change_pct: 2 },
      });
      showToast("Scenario created", "success");
      retry();
    } catch (error) {
      showToast(error instanceof Error ? error.message : "Unable to create scenario", "error");
    } finally {
      setCreatingScenario(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, paddingBottom: 16, marginBottom: 24, borderBottom: "1px solid var(--color-border)", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 4 }}>Integrated Business Planning</div>
              <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)" }}>Unified IBP Workspace</h1>
              <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>Coordinate planning templates, data flows, and scenarios in one operational view.</p>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <button className="btn btn-secondary btn-sm" onClick={createScenario} disabled={creatingScenario}>
                <Plus size={14} /> {creatingScenario ? "Creating..." : "Scenario"}
              </button>
              <button className="btn btn-primary btn-sm" onClick={runFlow} disabled={runningFlow}>
                <Play size={14} /> {runningFlow ? "Running..." : "Run Flow"}
              </button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginBottom: 24 }}>
            <KpiCard label="Records Available" value={(overview?.data_flow.records_available ?? 0).toLocaleString()} delta={sourcesLabel} deltaDir="neutral" />
            <KpiCard label="Automation State" value={overview?.data_flow.automation_state ?? "ready"} delta="Data flow orchestration" deltaDir="up" />
            <KpiCard label="Templates" value={Object.keys(templates).length} delta="Reusable processes" deltaDir="up" />
            <KpiCard label="Scenarios" value={overview?.scenario_count ?? 0} delta="What-if workspace" deltaDir="neutral" />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 16, alignItems: "start" }}>
            <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20 }}>
              <SectionLabel>Process Templates</SectionLabel>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 14 }}>
                {Object.entries(templates).map(([id, template]) => (
                  <button key={id} className="btn-text" onClick={() => setTemplateId(id)} style={{ textAlign: "left", padding: 12, borderRadius: 4, background: templateId === id ? "var(--color-surface-2)" : "transparent", border: "1px solid var(--color-border)" }}>
                    <Workflow size={14} /> {template.name}
                  </button>
                ))}
              </div>
              <input value={scenarioName} onChange={(event) => setScenarioName(event.target.value)} style={{ width: "100%", height: 36, marginTop: 16, border: "1px solid var(--color-border)", borderRadius: 4, background: "var(--color-surface-2)", color: "var(--color-text-1)", padding: "0 10px" }} />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20 }}>
                <SectionLabel>{selectedTemplate?.name ?? "Template Flow"}</SectionLabel>
                <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
                  {displaySteps.map((step, index) => (
                    <div key={step.step} style={{ display: "flex", alignItems: "center", gap: 10, padding: 12, border: "1px solid var(--color-border)", borderRadius: 4 }}>
                      <GitBranch size={14} color={step.status === "completed" ? "#10B981" : step.status === "not_started" ? "#9CA3AF" : "#6B7280"} />
                      <span style={{ flex: 1, fontSize: 13, color: "var(--color-text-1)" }}>{index + 1}. {step.step.replaceAll("_", " ")}</span>
                      <span style={{ fontSize: 11, color: step.status === "not_started" ? "#9CA3AF" : "var(--color-text-3)" }}>{step.status === "not_started" ? "not run" : step.status}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", borderRadius: 6, padding: 20 }}>
                <SectionLabel>Unified Modules</SectionLabel>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10, marginTop: 14 }}>
                  {(overview?.ui_modules ?? []).map((module) => (
                    <Link key={module.path} href={module.path} style={{ padding: 12, border: "1px solid var(--color-border)", borderRadius: 4, color: "var(--color-text-1)", textDecoration: "none" }}>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>{module.name}</div>
                      <div style={{ fontSize: 11, color: "var(--color-text-3)", marginTop: 2 }}>{module.status}</div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
