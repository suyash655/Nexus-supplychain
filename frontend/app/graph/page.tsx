"use client";

import { useEffect, useState, useRef, useCallback, useMemo } from "react";
import dynamic from "next/dynamic";
import Sidebar from "../components/layout/Sidebar";
import TopNav from "../components/layout/TopNav";
import { Network, AlertTriangle, Zap, GitBranch, ZoomIn, ZoomOut, Maximize2, Search, Filter } from "lucide-react";
import { apiFetch, apiPostJSON } from "@/lib/api";
import {
  DEMO_GRAPH, DEMO_GRAPH_SUMMARY, DEMO_GRAPH_CENTRALITY,
} from "../demo-data";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

const NODE_COLORS: Record<string, string> = {
    supplier: "#facc15",
    sku: "#38bdf8",
    warehouse: "#34d399",
    region: "#a78bfa",
    unknown: "#64748b",
};

interface GraphNode {
    id: string;
    name: string;
    type: string;
    shipments?: number;
    avg_delay?: number;
    total_cost?: number;
    volume?: number;
    throughput?: number;
    activity?: number;
    [key: string]: any;
}

interface GraphEdge {
    source: string | GraphNode;
    target: string | GraphNode;
    edge_type?: string;
    weight?: number;
    [key: string]: any;
}

interface ForceNode extends GraphNode {
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
}

export default function GraphPage() {
    const [graphData, setGraphData] = useState<any>(null);
    const [graphSummary, setGraphSummary] = useState<Record<string, unknown> | null>(null);
    const [centrality, setCentrality] = useState<Record<string, unknown[]> | null>(null);
    const [criticalPaths, setCriticalPaths] = useState<unknown[]>([]);
    const [cascadeResult, setCascadeResult] = useState<Record<string, unknown> | null>(null);
    const [cascadeInput, setCascadeInput] = useState("");
    const [loading, setLoading] = useState(true);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isDemoData, setIsDemoData] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [simulatingFailure, setSimulatingFailure] = useState(false);
    const [simulatedFailureResult, setSimulatedFailureResult] = useState<any>(null);
    const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set());
    const [selectedNode, setSelectedNode] = useState<ForceNode | null>(null);
    const [hoveredNode, setHoveredNode] = useState<ForceNode | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set(["supplier", "sku", "warehouse", "region"]));
    const [maxNodes, setMaxNodes] = useState(100);
    const graphRef = useRef<unknown>(null);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Centrality lookup for node sizing
    const centralityMap = useMemo(() => {
        const map: Record<string, number> = {};
        if (centrality?.pagerank) {
            (centrality.pagerank as any[]).forEach((n) => {
                map[n.node_id] = n.pagerank_score || 0;
            });
        }
        return map;
    }, [centrality]);

    // Filter graph data based on active filters and search, with node limit
    const filteredGraphData = useMemo(() => {
        if (!graphData) return null;
        let filteredNodes = graphData.nodes.filter((n: GraphNode) => {
            const matchesType = activeFilters.has(n.type);
            const matchesSearch = !searchQuery || n.name.toLowerCase().includes(searchQuery.toLowerCase()) || n.id.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesType && matchesSearch;
        });
        
        // Sort by centrality (importance) and limit nodes
        filteredNodes = filteredNodes
            .sort((a: GraphNode, b: GraphNode) => (centralityMap[b.id] || 0) - (centralityMap[a.id] || 0))
            .slice(0, maxNodes);
        
        const nodeIds = new Set(filteredNodes.map((n: GraphNode) => n.id));
        const filteredLinks = graphData.links.filter((l: any) => {
            const src = typeof l.source === "object" ? l.source.id : l.source;
            const tgt = typeof l.target === "object" ? l.target.id : l.target;
            return nodeIds.has(src) && nodeIds.has(tgt);
        });
        return { nodes: filteredNodes, links: filteredLinks };
    }, [graphData, activeFilters, searchQuery, maxNodes, centralityMap]);

    /** Apply a graph visualization payload (nodes/edges) into React state */
    const applyGraphData = useCallback((rawGraph: any, summary: any, centralities: any, paths: any, demo: boolean) => {
        setGraphData({
            nodes: (rawGraph.nodes ?? []).map((n: GraphNode) => ({ ...n })),
            links: (rawGraph.edges ?? []).map((e: GraphEdge) => ({
                ...e,
                source: e.source,
                target: e.target,
            })),
        });
        setGraphSummary(summary);
        setCentrality(centralities);
        setCriticalPaths(Array.isArray(paths) ? paths : (paths?.data ?? []));
        setIsDemoData(demo);
    }, []);

    /** Load graph data. Returns true if real data was loaded. */
    const loadGraph = useCallback(async (): Promise<boolean> => {
        try {
            const [gRes, gsRes, cRes, cpRes] = await Promise.all([
                apiFetch(`/graph/visualization`),
                apiFetch(`/graph/summary`),
                apiFetch(`/graph/centrality`),
                apiFetch(`/graph/critical-paths`),
            ]);

            if (!gRes.ok) throw new Error(`Graph fetch failed: ${gRes.status}`);

            const rawGraph = await gRes.json();
            const hasRealNodes = rawGraph?.nodes?.length > 0;

            const [summary, centralities, paths] = await Promise.all([
                gsRes.ok ? gsRes.json() : Promise.resolve({}),
                cRes.ok  ? cRes.json()  : Promise.resolve({ degree: [], betweenness: [], pagerank: [] }),
                cpRes.ok ? cpRes.json() : Promise.resolve([]),
            ]);

            if (hasRealNodes) {
                applyGraphData(rawGraph, summary, centralities, paths, false);
                return true;
            }

            // No real data yet — fall back to demo graph from backend or local constant
            let demoGraph = DEMO_GRAPH;
            try {
                const demoRes = await apiFetch(`/graph/demo`);
                if (demoRes.ok) {
                    const backendDemo = await demoRes.json();
                    if (backendDemo?.nodes?.length > 0) demoGraph = backendDemo;
                }
            } catch { /* use local fallback */ }

            applyGraphData(
                demoGraph,
                DEMO_GRAPH_SUMMARY,
                DEMO_GRAPH_CENTRALITY,
                [],
                true,
            );
            return false;
        } catch (e: unknown) {
            // Backend unreachable — use local demo data
            applyGraphData(DEMO_GRAPH, DEMO_GRAPH_SUMMARY, DEMO_GRAPH_CENTRALITY, [], true);
            return false;
        }
    }, [applyGraphData]);

    useEffect(() => {
        let cancelled = false;

        async function init() {
            setLoading(true);
            setError(null);

            const gotRealData = await loadGraph();
            if (cancelled) return;
            setLoading(false);

            if (!gotRealData) {
                // Check if analysis is currently running — if so, poll until it finishes
                try {
                    const statusRes = await apiFetch(`/graph/status`);
                    if (statusRes.ok) {
                        const status = await statusRes.json();
                        if (status.is_analyzing) {
                            setIsAnalyzing(true);
                            // Poll every 5 seconds until real graph data appears
                            pollRef.current = setInterval(async () => {
                                if (cancelled) { clearInterval(pollRef.current!); return; }
                                try {
                                    const s = await apiFetch(`/graph/status`);
                                    if (!s.ok) return;
                                    const st = await s.json();
                                    if (st.has_real_data) {
                                        clearInterval(pollRef.current!);
                                        setIsAnalyzing(false);
                                        await loadGraph();
                                    } else if (!st.is_analyzing) {
                                        // Analysis finished but no graph data — stop polling
                                        clearInterval(pollRef.current!);
                                        setIsAnalyzing(false);
                                    }
                                } catch { /* keep polling */ }
                            }, 5000);
                        }
                    }
                } catch { /* ignore status check failures */ }
            }
        }

        init();

        return () => {
            cancelled = true;
            if (pollRef.current) clearInterval(pollRef.current);
        };
    }, [loadGraph]);

    const handleNodeClick = useCallback((node: ForceNode) => {
        setSelectedNode(node);
        const neighbors = new Set<string>();
        neighbors.add(node.id);
        if (graphData?.links) {
            graphData.links.forEach((link: any) => {
                const src = typeof link.source === "object" ? (link.source as ForceNode).id : link.source;
                const tgt = typeof link.target === "object" ? (link.target as ForceNode).id : link.target;
                if (src === node.id) neighbors.add(tgt);
                if (tgt === node.id) neighbors.add(src);
            });
        }
        setHighlightNodes(neighbors);
    }, [graphData]);

    const handleNodeHover = useCallback((node: ForceNode | null) => {
        setHoveredNode(node);
        document.body.style.cursor = node ? "pointer" : "default";
    }, []);

    const zoomIn = () => { const g = graphRef.current as any; if (g?.zoom) { const z = g.zoom(); g.zoom(z * 1.4, 400); } };
    const zoomOut = () => { const g = graphRef.current as any; if (g?.zoom) { const z = g.zoom(); g.zoom(z * 0.7, 400); } };
    const zoomFit = () => { const g = graphRef.current as any; if (g?.zoomToFit) g.zoomToFit(400, 40); };

    const toggleFilter = (type: string) => {
        setActiveFilters(prev => {
            const next = new Set(prev);
            if (next.has(type)) next.delete(type);
            else next.add(type);
            return next;
        });
    };

    const runCascade = async () => {
        if (!cascadeInput.trim()) return;
        try {
            const res = await apiFetch(`/graph/simulate?node_ids=${encodeURIComponent(cascadeInput.trim())}`);
            setCascadeResult(await res.json());
        } catch (e) {
            console.error(e);
        }
    };

    const simulateGraphFailure = async (nodeId: string) => {
        setSimulatingFailure(true);
        try {
            const data: any = await apiPostJSON(`/graph/simulate-failure`, { node_id: nodeId });
            if (data.error) {
                console.error(data.error);
                return;
            }
            setSimulatedFailureResult(data.diff);
            
            // Adjust highlighting for visual diff
            const newHighlight = new Set<string>();
            newHighlight.add(data.diff.node_id);
            data.diff.newly_critical_nodes?.forEach((n: any) => newHighlight.add(n.node_id));
            data.diff.cascade_result?.affected_details?.forEach((n: any) => newHighlight.add(n.node_id));
            setHighlightNodes(newHighlight);
        } catch (e) {
            console.error(e);
        } finally {
            setSimulatingFailure(false);
        }
    };

    const getNodeSize = useCallback((node: ForceNode) => {
        const centralityScore = centralityMap[node.id] || 0;
        const baseSize = { supplier: 4, warehouse: 3, sku: 2, region: 3 }[node.type] || 2;
        return baseSize + Math.min(4, centralityScore * 10);
    }, [centralityMap]);

    const getRiskColor = useCallback((node: ForceNode) => {
        if (simulatedFailureResult) {
            if (node.id === simulatedFailureResult.node_id) return "#475569"; // Grey out failed node
            if (simulatedFailureResult.newly_critical_nodes?.some((n: any) => n.node_id === node.id)) return "#ef4444"; // Red for newly critical
            if (simulatedFailureResult.cascade_result?.affected_details?.some((n: any) => n.node_id === node.id)) return "#f59e0b"; // Orange for cascade affected
        }
        if (node.type !== "supplier") return NODE_COLORS[node.type] || NODE_COLORS.unknown;
        const delay = node.avg_delay || 0;
        if (delay > 10) return "#ef4444"; // red
        if (delay > 5) return "#f59e0b";  // yellow
        if (delay > 2) return "#facc15";  // gold
        return "#22c55e"; // green
    }, [simulatedFailureResult]);

    const renderNode = useCallback(
        (node: ForceNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const baseColor = getRiskColor(node);
            const isHighlighted = highlightNodes.size === 0 || highlightNodes.has(node.id);
            const isHovered = hoveredNode?.id === node.id;
            const radius = getNodeSize(node);
            const x = node.x ?? 0;
            const y = node.y ?? 0;

            // Simple solid circle
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fillStyle = isHighlighted ? baseColor : baseColor + "88";
            ctx.fill();

            // Simple border for hover
            if (isHovered) {
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.5 / globalScale;
                ctx.stroke();
            }

            // Simple label only for important nodes or on hover
            if (globalScale >= 1.2 || isHovered) {
                const label = node.name || node.id;
                const fontSize = Math.max(9, 10 / globalScale);
                ctx.font = `${fontSize}px sans-serif`;
                ctx.fillStyle = "#94a3b8";
                ctx.textAlign = "center";
                ctx.textBaseline = "top";
                ctx.fillText(label.length > 12 ? label.slice(0, 11) + "…" : label, x, y + radius + 2);
            }
        },
        [highlightNodes, hoveredNode, getNodeSize, getRiskColor]
    );

    const renderLink = useCallback((link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const src = link.source as ForceNode;
        const tgt = link.target as ForceNode;
        if (src.x == null || src.y == null || tgt.x == null || tgt.y == null) return;

        const isHighlighted = highlightNodes.size > 0 && (highlightNodes.has(src.id) || highlightNodes.has(tgt.id));

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.strokeStyle = isHighlighted ? "rgba(250, 204, 21, 0.3)" : "rgba(148, 163, 184, 0.15)";
        ctx.lineWidth = 1 / globalScale;
        ctx.stroke();
    }, [highlightNodes]);

    if (loading) {
        return (
            <div className="app-layout">
                <Sidebar />
                <div className="main-wrapper">
                    <TopNav />
                    <main className="main-content" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12 }}>
                        <div style={{ width: 24, height: 24, border: "2px solid var(--accent-primary)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                        <p style={{ color: "var(--color-text-muted)" }}>Building supply chain network…</p>
                    </main>
                </div>
            </div>
        );
    }

    const cascadeAffectedCount = cascadeResult?.total_affected as number | undefined;
    const cascadeRisk = cascadeResult?.risk_assessment as string | undefined;

    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-wrapper">
                <TopNav />
                <main className="main-content">
                    <div style={{ marginBottom: 24 }}>
                        <h1 style={{ fontFamily: "var(--font-plex)", fontSize: 28, fontWeight: 700, marginBottom: 4, display: "flex", alignItems: "center", gap: 10 }}>
                            <Network size={24} />
                            Graph Intelligence
                        </h1>
                        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                            Interactive supply chain topology — nodes sized by importance, colored by risk
                        </p>
                    </div>

                    {error && (
                        <div style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 10, padding: 16, marginBottom: 20, display: "flex", gap: 10, alignItems: "center" }}>
                            <AlertTriangle size={18} color="#ef4444" />
                            <span style={{ color: "#ef4444", fontSize: 13 }}>No graph data. Upload a dataset first. ({error})</span>
                        </div>
                    )}

                    {/* Analyzing banner — shown while analysis pipeline runs after upload */}
                    {isAnalyzing && (
                        <div style={{ background: "rgba(56, 189, 248, 0.08)", border: "1px solid rgba(56, 189, 248, 0.25)", borderRadius: 10, padding: 16, marginBottom: 20, display: "flex", gap: 10, alignItems: "center" }}>
                            <div style={{ width: 14, height: 14, border: "2px solid #38bdf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite", flexShrink: 0 }} />
                            <span style={{ color: "#38bdf8", fontSize: 13 }}>
                                Analysis pipeline running — graph will update automatically when complete (~60s)
                            </span>
                        </div>
                    )}

                    {/* Demo data banner */}
                    {isDemoData && !isAnalyzing && (
                        <div style={{ background: "rgba(168, 85, 247, 0.08)", border: "1px solid rgba(168, 85, 247, 0.25)", borderRadius: 10, padding: "10px 16px", marginBottom: 20, display: "flex", gap: 10, alignItems: "center" }}>
                            <Zap size={14} color="#a855f7" style={{ flexShrink: 0 }} />
                            <span style={{ color: "#a855f7", fontSize: 13 }}>
                                Showing demo network — <a href="/upload" style={{ color: "#c084fc", fontWeight: 600, textDecoration: "none" }}>upload your data</a> to visualize your real supply chain graph
                            </span>
                        </div>
                    )}

                    {/* Stats */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginBottom: 20 }}>
                        {[
                            { label: "Visible Nodes", value: filteredGraphData?.nodes.length ?? 0 },
                            { label: "Total Nodes", value: graphSummary?.total_nodes ?? 0 },
                            { label: "Edges", value: graphSummary?.total_edges ?? 0 },
                            { label: "Density", value: graphSummary?.density ?? 0 },
                            { label: "Resilience", value: (graphSummary?.resilience_metrics as Record<string, unknown>)?.network_resilience_score ?? "—" },
                        ].map(({ label, value }) => (
                            <div key={label} className="card" style={{ padding: 16 }}>
                                <div className="kpi-label">{label}</div>
                                <div style={{ fontSize: 22, fontWeight: 700, marginTop: 4 }}>{String(value)}</div>
                            </div>
                        ))}
                    </div>

                    {/* Graph Controls */}
                    <div className="card" style={{ marginBottom: 20, padding: 0, overflow: "hidden", position: "relative" }}>
                        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <span className="chart-title" style={{ margin: 0 }}>Supply Chain Network</span>
                            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                                {/* Search */}
                                <div style={{ display: "flex", alignItems: "center", gap: 4, background: "rgba(255,255,255,0.03)", borderRadius: 6, padding: "4px 8px", border: "1px solid var(--border-subtle)" }}>
                                    <Search size={12} color="#64748b" />
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={e => setSearchQuery(e.target.value)}
                                        placeholder="Search nodes..."
                                        style={{ background: "transparent", border: "none", outline: "none", color: "#f1f5f9", fontSize: 11, width: 110 }}
                                    />
                                </div>

                                {/* Type Filters */}
                                <div style={{ display: "flex", gap: 4 }}>
                                    {Object.entries(NODE_COLORS).filter(([k]) => k !== "unknown").map(([type, color]) => (
                                        <button
                                            key={type}
                                            onClick={() => toggleFilter(type)}
                                            style={{
                                                fontSize: 10, display: "flex", alignItems: "center", gap: 3,
                                                color: activeFilters.has(type) ? color : "#64748b55",
                                                background: activeFilters.has(type) ? color + "15" : "transparent",
                                                border: `1px solid ${activeFilters.has(type) ? color + "44" : "transparent"}`,
                                                borderRadius: 4, padding: "2px 6px", cursor: "pointer",
                                                transition: "all 0.2s",
                                            }}
                                        >
                                            <span style={{ width: 6, height: 6, borderRadius: "50%", background: activeFilters.has(type) ? color : "#64748b55", display: "inline-block" }} />
                                            {type}
                                        </button>
                                    ))}
                                </div>

                                {/* Zoom Controls */}
                                <div style={{ display: "flex", gap: 2, marginLeft: 8 }}>
                                    <button onClick={zoomIn} style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: 4, padding: "4px 6px", cursor: "pointer", color: "#94a3b8" }} title="Zoom In"><ZoomIn size={14} /></button>
                                    <button onClick={zoomOut} style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: 4, padding: "4px 6px", cursor: "pointer", color: "#94a3b8" }} title="Zoom Out"><ZoomOut size={14} /></button>
                                    <button onClick={zoomFit} style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: 4, padding: "4px 6px", cursor: "pointer", color: "#94a3b8" }} title="Fit to View"><Maximize2 size={14} /></button>
                                </div>

                                {/* Node Limit Control */}
                                <div style={{ display: "flex", alignItems: "center", gap: 4, marginLeft: 8 }}>
                                    <span style={{ fontSize: 10, color: "#64748b" }}>Max nodes:</span>
                                    <select 
                                        value={maxNodes}
                                        onChange={(e) => setMaxNodes(Number(e.target.value))}
                                        style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: 4, padding: "2px 6px", color: "#94a3b8", fontSize: 10 }}
                                    >
                                        <option value={50}>50</option>
                                        <option value={100}>100</option>
                                        <option value={200}>200</option>
                                        <option value={500}>500</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div style={{ height: 540, background: "transparent" }} onClick={() => { setHighlightNodes(new Set()); setSelectedNode(null); }}>
                            {filteredGraphData && filteredGraphData.nodes.length > 0 ? (
                                <ForceGraph2D
                                    ref={graphRef as any}
                                    graphData={filteredGraphData}
                                    height={540}
                                    backgroundColor="transparent"
                                    nodeCanvasObject={renderNode as any}
                                    nodeCanvasObjectMode={() => "replace"}
                                    linkCanvasObject={renderLink as any}
                                    linkCanvasObjectMode={() => "replace"}
                                    onNodeClick={handleNodeClick as any}
                                    onNodeHover={handleNodeHover as any}
                                    cooldownTicks={50}
                                    onEngineStop={() => {
                                        const g = graphRef.current as any;
                                        if (g?.zoomToFit) g.zoomToFit(400, 40);
                                    }}
                                    warmupTicks={10}
                                    d3AlphaDecay={0.05}
                                    d3VelocityDecay={0.4}
                                />
                            ) : (
                                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-muted)", fontSize: 13, gap: 12 }}>
                                    <Network size={48} style={{ opacity: 0.15 }} />
                                    <p>No graph data — upload a supply chain CSV to populate the network.</p>
                                    <a href="/upload" style={{ color: "#38bdf8", fontSize: 12, fontWeight: 600, textDecoration: "none" }}>Go to Upload →</a>
                                </div>
                            )}
                        </div>

                        {/* Risk Legend */}
                        <div style={{ padding: "10px 20px", borderTop: "1px solid var(--border-subtle)", display: "flex", gap: 16, alignItems: "center", fontSize: 10, color: "#64748b" }}>
                            <span style={{ fontWeight: 600 }}>Risk:</span>
                            {[
                                { label: "Low", color: "#22c55e" },
                                { label: "Moderate", color: "#facc15" },
                                { label: "High", color: "#f59e0b" },
                                { label: "Critical", color: "#ef4444" },
                            ].map(({ label, color }) => (
                                <span key={label} style={{ display: "flex", alignItems: "center", gap: 3 }}>
                                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: color }} /> {label}
                                </span>
                            ))}
                            <span style={{ marginLeft: "auto", color: "#475569" }}>Node size = network importance</span>
                        </div>
                    </div>

                    {/* Node Details Panel */}
                    {selectedNode && (
                        <div className="card" style={{ marginBottom: 20, padding: 16, borderColor: (NODE_COLORS[selectedNode.type] || NODE_COLORS.unknown) + "44" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                                <span style={{ fontWeight: 600, fontSize: 15, color: NODE_COLORS[selectedNode.type] }}>
                                    {selectedNode.name}
                                    <span style={{ fontWeight: 400, color: "#64748b", fontSize: 12, marginLeft: 8 }}>{selectedNode.type}</span>
                                </span>
                                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                                    <button 
                                        onClick={() => simulateGraphFailure(selectedNode.id)}
                                        disabled={simulatingFailure}
                                        style={{ background: "#ef4444", color: "#fff", border: "none", borderRadius: 6, padding: "6px 12px", fontSize: 12, fontWeight: 600, cursor: simulatingFailure ? "wait" : "pointer" }}>
                                        {simulatingFailure ? "Simulating..." : "Simulate Failure"}
                                    </button>
                                    <button onClick={() => { setSelectedNode(null); setHighlightNodes(new Set()); }} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 18 }}>×</button>
                                </div>
                            </div>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                                {Object.entries(selectedNode).filter(([k]) => !["id", "x", "y", "vx", "vy", "__indexColor", "__threeObj", "index", "fx", "fy"].includes(k)).map(([k, v]) => (
                                    <div key={k} style={{ background: "rgba(255,255,255,0.03)", borderRadius: 8, padding: "6px 12px" }}>
                                        <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>{k.replace(/_/g, " ")}</div>
                                        <div style={{ fontSize: 13, fontWeight: 600, marginTop: 2 }}>{typeof v === "number" ? v.toLocaleString() : String(v)}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Simulation Result Panel */}
                    {simulatedFailureResult && (
                        <div className="card" style={{ marginBottom: 20, padding: 16, borderColor: "#ef444444", background: "rgba(239, 68, 68, 0.05)" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                                <span style={{ fontWeight: 600, fontSize: 15, color: "#ef4444", display: "flex", alignItems: "center", gap: 8 }}>
                                    <AlertTriangle size={16} /> Failure Simulation: {simulatedFailureResult.node_name}
                                </span>
                                <button onClick={() => { setSimulatedFailureResult(null); setHighlightNodes(new Set()); }} style={{ background: "none", border: "none", color: "#ef4444", cursor: "pointer", fontSize: 18 }}>×</button>
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
                                <div>
                                    <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", fontWeight: 600, marginBottom: 8 }}>Newly Critical Nodes</div>
                                    {simulatedFailureResult.newly_critical_nodes?.length > 0 ? (
                                        simulatedFailureResult.newly_critical_nodes.map((n: any) => (
                                            <div key={n.node_id} style={{ fontSize: 13, marginBottom: 4 }}>
                                                <span style={{ color: "#ef4444", fontWeight: 500 }}>{n.name}</span> <span style={{ color: "#64748b", fontSize: 11 }}>({n.type})</span>
                                            </div>
                                        ))
                                    ) : (
                                        <div style={{ fontSize: 12, color: "#94a3b8" }}>None</div>
                                    )}
                                </div>
                                <div>
                                    <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", fontWeight: 600, marginBottom: 8 }}>Unreachable SKUs</div>
                                    {simulatedFailureResult.unreachable_skus?.length > 0 ? (
                                        simulatedFailureResult.unreachable_skus.map((n: any) => (
                                            <div key={n.node_id} style={{ fontSize: 13, marginBottom: 4, color: "#f59e0b" }}>{n.name}</div>
                                        ))
                                    ) : (
                                        <div style={{ fontSize: 12, color: "#94a3b8" }}>None</div>
                                    )}
                                </div>
                                <div>
                                    <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", fontWeight: 600, marginBottom: 8 }}>Affected Regions</div>
                                    {simulatedFailureResult.affected_regions?.length > 0 ? (
                                        simulatedFailureResult.affected_regions.map((n: any) => (
                                            <div key={n.node_id} style={{ fontSize: 13, marginBottom: 4, color: "#a78bfa" }}>{n.name}</div>
                                        ))
                                    ) : (
                                        <div style={{ fontSize: 12, color: "#94a3b8" }}>None</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
                        {/* PageRank */}
                        <div className="card">
                            <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <Zap size={14} />PageRank (Network Influence)
                            </div>
                            {(centrality?.pagerank?.length ?? 0) > 0 ? (
                                <table className="data-table">
                                    <thead><tr><th>Node</th><th>Type</th><th>Score</th></tr></thead>
                                    <tbody>
                                        {(centrality!.pagerank as unknown[]).slice(0, 8).map((n: unknown, i: number) => {
                                            const node = n as { name: string; type: string; pagerank_score: number };
                                            return (
                                                <tr key={i}>
                                                    <td style={{ fontWeight: 500 }}>{node.name}</td>
                                                    <td><span style={{ color: NODE_COLORS[node.type], fontSize: 11, fontWeight: 600, textTransform: "uppercase" }}>{node.type}</span></td>
                                                    <td>{node.pagerank_score}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            ) : (
                                <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No data</p>
                            )}
                        </div>

                        {/* Critical Bottlenecks */}
                        <div className="card">
                            <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <GitBranch size={14} />Critical Bottlenecks
                            </div>
                            {criticalPaths.length > 0 ? (
                                <table className="data-table">
                                    <thead><tr><th>Node</th><th>Betweenness</th><th>Risk</th></tr></thead>
                                    <tbody>
                                        {(criticalPaths as unknown[]).map((n: unknown, i: number) => {
                                            const node = n as { name: string; betweenness_score: number; bottleneck_risk: string };
                                            return (
                                                <tr key={i}>
                                                    <td style={{ fontWeight: 500 }}>{node.name}</td>
                                                    <td>{node.betweenness_score}</td>
                                                    <td>
                                                        <span className={`risk-badge risk-${node.bottleneck_risk === "high" ? "critical" : node.bottleneck_risk === "medium" ? "elevated" : "stable"}`}>
                                                            {node.bottleneck_risk}
                                                        </span>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            ) : (
                                <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No data</p>
                            )}
                        </div>
                    </div>

                    {/* Cascade Simulation */}
                    <div className="card">
                        <div className="chart-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <AlertTriangle size={14} />Cascade Failure Simulation
                        </div>
                        <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 12 }}>
                            Simulate what happens when a node fails. Enter a supplier, warehouse, or region name.
                        </p>
                        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                            <input
                                className="chat-input"
                                placeholder='e.g. "Supplier A" or "Central Warehouse"'
                                value={cascadeInput}
                                onChange={(e) => setCascadeInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && runCascade()}
                            />
                            <button className="chat-send-btn" onClick={runCascade}>Simulate</button>
                        </div>

                        {cascadeResult && !cascadeResult.error && (
                            <div style={{ padding: 16, background: "rgba(255,255,255,0.02)", borderRadius: 12, border: "1px solid var(--border-subtle)" }}>
                                <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 12 }}>Failure Impact Analysis</div>
                                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: 12, marginBottom: 12 }}>
                                    <div>
                                        <div className="kpi-label">Total Affected</div>
                                        <div style={{ fontSize: 28, fontWeight: 700, color: "#ef4444" }}>{cascadeAffectedCount ?? 0}</div>
                                    </div>
                                    <div>
                                        <div className="kpi-label">Risk Level</div>
                                        <div style={{ fontSize: 16, fontWeight: 700, marginTop: 6, color: cascadeRisk === "catastrophic" ? "#ef4444" : cascadeRisk === "severe" ? "#f59e0b" : "#34d399" }}>
                                            {(cascadeRisk ?? "—").toUpperCase()}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="kpi-label">Recovery</div>
                                        <div style={{ fontSize: 16, fontWeight: 700, marginTop: 6 }}>{String(cascadeResult.recovery_complexity ?? "—")}</div>
                                    </div>
                                </div>

                                {Array.isArray(cascadeResult.affected_details) && cascadeResult.affected_details.length > 0 && (
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: 12, marginBottom: 6, color: "#64748b" }}>Affected Nodes</div>
                                        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                                            {(cascadeResult.affected_details as unknown[]).slice(0, 15).map((n: unknown, i: number) => {
                                                const node = n as { name: string; type: string; estimated_ttr_days: number };
                                                return (
                                                    <span key={i} style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: 6, padding: "2px 8px", fontSize: 11 }}>
                                                        {node.name} <span style={{ color: "#64748b" }}>({node.type})</span>
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                        {cascadeResult?.error && (
                            <div style={{ color: "#ef4444", fontSize: 13 }}>{String(cascadeResult.error)}</div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
