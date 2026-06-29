"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import { AnimatedSection, StaggerGrid, StaggerItem } from "../components/Animated";
import { useToast } from "../components/ToastContext";
import { apiFetchJSON, apiPostJSON } from "@/lib/api";
import {
  Database, Plug, Cloud, Globe, CheckCircle, XCircle, RefreshCw, Plus,
} from "lucide-react";

type ConnectorType = {
  id: string; name: string; icon: string; description: string;
};

type Connector = {
  id: number; name: string; type: string; active: boolean;
  last_sync: string | null; last_status: string | null; last_rows: number | null;
};

export default function ConnectorsPage() {
  const { showToast } = useToast();
  const [types, setTypes] = useState<ConnectorType[]>([]);
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("csv");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [typesRes, connsRes] = await Promise.all([
        apiFetchJSON<{ types?: ConnectorType[] }>(`/connectors/types`),
        apiFetchJSON<{ connectors?: Connector[] }>(`/connectors`),
      ]);
      setTypes(typesRes.types || []);
      setConnectors(connsRes.connectors || []);
      if (!newType && typesRes.types?.[0]?.id) {
        setNewType(typesRes.types[0].id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load connectors";
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [newType, showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const createConnector = async () => {
    const name = newName.trim();
    if (!name) {
      showToast("Connector name is required.", "warning");
      return;
    }
    setCreating(true);
    try {
      await apiPostJSON(`/connectors`, { name, connector_type: newType, config: {}, schedule: "manual" });
      setShowCreate(false);
      setNewName("");
      await load();
      showToast("Connector created successfully.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Connector creation failed.", "error");
    } finally {
      setCreating(false);
    }
  };

  const testConnector = async (id: number) => {
    setTestingId(id);
    try {
      const data = await apiPostJSON<{ status: string; message?: string }>(`/connectors/${id}/test`, {});
      showToast(`Connection Test: ${data.status} ${data.message || ""}`, data.status === "success" ? "success" : "error");
      await load();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Connection test failed.", "error");
    } finally {
      setTestingId(null);
    }
  };

  const iconMap: Record<string, React.ReactNode> = {
    csv: <Database size={24} color="#06b6d4" />,
    database: <Database size={24} color="#a78bfa" />,
    s3: <Cloud size={24} color="#f59e0b" />,
    api: <Globe size={24} color="#22c55e" />,
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
        <AnimatedSection>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
            <div>
              <h1 className="text-heading">Data Connectors</h1>
              <p style={{ fontSize: 13, color: "var(--color-text-muted)", marginTop: 4 }}>
                Multi-source data ingestion — connect databases, cloud storage, APIs, and files
              </p>
            </div>
            <button onClick={() => setShowCreate(!showCreate)} className="btn btn-primary">
              <Plus size={16} /> New Connector
            </button>
          </div>
        </AnimatedSection>

        {/* Available Connector Types */}
        <StaggerGrid style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
          {types.map(t => (
            <StaggerItem key={t.id}>
              <div className="card" style={{ textAlign: "center", padding: 24 }}>
                <div style={{ marginBottom: 12, display: "flex", justifyContent: "center" }}>
                  {iconMap[t.id] || <Plug size={24} color="var(--color-text-muted)" />}
                </div>
                <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{t.name}</div>
                <div style={{ fontSize: 11, color: "var(--color-text-muted)" }}>{t.description}</div>
              </div>
            </StaggerItem>
          ))}
        </StaggerGrid>

        {/* Create Connector Form */}
        {showCreate && (
          <AnimatedSection>
            <div className="card" style={{ marginBottom: 24, border: "1px solid rgba(99, 102, 241, 0.2)", padding: 24 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16 }}>Create New Connector</h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: 12, alignItems: "end" }}>
                <div>
                  <label className="input-label">Name</label>
                  <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="My Database" className="input" />
                </div>
                <div>
                  <label className="input-label">Type</label>
                  <select value={newType} onChange={e => setNewType(e.target.value)} className="input">
                    {types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
                <button onClick={createConnector} className="btn btn-primary" disabled={creating}>
                  {creating ? "Creating..." : "Create"}
                </button>
              </div>
            </div>
          </AnimatedSection>
        )}

        {/* Active Connectors */}
        <AnimatedSection delay={0.2}>
          <h2 className="text-subheading" style={{ marginBottom: 16 }}>Active Connectors</h2>
        </AnimatedSection>
        {error ? (
          <div className="card-static" style={{ textAlign: "center", padding: 40, color: "var(--color-danger)" }}>
            {error}
          </div>
        ) : loading ? (
          <div className="card-static" style={{ textAlign: "center", padding: 40, color: "var(--color-text-muted)" }}>
            Loading connectors...
          </div>
        ) : connectors.length === 0 ? (
          <div className="card-static" style={{ textAlign: "center", padding: 40, color: "var(--color-text-muted)" }}>
            No connectors configured. Create one to start ingesting data.
          </div>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {connectors.map(c => (
              <div key={c.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  {iconMap[c.type] || <Plug size={20} color="var(--color-text-muted)" />}
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700 }}>{c.name}</div>
                    <div className="text-caption">
                      Type: {c.type} · Last sync: {c.last_sync || "Never"} · Rows: {c.last_rows ?? "—"}
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <span className={c.last_status === "success" ? "badge badge-success" : "badge badge-warning"}>
                    {c.last_status === "success" ? <CheckCircle size={12} /> : <XCircle size={12} />}
                    {c.last_status || "pending"}
                  </span>
                  <button onClick={() => testConnector(c.id)} className="btn btn-ghost btn-sm" disabled={testingId === c.id}>
                    <RefreshCw size={12} /> {testingId === c.id ? "Testing..." : "Test"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
      </div>
    </div>
  );
}
