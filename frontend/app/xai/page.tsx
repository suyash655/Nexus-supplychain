"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import TopNav from "../components/TopNav";
import { SafeMarkdown } from "../components/SafeMarkdown";
import { SynBarChart } from "../components/Charts";
import { apiFetch } from "@/lib/api";
import { Brain, ArrowDownRight } from "lucide-react";

// Demo data for when backend is unavailable
const DEMO_IMPORTANCE = {
    features: [
        { rank: 1, feature: "delay_days", importance: 0.42, permutation_importance: 0.38 },
        { rank: 2, feature: "cost", importance: 0.28, permutation_importance: 0.25 },
        { rank: 3, feature: "quality_score", importance: 0.15, permutation_importance: 0.13 },
        { rank: 4, feature: "lead_time", importance: 0.09, permutation_importance: 0.11 },
        { rank: 5, feature: "shipment_count", importance: 0.06, permutation_importance: 0.05 },
    ],
    interpretation: "**delay_days** is the strongest predictor of supplier risk, contributing 42% of the model's decision. **cost** follows at 28%, indicating that high-cost shipments correlate with elevated risk.",
    model_score: 0.87,
    target: "risk_score",
};

const DEMO_COUNTERFACTUALS: any[] = [
    {
        supplier: "Apex Materials", tier: "critical", current_risk_score: 82, best_action: "Reduce avg delay to 4d",
        counterfactuals: [
            { change: "Reduce delay", current_value: "8.3d", target_value: "4.0d", risk_reduction: 18.5, new_risk_score: 63.5 },
            { change: "Improve quality", current_value: "72%", target_value: "90%", risk_reduction: 8.2, new_risk_score: 73.8 },
        ],
    },
];

export default function XAIPage() {
    const [importance, setImportance] = useState<any>(null);
    const [counterfactuals, setCounterfactuals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const [impRes, cfRes] = await Promise.all([
                    apiFetch(`/xai/feature-importance`),
                    apiFetch(`/xai/counterfactuals`),
                ]);
                if (!impRes.ok || !cfRes.ok) throw new Error("XAI API failed");
                setImportance(await impRes.json());
                setCounterfactuals(await cfRes.json());
            } catch {
                // Fallback to demo data
                setImportance(DEMO_IMPORTANCE);
                setCounterfactuals(DEMO_COUNTERFACTUALS);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) {
        return (
            <div className="app-layout">
                <Sidebar />
                <div className="main-wrapper">
                    <TopNav />
                    <main className="main-content" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <p style={{ color: "var(--color-text-muted)" }}>Computing explanations...</p>
                    </main>
                </div>
            </div>
        );
    }

    const featureData = (importance?.features || []).map((f: any) => ({
        name: f.feature,
        importance: parseFloat((f.importance * 100).toFixed(1)),
    }));

    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-wrapper">
            <TopNav />
            <main className="main-content">
                <div style={{ marginBottom: 24 }}>
                    <h1 style={{ fontFamily: "var(--font-plex)", fontSize: 28, fontWeight: 700, marginBottom: 4 }}>
                        <Brain size={24} style={{ display: "inline", marginRight: 10, verticalAlign: "middle" }} />
                        Explainable AI (XAI)
                    </h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                        Understand why the AI makes its predictions — feature importance, counterfactuals, and causal reasoning
                    </p>
                </div>

                {/* Feature Importance */}
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="chart-title">Feature Importance for Delay Prediction</div>
                    {importance?.interpretation && (
                        <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16, lineHeight: 1.6 }}>
                            <SafeMarkdown text={importance.interpretation} />
                        </p>
                    )}
                    {featureData.length > 0 ? (
                        <SynBarChart data={featureData} dataKey="importance" nameKey="name" color="#a78bfa" height={280} />
                    ) : (
                        <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Upload data to compute feature importance</p>
                    )}
                    {importance?.model_score != null && (
                        <div style={{ marginTop: 12, fontSize: 12, color: "var(--text-muted)" }}>
                            Model R² Score: {importance.model_score} · Target: {importance.target}
                        </div>
                    )}
                </div>

                {/* Feature Importance Table */}
                {importance?.features?.length > 0 && (
                    <div className="card" style={{ marginBottom: 20 }}>
                        <div className="chart-title">Detailed Feature Rankings</div>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Feature</th>
                                    <th>Importance</th>
                                    <th>Permutation Importance</th>
                                    <th>Contribution</th>
                                </tr>
                            </thead>
                            <tbody>
                                {importance.features.map((f: any) => (
                                    <tr key={f.feature}>
                                        <td style={{ fontWeight: 600, color: "var(--accent)" }}>#{f.rank}</td>
                                        <td style={{ fontWeight: 500 }}>{f.feature}</td>
                                        <td>{(f.importance * 100).toFixed(1)}%</td>
                                        <td>{(f.permutation_importance * 100).toFixed(1)}%</td>
                                        <td>
                                            <div className="risk-bar" style={{ width: 80 }}>
                                                <div className="risk-bar-fill" style={{ width: `${f.importance * 100}%`, background: "#a78bfa" }} />
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Counterfactual Explanations */}
                <div className="card">
                    <div className="chart-title">Counterfactual Explanations</div>
                    <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
                        &quot;What would need to change to reduce risk?&quot; — actionable insights per supplier
                    </p>

                    {counterfactuals.length > 0 ? (
                        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                            {counterfactuals.map((cf, i) => (
                                <div
                                    key={i}
                                    style={{
                                        padding: 16,
                                        background: "rgba(255,255,255,0.02)",
                                        borderRadius: 12,
                                        border: "1px solid var(--border-subtle)",
                                    }}
                                >
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                                        <div>
                                            <span style={{ fontWeight: 600, fontSize: 14 }}>{cf.supplier}</span>
                                            <span
                                                className={`risk-badge risk-${cf.tier === "critical" ? "critical" : cf.tier === "elevated" ? "elevated" : "stable"}`}
                                                style={{ marginLeft: 8 }}
                                            >
                                                Risk: {cf.current_risk_score}
                                            </span>
                                        </div>
                                        <div style={{ fontSize: 12, color: "#22c55e" }}>
                                            Best action: {cf.best_action}
                                        </div>
                                    </div>

                                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 8 }}>
                                        {cf.counterfactuals.map((c: any, j: number) => (
                                            <div
                                                key={j}
                                                style={{
                                                    padding: "10px 12px",
                                                    borderRadius: 8,
                                                    background: "rgba(255,255,255,0.02)",
                                                    border: "1px solid var(--border-subtle)",
                                                    fontSize: 12,
                                                }}
                                            >
                                                <div style={{ fontWeight: 500, marginBottom: 4 }}>{c.change}</div>
                                                <div style={{ color: "var(--text-muted)" }}>
                                                    {c.current_value} → {c.target_value}
                                                </div>
                                                <div style={{ color: "#22c55e", marginTop: 4, display: "flex", alignItems: "center", gap: 4 }}>
                                                    <ArrowDownRight size={12} /> Risk drops {c.risk_reduction.toFixed(1)} pts → {c.new_risk_score.toFixed(1)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Upload data to generate counterfactual explanations</p>
                    )}
                </div>
            </main>
            </div>
        </div>
    );
}
