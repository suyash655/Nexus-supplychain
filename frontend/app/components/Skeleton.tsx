"use client";

/**
 * Skeleton Loader Components
 * ===========================
 * Shimmer skeletons for every content type. Never show blank screens.
 */

export function SkeletonCard({ height = 120 }: { height?: number }) {
  return (
    <div className="skeleton skeleton-card" style={{ height }} />
  );
}

export function SkeletonText({ lines = 3, width = "100%" }: { lines?: number; width?: string }) {
  return (
    <div style={{ width }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton-text"
          style={{ width: i === lines - 1 ? "60%" : "100%" }}
        />
      ))}
    </div>
  );
}

export function SkeletonKPI() {
  return (
    <div className="card-static" style={{ padding: 20 }}>
      <div className="skeleton" style={{ width: 80, height: 14, marginBottom: 10 }} />
      <div className="skeleton" style={{ width: 120, height: 28, marginBottom: 8 }} />
      <div className="skeleton" style={{ width: 60, height: 12 }} />
    </div>
  );
}

export function SkeletonChart({ height = 200 }: { height?: number }) {
  return (
    <div className="card-static" style={{ padding: 20 }}>
      <div className="skeleton" style={{ width: 160, height: 16, marginBottom: 16 }} />
      <div className="skeleton skeleton-chart" style={{ height }} />
      {/* Fake axis lines */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="skeleton" style={{ width: 30, height: 10 }} />
        ))}
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 6 }: { rows?: number }) {
  return (
    <div className="card-static" style={{ padding: 0, overflow: "hidden" }}>
      {/* Header row */}
      <div style={{ display: "flex", gap: 16, padding: "12px 16px", borderBottom: "1px solid var(--color-border-subtle)" }}>
        {[120, 100, 80, 60].map((w, i) => (
          <div key={i} className="skeleton" style={{ width: w, height: 12 }} />
        ))}
      </div>
      {/* Data rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ display: "flex", gap: 16, padding: "12px 16px", borderBottom: "1px solid var(--color-border-subtle)", opacity: 1 - i * 0.1 }}>
          {[120, 100, 80, 60].map((w, j) => (
            <div key={j} className="skeleton" style={{ width: w, height: 12 }} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonDashboard() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {[1, 2, 3, 4].map(i => <SkeletonKPI key={i} />)}
      </div>
      {/* Chart Row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <SkeletonChart />
        <SkeletonChart />
      </div>
      {/* Table */}
      <SkeletonTable />
    </div>
  );
}
