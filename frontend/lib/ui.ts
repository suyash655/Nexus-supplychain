/**
 * UI & Chart Styling Tokens & Helper Utilities
 * Used by Recharts visual components and dashboard widgets.
 */

export const CHART = {
  axis: "#64748b",      // Axis ticks and active cursors
  grid: "#1e293b",      // Cartesian grid stroke lines
  text: "#94a3b8",      // Tooltip labels and legend captions
  blue: "#38bdf8",      // Primary data line/bar/area color
  brass: "#eab308",     // Secondary brass / warm gold tone
  sage: "#22c55e",      // Healthy / positive green tone
  amber: "#f59e0b",     // Warning / elevated risk amber tone
  red: "#ef4444",       // Critical / danger red tone
} as const;

export const NEUTRAL_PALETTE = [
  "#38bdf8",
  "#818cf8",
  "#34d399",
  "#fbbf24",
  "#f87171",
  "#a78bfa",
  "#3b82f6",
  "#ec4899",
  "#64748b",
] as const;

/**
 * Returns the semantic hex color for a given risk tier name,
 * or undefined if the tier is unknown (allowing fallback to NEUTRAL_PALETTE).
 */
export function tierColor(tier?: string): string | undefined {
  if (!tier) return undefined;
  const t = tier.toLowerCase().trim();
  if (t === "critical" || t === "catastrophic" || t === "severe") return "#ef4444";
  if (t === "elevated" || t === "high") return "#f59e0b";
  if (t === "moderate" || t === "medium") return "#eab308";
  if (t === "stable" || t === "low") return "#22c55e";
  return undefined;
}

/**
 * Formats numbers into compact human-readable representations:
 * e.g. 1500000 -> "1.5M", 1240 -> "1.2k", 42 -> "42"
 */
export function formatCompact(value: number): string {
  if (value == null || isNaN(value)) return "0";
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(1).replace(/\.0$/, "")}k`;
  }
  if (Number.isInteger(value)) {
    return value.toString();
  }
  return value.toFixed(1);
}

/** Formats a number to 1 decimal place. e.g. 4.7 */
export function formatDecimal(value: number): string {
  if (value == null || isNaN(value)) return "0.0";
  return value.toFixed(1);
}

/** Formats a delay value in days. e.g. "4.7d" */
export function formatDelay(value: number | null | undefined): string {
  if (value == null || isNaN(Number(value))) return "—";
  return `${Number(value).toFixed(1)}d`;
}

/** Formats a number as a currency value. e.g. "$1,420,000" */
export function formatInr(value: number | null | undefined): string {
  if (value == null || isNaN(Number(value))) return "—";
  const num = Number(value);
  const formatted = Math.abs(num).toLocaleString("en-US", { maximumFractionDigits: 0 });
  return num < 0 ? `-$${formatted}` : `$${formatted}`;
}

/** Formats a number as compact currency. e.g. "$1.4M" */
export function formatInrCompact(value: number): string {
  if (value == null || isNaN(value)) return "$0";
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (abs >= 1_000) return `${sign}$${(abs / 1_000).toFixed(1).replace(/\.0$/, "")}k`;
  return `${sign}$${abs.toFixed(0)}`;
}

/** Formats a number with locale separators. e.g. "1,420" */
export function formatNumber(value: number | null | undefined): string {
  if (value == null || isNaN(Number(value))) return "0";
  return Number(value).toLocaleString("en-US", { maximumFractionDigits: 1 });
}

/** Returns a CSS hex color string based on 0-100 risk score (for color prop). */
export function scoreVar(score: number): string {
  if (score >= 70) return "#ef4444";   // critical red
  if (score >= 40) return "#f59e0b";   // elevated amber
  return "#22c55e";                     // stable green
}

/** Returns a hex color string based on 0-100 risk score (for colorBy callbacks). */
export function scoreColor(score: number): string {
  return scoreVar(score);
}

/** Truncates a supplier name to maxLen characters with ellipsis. */
export function shortName(name: string, maxLen = 12): string {
  if (!name) return "";
  return name.length > maxLen ? name.slice(0, maxLen - 1) + "…" : name;
}

