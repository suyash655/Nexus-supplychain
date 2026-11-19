"use client";

import { useId, useState } from "react";
import { useReducedMotion } from "framer-motion";
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { CHART, NEUTRAL_PALETTE, formatCompact, tierColor } from "@/lib/ui";

type Row = Record<string, any>;
type Fmt = (v: number) => string;

const AXIS_TICK = { fill: CHART.axis, fontSize: 11 };
const defaultFmt: Fmt = (v) => formatCompact(v);
const labelFor = (key: string) => key.replace(/_/g, " ");

/* ── Tooltip ── */
function ChartTooltip({ active, payload, label, formatValue }: any) {
    if (!active || !payload?.length) return null;
    const fmt: Fmt = formatValue ?? defaultFmt;
    return (
        <div
            style={{
                minWidth: 130,
                padding: "8px 12px",
                fontSize: 12,
                background: "rgba(10,17,29,0.92)",
                border: "1px solid #2a3b5a",
                borderRadius: 10,
                backdropFilter: "blur(10px)",
            }}
        >
            {label != null && label !== "" && (
                <div style={{ marginBottom: 6, color: CHART.text }}>{label}</div>
            )}
            {payload.map((p: any, i: number) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, color: "#f3efe4" }}>
                    <span
                        style={{
                            width: 8,
                            height: 8,
                            flexShrink: 0,
                            borderRadius: 2,
                            background: p.payload?._fill ?? p.payload?.fill ?? p.color ?? p.fill,
                        }}
                    />
                    <span style={{ color: CHART.text }}>{p.name}</span>
                    <span style={{ marginLeft: "auto", paddingLeft: 12, fontVariantNumeric: "tabular-nums" }}>
                        {typeof p.value === "number" ? fmt(p.value) : p.value}
                    </span>
                </div>
            ))}
        </div>
    );
}

/* ── Bar ── */
interface BarProps {
    data: Row[];
    dataKey: string;
    nameKey?: string;
    color?: string;
    height?: number;
    colorBy?: (row: Row) => string;
    formatValue?: Fmt;
    label?: string;
    [extra: string]: unknown;
}

export function SynBarChart({
    data,
    dataKey,
    nameKey = "name",
    color = CHART.blue,
    height = 220,
    colorBy,
    formatValue = defaultFmt,
    label,
}: BarProps) {
    const reduce = useReducedMotion();
    const rows = data.map((r) => ({ ...r, _fill: colorBy ? colorBy(r) : color }));

    return (
        <ResponsiveContainer width="100%" height={height}>
            <BarChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: 0 }} barCategoryGap="22%">
                <CartesianGrid vertical={false} stroke={CHART.grid} strokeDasharray="3 3" />
                <XAxis
                    dataKey={nameKey}
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={{ stroke: CHART.grid }}
                    interval={rows.length <= 10 ? 0 : "preserveStartEnd"}
                />
                <YAxis tick={AXIS_TICK} tickLine={false} axisLine={false} width={44} tickFormatter={formatValue} />
                <Tooltip
                    cursor={{ fill: "rgba(140,170,220,0.06)" }}
                    content={<ChartTooltip formatValue={formatValue} />}
                />
                <Bar
                    dataKey={dataKey}
                    name={label ?? labelFor(dataKey)}
                    radius={[5, 5, 0, 0]}
                    maxBarSize={56}
                    isAnimationActive={!reduce}
                    animationDuration={800}
                    activeBar={{ fillOpacity: 1 }}
                >
                    {rows.map((r, i) => (
                        <Cell key={i} fill={r._fill} fillOpacity={0.82} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

/* ── Area ── */
interface AreaProps {
    data: Row[];
    dataKey: string;
    xKey?: string;
    color?: string;
    height?: number;
    formatValue?: Fmt;
    label?: string;
    [extra: string]: unknown;
}

export function SynAreaChart({
    data,
    dataKey,
    xKey = "period",
    color = CHART.blue,
    height = 200,
    formatValue = defaultFmt,
    label,
}: AreaProps) {
    const reduce = useReducedMotion();
    const gid = "g" + useId().replace(/[^a-zA-Z0-9]/g, "");

    return (
        <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                <defs>
                    <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                        <stop offset="100%" stopColor={color} stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke={CHART.grid} strokeDasharray="3 3" />
                <XAxis dataKey={xKey} tick={AXIS_TICK} tickLine={false} axisLine={{ stroke: CHART.grid }} />
                <YAxis
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={false}
                    width={44}
                    domain={[0, "auto"]}
                    tickFormatter={formatValue}
                />
                <Tooltip
                    cursor={{ stroke: CHART.axis, strokeDasharray: "3 3" }}
                    content={<ChartTooltip formatValue={formatValue} />}
                />
                <Area
                    type="monotone"
                    dataKey={dataKey}
                    name={label ?? labelFor(dataKey)}
                    stroke={color}
                    strokeWidth={2}
                    fill={`url(#${gid})`}
                    dot={false}
                    activeDot={{ r: 4, fill: color, stroke: "#060a12", strokeWidth: 2 }}
                    isAnimationActive={!reduce}
                    animationDuration={900}
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}

/* ── Line ── */
const LINE_PALETTE = [CHART.blue, CHART.brass, CHART.sage, CHART.amber, CHART.red];

interface LineSpec {
    key: string;
    color?: string;
    name?: string;
    axis?: "left" | "right";
    dashed?: boolean;
}

interface LineProps {
    data: Row[];
    lines: LineSpec[];
    xKey?: string;
    height?: number;
    formatValue?: Fmt;
    [extra: string]: unknown;
}

/* Guards against near-black series colours that vanish on the navy background */
function visibleColor(c: string | undefined, i: number): string {
    const fallback = LINE_PALETTE[i % LINE_PALETTE.length];
    if (!c) return fallback;
    const m = /^#?([0-9a-f]{6})$/i.exec(c.trim());
    if (!m) return c;
    const n = parseInt(m[1], 16);
    const lum = 0.2126 * ((n >> 16) & 255) + 0.7152 * ((n >> 8) & 255) + 0.0722 * (n & 255);
    return lum < 60 ? fallback : c;
}

export function SynLineChart({
    data,
    lines,
    xKey = "name",
    height = 220,
    formatValue = defaultFmt,
}: LineProps) {
    const reduce = useReducedMotion();
    const specs = lines.map((l, i) => ({ ...l, color: visibleColor(l.color, i) }));
    const hasRight = specs.some((l) => l.axis === "right");
    const showDots = data.length <= 12;

    return (
        <div>
            <ResponsiveContainer width="100%" height={height}>
                <LineChart data={data} margin={{ top: 8, right: hasRight ? 0 : 8, bottom: 0, left: 0 }}>
                    <CartesianGrid vertical={false} stroke={CHART.grid} strokeDasharray="3 3" />
                    <XAxis dataKey={xKey} tick={AXIS_TICK} tickLine={false} axisLine={{ stroke: CHART.grid }} />
                    <YAxis
                        yAxisId="left"
                        tick={AXIS_TICK}
                        tickLine={false}
                        axisLine={false}
                        width={44}
                        domain={["auto", "auto"]}
                        tickFormatter={formatValue}
                    />
                    {hasRight && (
                        <YAxis
                            yAxisId="right"
                            orientation="right"
                            tick={AXIS_TICK}
                            tickLine={false}
                            axisLine={false}
                            width={40}
                            domain={["auto", "auto"]}
                            tickFormatter={formatValue}
                        />
                    )}
                    <Tooltip
                        cursor={{ stroke: CHART.axis, strokeDasharray: "3 3" }}
                        content={<ChartTooltip formatValue={formatValue} />}
                    />
                    {specs.map((l) => (
                        <Line
                            key={l.key}
                            yAxisId={l.axis === "right" ? "right" : "left"}
                            type="monotone"
                            dataKey={l.key}
                            name={l.name ?? labelFor(l.key)}
                            stroke={l.color}
                            strokeWidth={2}
                            strokeDasharray={l.dashed ? "5 4" : undefined}
                            dot={showDots ? { r: 3, fill: l.color, strokeWidth: 0 } : false}
                            activeDot={{ r: 5, fill: l.color, stroke: "#060a12", strokeWidth: 2 }}
                            isAnimationActive={!reduce}
                            animationDuration={900}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>

            {specs.length > 1 && (
                <ul
                    style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "6px 16px",
                        margin: "10px 0 0",
                        padding: 0,
                        listStyle: "none",
                        fontSize: 12,
                        color: CHART.text,
                    }}
                >
                    {specs.map((l) => (
                        <li key={l.key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <span style={{ width: 8, height: 8, borderRadius: 2, background: l.color }} />
                            {l.name ?? labelFor(l.key)}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

/* ── Pie / donut ── */
interface PieProps {
    data: Row[];
    dataKey?: string;
    nameKey?: string;
    height?: number;
    formatValue?: Fmt;
    centerCaption?: string;
    colorBy?: (row: Row) => string;
    [extra: string]: unknown;
}

export function SynPieChart({
    data,
    dataKey = "value",
    nameKey = "name",
    height = 180,
    formatValue = defaultFmt,
    centerCaption = "total",
    colorBy,
}: PieProps) {
    const reduce = useReducedMotion();
    const [active, setActive] = useState<number | null>(null);

    /* Tier names (Critical / Elevated / Stable ...) get their risk colour automatically */
    const rows = data.map((r, i) => ({
        ...r,
        _fill: colorBy?.(r) ?? tierColor(String(r[nameKey])) ?? NEUTRAL_PALETTE[i % NEUTRAL_PALETTE.length],
    }));
    const total = rows.reduce((s, r) => s + (Number(r[dataKey]) || 0), 0);

    return (
        <div>
            <div style={{ position: "relative", height }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Tooltip content={<ChartTooltip formatValue={formatValue} />} />
                        <Pie
                            data={rows}
                            dataKey={dataKey}
                            nameKey={nameKey}
                            innerRadius="62%"
                            outerRadius="90%"
                            paddingAngle={2}
                            stroke="#0b1220"
                            strokeWidth={2}
                            isAnimationActive={!reduce}
                            animationDuration={900}
                            onMouseEnter={(_: unknown, i: number) => setActive(i)}
                            onMouseLeave={() => setActive(null)}
                        >
                            {rows.map((r, i) => (
                                <Cell
                                    key={i}
                                    fill={r._fill}
                                    fillOpacity={active === null || active === i ? 1 : 0.35}
                                    style={{ transition: "fill-opacity 160ms ease" }}
                                />
                            ))}
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
                <div
                    style={{
                        position: "absolute",
                        inset: 0,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        pointerEvents: "none",
                    }}
                >
                    <div style={{ fontSize: 22, fontWeight: 300, color: "#f3efe4", letterSpacing: "-0.02em" }}>
                        {formatValue(total)}
                    </div>
                    <div style={{ fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: CHART.axis }}>
                        {centerCaption}
                    </div>
                </div>
            </div>

            <ul style={{ margin: "14px 0 0", padding: 0, listStyle: "none" }}>
                {rows.map((r, i) => {
                    const v = Number(r[dataKey]) || 0;
                    return (
                        <li
                            key={i}
                            className="list-row"
                            onMouseEnter={() => setActive(i)}
                            onMouseLeave={() => setActive(null)}
                            style={{ padding: "6px 10px", fontSize: 12 }}
                        >
                            <span style={{ width: 8, height: 8, flexShrink: 0, borderRadius: 2, background: r._fill }} />
                            <span
                                style={{
                                    flex: 1,
                                    minWidth: 0,
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    whiteSpace: "nowrap",
                                    color: "#cfd8e8",
                                }}
                            >
                                {String(r[nameKey])}
                            </span>
                            <span style={{ color: CHART.text, fontVariantNumeric: "tabular-nums" }}>
                                {total > 0 ? ((v / total) * 100).toFixed(1) : "0.0"}%
                            </span>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}