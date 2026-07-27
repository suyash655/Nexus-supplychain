"use client";
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";
import React, { useState, useMemo } from "react";

/* ── Palette-only colour sequence for data series ── */
const COLORS = [
    "var(--chart-1)",
    "var(--chart-2)",
    "var(--chart-3)",
    "var(--chart-4)",
    "var(--chart-5)",
];

const tooltipStyle = {
    backgroundColor: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "8px",
    color: "var(--color-text-1)",
    fontSize: "12px",
    boxShadow: "none",
};

const AXIS_TICK   = { fill: "var(--color-text-3)", fontSize: 11 };
const AXIS_LINE   = { stroke: "var(--color-border)" };
const GRID_STROKE = "var(--color-border)";

type ChartDatum = Record<string, any>;

/* ============================
   BAR CHART
   ============================ */
export const SynBarChart = React.memo(function SynBarChart({
    data,
    dataKey,
    nameKey = "name",
    color = "var(--chart-1)",
    height = 300,
}: {
    data: ChartDatum[];
    dataKey: string;
    nameKey?: string;
    color?: string;
    height?: number;
}) {
    return (
        <ResponsiveContainer width="100%" height={height}>
            <BarChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} vertical={false} />
                <XAxis dataKey={nameKey} tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
                <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-surface-2)" }} />
                <Bar dataKey={dataKey} fill={color} radius={[2, 2, 0, 0]} />
            </BarChart>
        </ResponsiveContainer>
    );
});

/* ============================
   LINE CHART
   ============================ */
export const SynLineChart = React.memo(function SynLineChart({
    data,
    lines,
    xKey = "name",
    height = 300,
}: {
    data: ChartDatum[];
    lines: { key: string; color?: string; name?: string }[];
    xKey?: string;
    height?: number;
}) {
    return (
        <ResponsiveContainer width="100%" height={height}>
            <LineChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} vertical={false} />
                <XAxis dataKey={xKey} tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
                <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 11, color: "var(--color-text-2)" }} />
                {lines.map((line, i) => (
                    <Line
                        key={line.key}
                        type="monotone"
                        dataKey={line.key}
                        stroke={line.color || COLORS[i % COLORS.length]}
                        strokeWidth={2}
                        dot={{ r: 2, fill: line.color || COLORS[i % COLORS.length] }}
                        activeDot={{ r: 3 }}
                        name={line.name || line.key}
                    />
                ))}
            </LineChart>
        </ResponsiveContainer>
    );
});

/* ============================
   AREA CHART
   ============================ */
export const SynAreaChart = React.memo(function SynAreaChart({
    data,
    dataKey,
    xKey = "name",
    color = "var(--chart-1)",
    height = 300,
}: {
    data: ChartDatum[];
    dataKey: string;
    xKey?: string;
    color?: string;
    height?: number;
}) {
    // Generate a safe gradId without var() wrappers
    const safeColor = color.replace(/[^a-zA-Z0-9-]/g, "");
    const gradId = `grad-${dataKey}-${safeColor}`;
    return (
        <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                <defs>
                    <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%"   stopColor={color} stopOpacity={0.12} />
                        <stop offset="100%" stopColor={color} stopOpacity={0}    />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} vertical={false} />
                <XAxis dataKey={xKey} tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
                <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area
                    type="monotone"
                    dataKey={dataKey}
                    stroke={color}
                    fill={`url(#${gradId})`}
                    strokeWidth={2}
                    dot={false}
                />
            </AreaChart>
        </ResponsiveContainer>
    );
});

/* ============================
   PIE CHART
   ============================ */
const MAX_SLICES = 6;

function CustomPieTooltip({ active, payload }: any) {
    if (!active || !payload?.length) return null;
    const d = payload[0];
    return (
        <div style={{
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 12,
            color: "var(--color-text-1)",
        }}>
            <div style={{ fontWeight: 600, marginBottom: 4, color: d.payload?.fill || "var(--chart-1)" }}>
                {d.name}
            </div>
            <div style={{ color: "var(--color-text-2)" }}>
                {typeof d.value === "number" ? d.value.toLocaleString() : d.value}
                {d.payload?.percent != null && (
                    <span style={{ color: "var(--color-text-3)", marginLeft: 6 }}>
                        ({(d.payload.percent * 100).toFixed(1)}%)
                    </span>
                )}
            </div>
            {d.payload?._groupedItems && (
                <div style={{ marginTop: 6, paddingTop: 6, borderTop: "1px solid var(--color-border)", fontSize: 11, color: "var(--color-text-3)" }}>
                    Includes: {d.payload._groupedItems.join(", ")}
                </div>
            )}
        </div>
    );
}

export const SynPieChart = React.memo(function SynPieChart({
    data,
    dataKey,
    nameKey = "name",
    height = 300,
}: {
    data: ChartDatum[];
    dataKey: string;
    nameKey?: string;
    height?: number;
}) {
    const [hovered, setHovered] = useState<number | null>(null);

    const { chartData, colorMap } = useMemo(() => {
        if (!data || data.length === 0) return { chartData: [], colorMap: {} as Record<string, string> };

        const sorted = [...data].sort((a, b) => (b[dataKey] || 0) - (a[dataKey] || 0));
        const cMap: Record<string, string> = {};

        if (sorted.length <= MAX_SLICES) {
            sorted.forEach((d, i) => { cMap[d[nameKey]] = COLORS[i % COLORS.length]; });
            return { chartData: sorted, colorMap: cMap };
        }

        const topItems      = sorted.slice(0, MAX_SLICES - 1);
        const remainingItems = sorted.slice(MAX_SLICES - 1);
        const otherValue    = remainingItems.reduce((sum, d) => sum + (d[dataKey] || 0), 0);
        const otherNames    = remainingItems.map(d => d[nameKey]);

        topItems.forEach((d, i) => { cMap[d[nameKey]] = COLORS[i % COLORS.length]; });
        cMap["Other"] = "var(--color-text-3)";

        const grouped = [
            ...topItems,
            { [nameKey]: "Other", [dataKey]: otherValue, _groupedItems: otherNames },
        ];

        return { chartData: grouped, colorMap: cMap };
    }, [data, dataKey, nameKey]);

    if (chartData.length === 0) {
        return (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height, color: "var(--color-text-3)", fontSize: 13 }}>
                No data available
            </div>
        );
    }

    const total = chartData.reduce((sum, d) => sum + (d[dataKey] || 0), 0);

    return (
        <div style={{ display: "flex", alignItems: "center", gap: 16, height }}>
            <div style={{ flex: "0 0 55%", height: "100%" }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            dataKey={dataKey}
                            nameKey={nameKey}
                            cx="50%"
                            cy="50%"
                            outerRadius={Math.min(height * 0.38, 110)}
                            innerRadius={Math.min(height * 0.2,  55)}
                            paddingAngle={2}
                            label={false}
                            labelLine={false}
                            onMouseEnter={(_, index) => setHovered(index)}
                            onMouseLeave={() => setHovered(null)}
                            stroke="none"
                        >
                            {chartData.map((entry, i) => (
                                <Cell
                                    key={i}
                                    fill={colorMap[entry[nameKey]] || COLORS[i % COLORS.length]}
                                    opacity={hovered === null || hovered === i ? 1 : 0.35}
                                    style={{ transition: "opacity 120ms cubic-bezier(0.16,1,0.3,1)", cursor: "pointer" }}
                                />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomPieTooltip />} />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Legend */}
            <div style={{
                flex: "1 1 45%",
                maxHeight: height - 16,
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: 4,
            }}>
                {chartData.map((entry, i) => {
                    const val   = entry[dataKey] || 0;
                    const pct   = total > 0 ? ((val / total) * 100).toFixed(1) : "0";
                    const name  = entry[nameKey];
                    const color = colorMap[name] || COLORS[i % COLORS.length];
                    const isHov = hovered === i;

                    return (
                        <div
                            key={i}
                            onMouseEnter={() => setHovered(i)}
                            onMouseLeave={() => setHovered(null)}
                            style={{
                                display:    "flex",
                                alignItems: "center",
                                gap:        8,
                                padding:    "4px 8px",
                                borderRadius: 4,
                                background: isHov ? "var(--color-surface-2)" : "transparent",
                                cursor:     "pointer",
                                transition: "background 120ms cubic-bezier(0.16,1,0.3,1)",
                            }}
                        >
                            <span style={{ width: 8, height: 8, borderRadius: 2, background: color, flexShrink: 0 }} />
                            <span style={{
                                flex: 1,
                                fontSize: 11,
                                color: isHov ? "var(--color-text-1)" : "var(--color-text-2)",
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                fontWeight: isHov ? 500 : 400,
                                transition: "color 120ms cubic-bezier(0.16,1,0.3,1)",
                            }}>
                                {name}
                            </span>
                            <span style={{
                                fontSize:   11,
                                color:      isHov ? color : "var(--color-text-3)",
                                fontWeight: 500,
                                flexShrink: 0,
                                transition: "color 120ms cubic-bezier(0.16,1,0.3,1)",
                            }}>
                                {pct}%
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
});
