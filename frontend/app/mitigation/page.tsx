"use client";

import React, { useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { useApi } from "../../hooks/useApi";
import { useToast } from "../components/feedback/ToastContext";
import { SafeMarkdown } from "../components/feedback/SafeMarkdown";
import { NoData } from "../components/Cards/NoData";

type PendingAction = {
  id: number;
  supplier: string;
  trigger_score: number;
  action_type: string;
  action_summary: string;
  action_detail: any;
  status: string;
  created_at: string;
  llm_reasoning: string;
};

export default function MitigationPage() {
  const { data, loading, retry } = useApi<{ total: number; items: PendingAction[] }>("/mitigation/pending?status=awaiting_approval", { fallback: { total: 0, items: [] } });
  const { showToast } = useToast();
  const [processing, setProcessing] = useState<number | null>(null);

  const pendingItems = data?.items || [];

  const handleApprove = async (id: number) => {
    setProcessing(id);
    try {
      const token = localStorage.getItem("nexus_token");
      const res = await fetch(`http://localhost:8000/mitigation/approve/${id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ approved_by: "system_user" })
      });
      if (!res.ok) throw new Error("Approval failed");
      showToast("Action approved and executed.", "success");
      retry();
    } catch (err: any) {
      showToast(err.message, "error");
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (id: number) => {
    setProcessing(id);
    try {
      const token = localStorage.getItem("nexus_token");
      const res = await fetch(`http://localhost:8000/mitigation/reject/${id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ rejected_by: "system_user", reason: "Rejected via UI" })
      });
      if (!res.ok) throw new Error("Rejection failed");
      showToast("Action rejected.", "success");
      retry();
    } catch (err: any) {
      showToast(err.message, "error");
    } finally {
      setProcessing(null);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main className="main-content">
          <div style={{ marginBottom: 24, borderBottom: "1px solid var(--color-border)", paddingBottom: 16 }}>
            <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--color-text-1)" }}>Mitigation Loop</h1>
            <p style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 4 }}>
              Agentic actions awaiting human approval
            </p>
          </div>

          {loading ? (
            <div className="skeleton" style={{ height: 200, width: "100%", borderRadius: 6 }} />
          ) : pendingItems.length === 0 ? (
            <NoData msg="No pending actions awaiting approval." actionText="Check Traces" actionHref="/agent-traces" />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {pendingItems.map((item) => (
                <div key={item.id} style={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 6,
                  padding: 20
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontSize: 18, fontWeight: 600, color: "var(--color-text-1)" }}>{item.supplier}</span>
                        <span style={{ 
                          fontSize: 11, fontWeight: 600, padding: "2px 6px", borderRadius: 4, 
                          background: "rgba(255, 68, 68, 0.1)", color: "#FF4444" 
                        }}>
                          Risk Score: {item.trigger_score}
                        </span>
                      </div>
                      <div style={{ fontSize: 13, color: "var(--color-text-2)", marginTop: 4 }}>
                        {item.action_summary}
                      </div>
                    </div>
                    <span style={{ fontSize: 11, color: "var(--color-text-3)", background: "var(--color-surface-2)", padding: "4px 8px", borderRadius: 4 }}>
                      {item.action_type.toUpperCase()}
                    </span>
                  </div>

                  <div style={{ background: "var(--color-surface-2)", padding: 12, borderRadius: 6, marginBottom: 16, fontSize: 13, color: "var(--color-text-2)" }}>
                    <div style={{ fontWeight: 600, color: "var(--color-text-1)", marginBottom: 4 }}>Agent Rationale</div>
                    <SafeMarkdown text={item.action_detail?.rationale || "No rationale provided."} />
                  </div>

                  <div style={{ display: "flex", gap: 12, borderTop: "1px solid var(--color-border)", paddingTop: 16 }}>
                    <button 
                      className={`btn btn-primary ${processing === item.id ? "loading" : ""}`} 
                      onClick={() => handleApprove(item.id)}
                      disabled={processing !== null}
                    >
                      Approve & Execute
                    </button>
                    <button 
                      className={`btn btn-secondary ${processing === item.id ? "loading" : ""}`} 
                      onClick={() => handleReject(item.id)}
                      disabled={processing !== null}
                    >
                      Reject
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
