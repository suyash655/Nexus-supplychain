"use client";

/**
 * Skeleton Loader Components
 * ===========================
 * Enhanced skeletons with loading states and subtle animations for better UX.
 */

export function SkeletonCard({ height = 120 }: { height?: number }) {
  return (
    <div 
      className="skeleton skeleton-card" 
      style={{ 
        height,
        animation: "pulse-glow 2s ease-in-out infinite"
      }} 
    />
  );
}

export function SkeletonText({ lines = 3, width = "100%" }: { lines?: number; width?: string }) {
  return (
    <div style={{ width }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton-text"
          style={{ 
            width: i === lines - 1 ? "60%" : "100%",
            animation: `pulse-glow 2s ease-in-out ${i * 0.2}s infinite`
          }}
        />
      ))}
    </div>
  );
}

export function SkeletonKPI() {
  return (
    <div 
      className="card-static" 
      style={{ 
        padding: 20,
        transition: "opacity 0.3s ease"
      }}
    >
      <div 
        className="skeleton" 
        style={{ 
          width: 80, 
          height: 14, 
          marginBottom: 10,
          animation: "pulse-glow 2s ease-in-out infinite"
        }} 
      />
      <div 
        className="skeleton" 
        style={{ 
          width: 120, 
          height: 28, 
          marginBottom: 8,
          animation: "pulse-glow 2s ease-in-out 0.3s infinite"
        }} 
      />
      <div 
        className="skeleton" 
        style={{ 
          width: 60, 
          height: 12,
          animation: "pulse-glow 2s ease-in-out 0.6s infinite"
        }} 
      />
    </div>
  );
}

export function SkeletonChart({ height = 200 }: { height?: number }) {
  return (
    <div className="card-static" style={{ padding: 20 }}>
      <div 
        className="skeleton" 
        style={{ 
          width: 160, 
          height: 16, 
          marginBottom: 16,
          animation: "pulse-glow 2s ease-in-out infinite"
        }} 
      />
      <div 
        className="skeleton skeleton-chart" 
        style={{ 
          height,
          animation: "pulse-glow 2s ease-in-out 0.4s infinite"
        }} 
      />
      {/* Fake axis lines */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
        {[1, 2, 3, 4, 5].map(i => (
          <div 
            key={i} 
            className="skeleton" 
            style={{ 
              width: 30, 
              height: 10,
              animation: `pulse-glow 2s ease-in-out ${i * 0.1}s infinite`
            }} 
          />
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
          <div 
            key={i} 
            className="skeleton" 
            style={{ 
              width: w, 
              height: 12,
              animation: `pulse-glow 2s ease-in-out ${i * 0.15}s infinite`
            }} 
          />
        ))}
      </div>
      {/* Data rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div 
          key={i} 
          style={{ 
            display: "flex", 
            gap: 16, 
            padding: "12px 16px", 
            borderBottom: "1px solid var(--color-border-subtle)", 
            opacity: 1 - i * 0.1,
            transition: "opacity 0.3s ease"
          }}
        >
          {[120, 100, 80, 60].map((w, j) => (
            <div 
              key={j} 
              className="skeleton" 
              style={{ 
                width: w, 
                height: 12,
                animation: `pulse-glow 2s ease-in-out ${(i * 0.1) + (j * 0.05)}s infinite`
              }} 
            />
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
