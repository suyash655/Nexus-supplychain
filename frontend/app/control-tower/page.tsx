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
import { AlertTriangle, CheckCircle, Activity, TrendingUp, TrendingDown, GitBranch, Radar, Users } from "lucide-react";
import dynamic from "next/dynamic";
import { API_BASE, apiFetchJSON, apiPostJSON } from "@/lib/api";

const SynAreaChart = dynamic(() => import("../components/charts/Charts").then(m => ({ default: m.SynAreaChart })), { ssr: false, loading: () => <div className="skeleton skeleton-chart" style={{ height: 260 }} /> });

/* ── Types ── */
type ControlTowerMetrics = {
  total_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  info_alerts: number;
  resolved_today: number;
  avg_resolution_time: number;
  system_health: number;
  active_incidents: number;
};

type Alert = {
  id: string;
  severity: "critical" | "warning" | "info";
  type: string;
  description: string;
  source: string;
  timestamp: string;
  status: "active" | "acknowledged" | "resolved";
  assigned_to?: string;
  resolution_time?: number;
};

type PerformanceMetric = {
  metric: string;
  current: number;
  target: number;
  trend: "up" | "down" | "stable";
  period: string;
};

type SystemHealth = {
  component: string;
  status: "healthy" | "degraded" | "down";
  uptime: number;
  last_check: string;
  metrics: Record<string, number>;
};

type Incident = {
  id: string;
  incident_type: string;
  severity: "critical" | "high" | "medium" | "low";
  priority: "critical" | "high" | "medium" | "low";
  status: "open" | "acknowledged" | "investigating" | "resolved" | "closed";
  title: string;
  description: string;
  assigned_to?: string;
  assigned_team?: string;
  created_at: string;
  updated_at: string;
  escalation_level: number;
  timeline: Array<{
    action: string;
    timestamp: string;
    user: string;
    details: string;
  }>;
  affected_entities?: Record<string, unknown>;
};

type RootCauseHypothesis = {
  root_cause?: string;
  hypothesis?: string;
  confidence?: number;
  impact?: string;
};

type CorrelationSummary = {
  correlation_results?: {
    correlated_groups?: unknown[];
    root_cause_hypotheses?: RootCauseHypothesis[];
  };
};

type PredictiveAlert = {
  alert_type?: string;
  severity?: string;
  confidence?: number;
  message?: string;
};

type PredictiveAlertResponse = {
  predictive_alerts?: PredictiveAlert[];
  alerts?: PredictiveAlert[];
};

type IncidentResponse = {
  incidents?: Incident[];
};

/* ── Demo Data ── */
const DEMO_CONTROL_TOWER_METRICS: ControlTowerMetrics = {
  total_alerts: 47,
  critical_alerts: 3,
  warning_alerts: 12,
  info_alerts: 32,
  resolved_today: 28,
  avg_resolution_time: 2.4,
  system_health: 94.5,
  active_incidents: 2
};

const DEMO_ALERTS: Alert[] = [
  {
    id: "ALT-001",
    severity: "critical",
    type: "SUPPLIER_DELAY",
    description: "Supplier Alpha delayed by 7 days - critical path impact",
    source: "Demand Planning Engine",
    timestamp: "2024-06-26T10:30:00Z",
    status: "active",
    assigned_to: "Supply Chain Manager"
  },
  {
    id: "ALT-002",
    severity: "critical",
    type: "INVENTORY_SHORTAGE",
    description: "SKU-12345 stock below safety stock threshold",
    source: "Inventory Optimization",
    timestamp: "2024-06-26T09:15:00Z",
    status: "active",
    assigned_to: "Inventory Manager"
  },
  {
    id: "ALT-003",
    severity: "warning",
    type: "DEMAND_VARIANCE",
    description: "Regional demand variance exceeded 15% threshold",
    source: "S&OP Engine",
    timestamp: "2024-06-26T08:45:00Z",
    status: "acknowledged",
    assigned_to: "Demand Planner"
  },
  {
    id: "ALT-004",
    severity: "warning",
    type: "CAPACITY_CONSTRAINT",
    description: "Production capacity utilization at 92%",
    source: "Supply Planning",
    timestamp: "2024-06-26T07:30:00Z",
    status: "active"
  },
  {
    id: "ALT-005",
    severity: "info",
    type: "SYSTEM_UPDATE",
    description: "Scheduled system maintenance completed successfully",
    source: "System",
    timestamp: "2024-06-26T06:00:00Z",
    status: "resolved",
    resolution_time: 45
  },
];

const DEMO_PERFORMANCE_METRICS: PerformanceMetric[] = [
  { metric: "OTIF Rate", current: 94.2, target: 95.0, trend: "up", period: "Current Week" },
  { metric: "Forecast Accuracy", current: 87.5, target: 90.0, trend: "stable", period: "Current Month" },
  { metric: "Inventory Turnover", current: 4.2, target: 4.5, trend: "up", period: "Current Quarter" },
  { metric: "Supplier On-Time", current: 91.8, target: 93.0, trend: "down", period: "Current Week" },
];

const DEMO_SYSTEM_HEALTH: SystemHealth[] = [
  {
    component: "Demand Planning Engine",
    status: "healthy",
    uptime: 99.8,
    last_check: "2024-06-26T10:35:00Z",
    metrics: { cpu: 45, memory: 62, response_time: 120 }
  },
  {
    component: "Supply Planning Engine",
    status: "healthy",
    uptime: 99.9,
    last_check: "2024-06-26T10:35:00Z",
    metrics: { cpu: 38, memory: 55, response_time: 95 }
  },
  {
    component: "Inventory Optimization",
    status: "degraded",
    uptime: 98.5,
    last_check: "2024-06-26T10:34:00Z",
    metrics: { cpu: 78, memory: 85, response_time: 280 }
  },
  {
    component: "Control Tower Service",
    status: "healthy",
    uptime: 99.7,
    last_check: "2024-06-26T10:35:00Z",
    metrics: { cpu: 25, memory: 40, response_time: 65 }
  },
];

const DEMO_ALERT_TREND = [
  { period: "00:00", critical: 1, warning: 3, info: 5 },
  { period: "04:00", critical: 0, warning: 2, info: 4 },
  { period: "08:00", critical: 2, warning: 5, info: 8 },
  { period: "12:00", critical: 1, warning: 4, info: 6 },
  { period: "16:00", critical: 3, warning: 6, info: 9 },
  { period: "20:00", critical: 1, warning: 3, info: 5 },
];

/* ── Page ── */
export default function ControlTowerPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [liveAlerts, setLiveAlerts] = useState<Alert[]>(DEMO_ALERTS);
  const [liveMetrics, setLiveMetrics] = useState<ControlTowerMetrics>(DEMO_CONTROL_TOWER_METRICS);
  const [correlationSummary, setCorrelationSummary] = useState<CorrelationSummary | null>(null);
  const [predictiveAlerts, setPredictiveAlerts] = useState<PredictiveAlert[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isMobile, setIsMobile] = useState(false);
  const [viewMode, setViewMode] = useState<"dashboard" | "alerts" | "incidents">("dashboard");
  const [actionBusy, setActionBusy] = useState<string | null>(null);

  // Mobile detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const { data: metrics, loading: l1 } = useApi<ControlTowerMetrics>("/control-tower/metrics", { fallback: DEMO_CONTROL_TOWER_METRICS });
  const { data: alerts, loading: l2 } = useApi<Alert[]>("/control-tower/alerts", { fallback: DEMO_ALERTS });
  const { data: performanceMetrics, loading: l3 } = useApi<PerformanceMetric[]>("/control-tower/performance", { fallback: DEMO_PERFORMANCE_METRICS });
  const { data: systemHealth, loading: l4 } = useApi<SystemHealth[]>("/control-tower/health", { fallback: DEMO_SYSTEM_HEALTH });

  const loading = l1 || l2 || l3 || l4;
  const dashboardMetrics = liveMetrics ?? metrics ?? DEMO_CONTROL_TOWER_METRICS;
  const isDemoMode = metrics === DEMO_CONTROL_TOWER_METRICS && !liveMetrics;

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!autoRefresh) return;

    let ws: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout | null = null;

    const connectWebSocket = () => {
      try {
        const wsBase = API_BASE.replace(/^http/, "ws").replace(/\/$/, "");
        const wsUrl = `${wsBase}/ws/control-tower?client_id=ct_${Date.now()}`;
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log("Control Tower WebSocket connected");
          setIsWebSocketConnected(true);
          showToast("Real-time updates enabled", "success");
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            
            switch (message.type) {
              case "control_tower_connected":
                console.log("WebSocket connection confirmed:", message.data);
                break;
              
              case "initial_alerts":
                if (message.data?.active_alerts) {
                  setLiveAlerts(message.data.active_alerts);
                }
                break;
              
              case "alert_update":
                if (message.data?.recent_alerts) {
                  setLiveAlerts(prev => [...message.data.recent_alerts, ...prev].slice(0, 50));
                }
                if (message.data?.active_alerts !== undefined) {
                  setLiveMetrics(prev => ({ ...prev, total_alerts: message.data.active_alerts }));
                }
                break;
              
              case "metric_update":
                if (message.data?.system_health !== undefined) {
                  setLiveMetrics(prev => ({ ...prev, system_health: message.data.system_health }));
                }
                if (message.data?.active_incidents !== undefined) {
                  setLiveMetrics(prev => ({ ...prev, active_incidents: message.data.active_incidents }));
                }
                break;

              case "dashboard_snapshot":
                if (message.data?.alerts?.recent) {
                  setLiveAlerts(message.data.alerts.recent);
                }
                if (message.data?.health_score !== undefined) {
                  setLiveMetrics(prev => ({ ...prev, system_health: message.data.health_score }));
                }
                if (message.data?.incidents?.active_count !== undefined) {
                  setLiveMetrics(prev => ({ ...prev, active_incidents: message.data.incidents.active_count }));
                }
                break;
              
              case "keepalive":
                // Connection is alive, no action needed
                break;
              
              case "error":
                setIsWebSocketConnected(false);
                break;
              
              default:
                console.log("Unknown WebSocket message type:", message.type);
            }
          } catch {
            setIsWebSocketConnected(false);
          }
        };

        ws.onerror = () => {
          setIsWebSocketConnected(false);
        };

        ws.onclose = () => {
          setIsWebSocketConnected(false);
          
          // Attempt to reconnect after 5 seconds
          if (autoRefresh) {
            reconnectTimer = setTimeout(() => {
              connectWebSocket();
            }, 5000);
          }
        };
      } catch {
        setIsWebSocketConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [autoRefresh, showToast]);

  // Filter alerts by severity
  const filteredAlerts = useMemo(() => {
    const sourceAlerts = liveAlerts?.length ? liveAlerts : alerts ?? [];
    if (selectedSeverity === "all") return sourceAlerts;
    return sourceAlerts.filter(alert => alert.severity === selectedSeverity);
  }, [alerts, liveAlerts, selectedSeverity]);

  useEffect(() => {
    const loadAdvancedControlTower = async () => {
      try {
        const [correlationData, predictiveData, incidentData] = await Promise.all([
          apiPostJSON<CorrelationSummary>("/control-tower/correlation-analysis", { time_window_hours: 24 }),
          apiPostJSON<PredictiveAlertResponse>("/control-tower/predictive-alerts", { look_ahead_days: 7 }),
          apiFetchJSON<IncidentResponse>("/control-tower/incidents"),
        ]);
        setCorrelationSummary(correlationData);
        setPredictiveAlerts(predictiveData.predictive_alerts ?? predictiveData.alerts ?? []);
        setIncidents(incidentData.incidents ?? []);
      } catch {
        setCorrelationSummary({
          correlation_results: {
            correlated_groups: [],
            root_cause_hypotheses: [{ root_cause: "Supplier delay clustering", confidence: 0.72, impact: "Inventory and OTIF risk" }],
          },
        });
        setPredictiveAlerts([
          { alert_type: "predictive_delay", severity: "warning", confidence: 0.76, message: "Delay risk likely to increase in the next 7 days" },
        ]);
      }
    };

    loadAdvancedControlTower();
  }, []);

  // Auto-refresh simulation
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      // In production, this would trigger actual API calls
      console.log("Auto-refreshing Control Tower data...");
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleAcknowledgeAlert = async (alertId: string) => {
    setActionBusy(`ack-${alertId}`);
    try {
      await apiPostJSON(`/control-tower/alerts/${alertId}/acknowledge`, { user: "operator" });
      setLiveAlerts((prev) => prev.map((alert) => alert.id === alertId ? { ...alert, status: "acknowledged" } : alert));
      showToast(`Alert ${alertId} acknowledged`, "success");
    } catch (error) {
      showToast(error instanceof Error ? error.message : `Could not acknowledge ${alertId}`, "error");
    } finally {
      setActionBusy(null);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    setActionBusy(`resolve-${alertId}`);
    try {
      await apiPostJSON(`/control-tower/alerts/${alertId}/resolve`, { user: "operator", resolution_notes: "Resolved from Control Tower UI" });
      setLiveAlerts((prev) => prev.map((alert) => alert.id === alertId ? { ...alert, status: "resolved" } : alert));
      showToast(`Alert ${alertId} marked as resolved`, "success");
    } catch (error) {
      showToast(error instanceof Error ? error.message : `Could not resolve ${alertId}`, "error");
    } finally {
      setActionBusy(null);
    }
  };

  const createIncidentFromTopAlert = async () => {
    const alert = filteredAlerts[0];
    if (!alert) {
      showToast("No alert is available to convert into an incident.", "warning");
      return;
    }
    setActionBusy("incident-report");
    try {
      const result = await apiPostJSON<{ incident?: Incident }>("/control-tower/incidents", {
        incident_type: alert.type,
        severity: alert.severity === "info" ? "low" : alert.severity,
        priority: alert.severity === "critical" ? "critical" : "medium",
        description: alert.description,
        affected_entities: { source: alert.source },
        assigned_to: alert.assigned_to,
        related_alerts: [alert.id],
        tags: ["generated-from-alert"],
      });
      if (result.incident) {
        setIncidents((prev) => [result.incident as Incident, ...prev]);
      }
      setViewMode("incidents");
      showToast("Incident report generated.", "success");
    } catch (error) {
      showToast(error instanceof Error ? error.message : "Unable to generate incident report", "error");
    } finally {
      setActionBusy(null);
    }
  };

  const escalateLatestIncident = async () => {
    const incident = incidents[0];
    const incidentId = incident?.id ?? (incident as any)?.incident_id;
    if (!incidentId) {
      showToast("No incident is available to escalate.", "warning");
      return;
    }
    setActionBusy("escalate-incident");
    try {
      await apiPostJSON(`/control-tower/incidents/${incidentId}/escalate`, {});
      setIncidents((prev) => prev.map((item, index) => index === 0 ? { ...item, escalation_level: (item.escalation_level ?? 0) + 1, priority: "high" } : item));
      showToast(`Incident ${incidentId} escalated.`, "success");
    } catch (error) {
      showToast(error instanceof Error ? error.message : "Unable to escalate incident", "error");
    } finally {
      setActionBusy(null);
    }
  };

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            <div className="kpi-grid">
              {[...Array(4)].map((_, i) => (
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

          {/* ══ Mobile Header ══ */}
          {isMobile && (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              paddingBottom: 16,
              marginBottom: 16,
              borderBottom: "1px solid var(--color-border)",
            }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                  Control Tower
                </h1>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: isWebSocketConnected ? "#10B981" : "#EF4444",
                  }}
                />
              </div>
            </div>
          )}

          {/* ══ Desktop Page Header ══ */}
          {!isMobile && (
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
                  Real-time Monitoring
                </div>
                <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)", lineHeight: 1.2 }}>
                  Control Tower
                </h1>
                <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 2 }}>
                  Real-time alert management and performance monitoring
                </p>
              </div>
              <div style={{ display: "flex", gap: 8, flexShrink: 0, alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 12, color: "var(--color-text-3)" }}>Auto-refresh</span>
                  <button
                    onClick={() => setAutoRefresh(!autoRefresh)}
                    style={{
                      width: 40,
                      height: 20,
                      borderRadius: 10,
                      background: autoRefresh ? "var(--color-accent)" : "var(--color-border)",
                      border: "none",
                      cursor: "pointer",
                      position: "relative",
                      transition: "background 200ms ease"
                    }}
                  >
                    <div style={{
                      width: 16,
                      height: 16,
                      borderRadius: "50%",
                      background: "white",
                      position: "absolute",
                      top: 2,
                      left: autoRefresh ? 22 : 2,
                      transition: "left 200ms ease"
                    }} />
                  </button>
                </div>
                <button
                  className="btn btn-secondary"
                  onClick={() => router.push("/dashboard")}
                >
                  Back to Command Center
                </button>
              </div>
            </div>
          )}

          {/* ══ Mobile View Navigation ══ */}
          {isMobile && (
            <div style={{
              display: "flex",
              gap: 8,
              marginBottom: 16,
              overflowX: "auto",
              paddingBottom: 4,
            }}>
              {(["dashboard", "alerts", "incidents"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className="btn-text"
                  style={{
                    fontSize: 12,
                    padding: "8px 16px",
                    borderRadius: 20,
                    background: viewMode === mode ? "var(--color-accent)" : "var(--color-surface-2)",
                    color: viewMode === mode ? "white" : "var(--color-text-1)",
                    border: viewMode === mode ? "none" : "1px solid var(--color-border)",
                    whiteSpace: "nowrap",
                    fontWeight: viewMode === mode ? 500 : 400,
                  }}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          )}

          {/* Demo mode notice */}
          {isDemoMode && (
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

          {/* ══ KPI Grid ══ */}
          <div className="kpi-grid" style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "repeat(2, 1fr)" : "repeat(4, 1fr)",
            gap: isMobile ? 12 : 16,
            marginBottom: isMobile ? 16 : 24,
          }}>
            <KpiCard
              label="Active Alerts"
              value={dashboardMetrics.total_alerts ?? 0}
              delta={`${dashboardMetrics.critical_alerts ?? 0} critical`}
              deltaDir={dashboardMetrics.critical_alerts === 0 ? "up" : "down"}
              loading={l1}
              noData={!metrics && !l1}
            />
            <KpiCard
              label="System Health"
              value={`${dashboardMetrics.system_health?.toFixed(1) ?? 0}%`}
              delta={isWebSocketConnected ? "Live stream connected" : "Polling fallback"}
              deltaDir={dashboardMetrics.system_health >= 95 ? "up" : "neutral"}
              loading={l1}
              noData={!metrics && !l1}
            />
            <KpiCard
              label="Resolved Today"
              value={dashboardMetrics.resolved_today ?? 0}
              delta="Avg time: 2.4h"
              deltaDir="up"
              loading={l1}
              noData={!metrics && !l1}
            />
            <KpiCard
              label="Active Incidents"
              value={dashboardMetrics.active_incidents ?? 0}
              delta="Being managed"
              deltaDir={dashboardMetrics.active_incidents === 0 ? "up" : "neutral"}
              loading={l1}
              noData={!metrics && !l1}
            />
          </div>

          {/* ══ Main Content Grid ══ */}
          <div className="dashboard-layout" style={{
            display: isMobile ? "block" : "grid",
            gridTemplateColumns: isMobile ? "auto" : "1fr 1fr",
            gap: isMobile ? 16 : 24,
          }}>

            {/* ── Left Column ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: isMobile ? 12 : 16 }}>

              {/* Alert Feed */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: isMobile ? 16 : 20,
              }}>
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: isMobile ? 12 : 16,
                  flexWrap: isMobile ? "wrap" : "nowrap",
                  gap: isMobile ? 8 : 0,
                }}>
                  <SectionLabel>Live Alert Feed</SectionLabel>
                  <div style={{ 
                    display: "flex", 
                    gap: 8,
                    flexWrap: isMobile ? "wrap" : "nowrap"
                  }}>
                    {["all", "critical", "warning", "info"].map((severity) => (
                      <button
                        key={severity}
                        onClick={() => setSelectedSeverity(severity)}
                        className="btn-text"
                        style={{
                          fontSize: isMobile ? 10 : 11,
                          padding: isMobile ? "4px 8px" : "4px 8px",
                          borderRadius: 4,
                          background: selectedSeverity === severity ? "var(--color-surface-2)" : "transparent",
                          border: selectedSeverity === severity ? "1px solid var(--color-border)" : "1px solid transparent",
                          fontWeight: selectedSeverity === severity ? 500 : 400,
                        }}
                      >
                        {severity.charAt(0).toUpperCase() + severity.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {filteredAlerts.length > 0 ? (
                    filteredAlerts.map((alert) => (
                      <div
                        key={alert.id}
                        style={{
                          padding: "12px",
                          background: alert.status === "active" ? "var(--color-surface-2)" : "transparent",
                          borderRadius: 4,
                          border: `1px solid ${alert.severity === "critical" ? "#FEE2E2" : alert.severity === "warning" ? "#FEF3C7" : "#E5E7EB"}`,
                          borderLeft: `3px solid ${alert.severity === "critical" ? "#EF4444" : alert.severity === "warning" ? "#FF9500" : "#3B82F6"}`,
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            {alert.severity === "critical" && <AlertTriangle size={14} color="#EF4444" />}
                            {alert.severity === "warning" && <AlertTriangle size={14} color="#FF9500" />}
                            {alert.severity === "info" && <Activity size={14} color="#3B82F6" />}
                            <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                              {alert.type}
                            </span>
                          </div>
                          <div style={{
                            fontSize: 10,
                            padding: "2px 6px",
                            borderRadius: 3,
                            background: alert.status === "active" ? "#FEE2E2" : alert.status === "acknowledged" ? "#FEF3C7" : "#D1FAE5",
                            color: alert.status === "active" ? "#991B1B" : alert.status === "acknowledged" ? "#92400E" : "#065F46",
                            fontWeight: 500,
                          }}>
                            {alert.status}
                          </div>
                        </div>
                        <div style={{ fontSize: 12, color: "var(--color-text-2)", marginBottom: 8 }}>
                          {alert.description}
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <div style={{ fontSize: 11, color: "var(--color-text-3)" }}>
                            {alert.source} • {new Date(alert.timestamp).toLocaleString()}
                          </div>
                          {alert.status === "active" && (
                            <div style={{ display: "flex", gap: 8 }}>
                              <button
                                className="btn-text"
                                style={{ fontSize: 11 }}
                                onClick={() => handleAcknowledgeAlert(alert.id)}
                              >
                                Acknowledge
                              </button>
                              <button
                                className="btn-text"
                                style={{ fontSize: 11 }}
                                onClick={() => handleResolveAlert(alert.id)}
                              >
                                Resolve
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <NoData msg="No alerts matching current filter" />
                  )}
                </div>
              </div>

              {/* Alert Trend Chart */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Alert Trend (24h)</SectionLabel>
                <SynAreaChart
                  data={DEMO_ALERT_TREND}
                  dataKey="critical"
                  xKey="period"
                  color="#EF4444"
                  height={200}
                />
              </div>

              {(!isMobile || viewMode === "dashboard") && (
                <div style={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 6,
                  padding: isMobile ? 16 : 20,
                }}>
                  <SectionLabel>Correlation & Root Cause</SectionLabel>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
                    {(correlationSummary?.correlation_results?.root_cause_hypotheses ?? []).slice(0, 3).map((cause, index: number) => (
                      <div key={index} style={{ display: "flex", gap: 10, padding: 12, background: "var(--color-surface-2)", borderRadius: 4 }}>
                        <GitBranch size={15} color="#3B82F6" />
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-1)" }}>
                            {cause.root_cause ?? cause.hypothesis ?? "Correlated alert pattern"}
                          </div>
                          <div style={{ fontSize: 12, color: "var(--color-text-2)", marginTop: 2 }}>
                            Confidence {Math.round((cause.confidence ?? 0.7) * 100)}% · {cause.impact ?? "Likely shared operational driver"}
                          </div>
                        </div>
                      </div>
                    ))}
                    {!(correlationSummary?.correlation_results?.root_cause_hypotheses ?? []).length && (
                      <NoData msg="No correlated alert clusters detected" />
                    )}
                  </div>
                </div>
              )}

            </div>

            {/* ── Right Column ── */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

              {/* Performance Metrics */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Performance Metrics</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {performanceMetrics?.map((metric, index) => (
                    <div key={index} style={{
                      padding: "12px",
                      background: "var(--color-surface-2)",
                      borderRadius: 4,
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                        <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                          {metric.metric}
                        </span>
                        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                          {metric.trend === "up" && <TrendingUp size={14} color="#10B981" />}
                          {metric.trend === "down" && <TrendingDown size={14} color="#EF4444" />}
                          {metric.trend === "stable" && <Activity size={14} color="#6B7280" />}
                        </div>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                        <span style={{ fontSize: 18, fontWeight: 600, color: "var(--color-text-1)" }}>
                          {metric.current.toFixed(1)}%
                        </span>
                        <span style={{ fontSize: 11, color: "var(--color-text-3)" }}>
                          Target: {metric.target.toFixed(1)}%
                        </span>
                      </div>
                      <div style={{
                        height: 4,
                        background: "var(--color-border)",
                        borderRadius: 2,
                        marginTop: 8,
                        overflow: "hidden"
                      }}>
                        <div style={{
                          height: "100%",
                          width: `${(metric.current / metric.target) * 100}%`,
                          background: metric.current >= metric.target ? "#10B981" : metric.current >= metric.target * 0.9 ? "#FF9500" : "#EF4444",
                          borderRadius: 2,
                          transition: "width 300ms ease"
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* System Health */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>System Health</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {systemHealth?.map((component, index) => (
                    <div key={index} style={{
                      padding: "12px",
                      background: "var(--color-surface-2)",
                      borderRadius: 4,
                      border: `1px solid ${component.status === "healthy" ? "#D1FAE5" : component.status === "degraded" ? "#FEF3C7" : "#FEE2E2"}`,
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                        <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-1)" }}>
                          {component.component}
                        </span>
                        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                          {component.status === "healthy" && <CheckCircle size={14} color="#10B981" />}
                          {component.status === "degraded" && <AlertTriangle size={14} color="#FF9500" />}
                          {component.status === "down" && <AlertTriangle size={14} color="#EF4444" />}
                          <span style={{
                            fontSize: 10,
                            padding: "2px 6px",
                            borderRadius: 3,
                            background: component.status === "healthy" ? "#D1FAE5" : component.status === "degraded" ? "#FEF3C7" : "#FEE2E2",
                            color: component.status === "healthy" ? "#065F46" : component.status === "degraded" ? "#92400E" : "#991B1B",
                            fontWeight: 500,
                          }}>
                            {component.status}
                          </span>
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 16, fontSize: 11, color: "var(--color-text-3)" }}>
                        <span>Uptime: {component.uptime.toFixed(1)}%</span>
                        <span>CPU: {component.metrics.cpu}%</span>
                        <span>Memory: {component.metrics.memory}%</span>
                        <span>Response: {component.metrics.response_time}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Predictive Alerts</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
                  {predictiveAlerts.slice(0, 4).map((alert, index) => (
                    <div key={index} style={{ display: "flex", gap: 10, padding: 12, borderRadius: 4, background: "var(--color-surface-2)" }}>
                      <Radar size={15} color={alert.severity === "critical" ? "#EF4444" : "#FF9500"} />
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-1)" }}>
                          {alert.alert_type?.replaceAll("_", " ") ?? "Predictive risk"}
                        </div>
                        <div style={{ fontSize: 12, color: "var(--color-text-2)", marginTop: 2 }}>
                          {alert.message ?? "Potential issue anticipated by trend model"}
                        </div>
                      </div>
                    </div>
                  ))}
                  {!predictiveAlerts.length && <NoData msg="No predictive alerts currently active" />}
                </div>
              </div>

              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Incident Workflow</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
                  {(incidents.length ? incidents : [{
                    id: "INC-DEMO",
                    incident_type: "supplier_delay",
                    title: "Supplier delay triage",
                    description: "Supplier delay triage workflow",
                    status: "investigating",
                    assigned_team: "Supply Ops",
                    escalation_level: 1,
                    severity: "medium",
                    priority: "medium",
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    timeline: [],
                  }]).slice(0, 3).map((incident) => (
                    <div key={incident.id ?? incident.incident_id} style={{ display: "flex", gap: 10, padding: 12, borderRadius: 4, border: "1px solid var(--color-border)" }}>
                      <Users size={15} color="#10B981" />
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-1)" }}>
                          {incident.title ?? incident.incident_type}
                        </div>
                        <div style={{ fontSize: 12, color: "var(--color-text-2)", marginTop: 2 }}>
                          {incident.status} · {incident.assigned_team ?? incident.assigned_to ?? "Unassigned"} · L{incident.escalation_level ?? 0}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 20,
              }}>
                <SectionLabel>Quick Actions</SectionLabel>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={createIncidentFromTopAlert}
                    disabled={actionBusy === "incident-report"}
                  >
                    {actionBusy === "incident-report" ? "Generating..." : "Generate Incident Report"}
                  </button>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={escalateLatestIncident}
                    disabled={actionBusy === "escalate-incident"}
                  >
                    {actionBusy === "escalate-incident" ? "Escalating..." : "Escalate Incident"}
                  </button>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => router.push("/pipeline")}
                  >
                    Maintenance Mode
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
