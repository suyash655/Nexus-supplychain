"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Search, Bell, LogOut } from "lucide-react";

// Breadcrumb map: pathname → [Section, Page]
const BREADCRUMBS: Record<string, [string, string]> = {
  "/dashboard":  ["Overview",     "Command Center"],
  "/upload":     ["Overview",     "Upload Data"],
  "/analytics":  ["Intelligence", "Analytics"],
  "/graph":      ["Intelligence", "Graph Network"],
  "/copilot":    ["Intelligence", "AI Co-Pilot"],
  "/causal":     ["Intelligence", "Risk Propagation"],
  "/xai":        ["Intelligence", "Explainability"],
  "/connectors": ["Operations",   "Connectors"],
  "/pipeline":   ["Operations",   "Pipeline"],
  "/export":     ["Operations",   "Export"],
};

const T = "cubic-bezier(0.16, 1, 0.3, 1)";

export default function TopNav() {
  const router   = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<{ full_name?: string; username?: string; email?: string } | null>(null);

  useEffect(() => {
    try {
      const u = localStorage.getItem("nexus_user");
      if (u) setUser(JSON.parse(u));
    } catch { /* ignore */ }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("nexus_token");
    localStorage.removeItem("nexus_user");
    document.cookie = "nexus_token=; path=/; max-age=0; SameSite=Lax";
    router.push("/login");
  };

  const [section, page] = BREADCRUMBS[pathname] ?? ["", "Nexus"];

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : user?.username?.slice(0, 2).toUpperCase() ?? "NX";

  return (
    <header
      style={{
        height:          "var(--topnav-height)",
        display:         "flex",
        alignItems:      "center",
        justifyContent:  "space-between",
        padding:         "0 24px",
        borderBottom:    "1px solid var(--color-border)",
        background:      "var(--color-bg)",
        position:        "sticky",
        top:             0,
        zIndex:          50,
        flexShrink:      0,
      }}
    >
      {/* ── Left: breadcrumb ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 0 }}>
        {section && (
          <>
            <span style={{ fontSize: 12, color: "var(--color-text-3)", whiteSpace: "nowrap" }}>
              {section}
            </span>
            <span style={{ fontSize: 12, color: "var(--color-border-hi)" }}>/</span>
          </>
        )}
        <span style={{ fontSize: 12, color: "var(--color-text-2)", fontWeight: 500, whiteSpace: "nowrap" }}>
          {page}
        </span>
      </div>

      {/* ── Centre: search ── */}
      <div
        tabIndex={0}
        role="button"
        aria-label="Search (⌘K)"
        style={{
          display:       "flex",
          alignItems:    "center",
          gap:           8,
          padding:       "6px 12px",
          background:    "var(--color-surface)",
          border:        "1px solid var(--color-border)",
          borderRadius:  "var(--radius-md)",
          color:         "var(--color-text-3)",
          fontSize:      12,
          cursor:        "pointer",
          minWidth:      220,
          maxWidth:      320,
          transition:    `border-color 120ms ${T}`,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--color-border-hi)")}
        onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
      >
        <Search size={13} />
        <span style={{ flex: 1 }}>Search…</span>
        <kbd
          style={{
            fontSize:     10,
            fontFamily:   "var(--font-mono)",
            padding:      "1px 5px",
            background:   "var(--color-surface-2)",
            borderRadius: 3,
            color:        "var(--color-text-3)",
          }}
        >
          ⌘K
        </kbd>
      </div>

      {/* ── Right: actions ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        {/* Notifications */}
        <button
          aria-label="Notifications"
          style={{
            display:        "flex",
            alignItems:     "center",
            justifyContent: "center",
            width:          32,
            height:         32,
            borderRadius:   "var(--radius-sm)",
            border:         "none",
            background:     "transparent",
            color:          "var(--color-text-2)",
            cursor:         "pointer",
            position:       "relative",
            transition:     `background 120ms ${T}, color 120ms ${T}`,
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-1)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = "transparent";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-2)";
          }}
        >
          <Bell size={15} />
          {/* Notification dot */}
          <span
            style={{
              position:     "absolute",
              top:          6,
              right:        6,
              width:        5,
              height:       5,
              borderRadius: "50%",
              background:   "var(--color-danger)",
              border:       "1px solid var(--color-bg)",
            }}
          />
        </button>

        {/* Logout */}
        <button
          onClick={handleLogout}
          aria-label="Log out"
          style={{
            display:        "flex",
            alignItems:     "center",
            justifyContent: "center",
            width:          32,
            height:         32,
            borderRadius:   "var(--radius-sm)",
            border:         "none",
            background:     "transparent",
            color:          "var(--color-text-2)",
            cursor:         "pointer",
            transition:     `background 120ms ${T}, color 120ms ${T}`,
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-1)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = "transparent";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-2)";
          }}
        >
          <LogOut size={15} />
        </button>

        {/* Divider */}
        <div
          style={{
            width:      1,
            height:     20,
            background: "var(--color-border)",
            margin:     "0 4px",
          }}
        />

        {/* Avatar */}
        <div
          title={user?.email ?? "Account"}
          style={{
            width:          28,
            height:         28,
            borderRadius:   "var(--radius-full)",
            background:     "var(--color-surface-2)",
            border:         "1px solid var(--color-border-hi)",
            display:        "flex",
            alignItems:     "center",
            justifyContent: "center",
            fontSize:       11,
            fontWeight:     600,
            color:          "var(--color-text-1)",
            cursor:         "pointer",
            flexShrink:     0,
            transition:     `border-color 120ms ${T}`,
          }}
          onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-accent)")}
          onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.borderColor = "var(--color-border-hi)")}
        >
          {initials}
        </div>
      </div>
    </header>
  );
}
