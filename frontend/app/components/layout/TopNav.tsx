"use client";

import { useState, useRef, useEffect, memo } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Search, Bell, LogOut, X } from "lucide-react";

// Breadcrumb map: pathname → [Section, Page]
const BREADCRUMBS: Record<string, [string, string]> = {
  "/dashboard":  ["Overview",     "Command Center"],
  "/upload":     ["Overview",     "Upload Data"],
  "/analytics":  ["Intelligence", "Analytics"],
  "/analytics-reports": ["Intelligence", "Analytics Reports"],
  "/graph":      ["Intelligence", "Graph Network"],
  "/copilot":    ["Intelligence", "AI Co-Pilot"],
  "/causal":     ["Intelligence", "Risk Propagation"],
  "/xai":        ["Intelligence", "Explainability"],
  "/sop":        ["Planning",     "S&OP Executive"],
  "/ibp-unified": ["Planning",    "Unified IBP"],
  "/connectors": ["Operations",   "Connectors"],
  "/pipeline":   ["Operations",   "Pipeline"],
  "/export":     ["Operations",   "Export"],
  "/control-tower": ["Operations", "Control Tower"],
};

const T = "cubic-bezier(0.16, 1, 0.3, 1)";

const SEARCH_ACTIONS = [
  { label: "Command Center", keywords: "dashboard overview home kpi", path: "/dashboard" },
  { label: "Upload Data", keywords: "upload csv excel file ingestion", path: "/upload" },
  { label: "Analytics", keywords: "analytics charts metrics reports", path: "/analytics" },
  { label: "Analytics Reports", keywords: "reports schedule subscriptions export analytics", path: "/analytics-reports" },
  { label: "Graph Network", keywords: "graph network suppliers dependencies", path: "/graph" },
  { label: "AI Co-Pilot", keywords: "copilot chat assistant rag", path: "/copilot" },
  { label: "Risk Propagation", keywords: "causal risk fragility intervention", path: "/causal" },
  { label: "Explainability", keywords: "xai feature importance counterfactuals", path: "/xai" },
  { label: "S&OP Executive", keywords: "sop planning forecast consensus", path: "/sop" },
  { label: "Unified IBP", keywords: "ibp planning orchestrator scenarios", path: "/ibp-unified" },
  { label: "Connectors", keywords: "connectors database api s3 csv", path: "/connectors" },
  { label: "Pipeline", keywords: "pipeline quality lineage history", path: "/pipeline" },
  { label: "Export", keywords: "export tableau powerbi csv json", path: "/export" },
  { label: "Control Tower", keywords: "control tower alerts incidents operations", path: "/control-tower" },
];

export default memo(function TopNav() {
  const router   = useRouter();
  const pathname = usePathname();
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchRef = useRef<HTMLDivElement>(null);
  
  const [user] = useState<{ full_name?: string; username?: string; email?: string } | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const u = localStorage.getItem("nexus_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  });

  // Close search when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
      if (event.key === "Escape" && searchOpen) {
        setSearchOpen(false);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [searchOpen]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const quickActions = SEARCH_ACTIONS.slice(0, 4);
  const normalizedQuery = searchQuery.trim().toLowerCase();
  const searchResults = normalizedQuery
    ? SEARCH_ACTIONS.filter((action) =>
        `${action.label} ${action.keywords}`.toLowerCase().includes(normalizedQuery)
      ).slice(0, 8)
    : quickActions;

  const navigateTo = (path: string) => {
    router.push(path);
    setSearchOpen(false);
    setSearchQuery("");
  };

  const handleLogout = () => {
    localStorage.removeItem("nexus_token");
    localStorage.removeItem("nexus_user");
    localStorage.removeItem("nexus_demo_mode");
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
      <div ref={searchRef} style={{ position: "relative" }}>
        <div
          tabIndex={0}
          role="button"
          aria-label="Search (⌘K)"
          onClick={() => setSearchOpen(true)}
          className="topnav-search"
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

        {/* Search Dropdown */}
        {searchOpen && (
          <div
            style={{
              position: "absolute",
              top: "calc(100% + 8px)",
              left: 0,
              right: 0,
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-md)",
              boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
              zIndex: 100,
              padding: 12,
              minWidth: 320,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Search size={16} style={{ color: "var(--color-text-3)" }} />
              <input
                autoFocus
                type="text"
                placeholder="Search pages, suppliers, metrics..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && searchResults[0]) {
                    navigateTo(searchResults[0].path);
                  }
                }}
                style={{
                  flex: 1,
                  background: "transparent",
                  border: "none",
                  color: "var(--color-text-1)",
                  fontSize: 13,
                  outline: "none",
                  fontFamily: "var(--font-sans)",
                }}
              />
              <button
                onClick={() => {
                  setSearchOpen(false);
                  setSearchQuery("");
                }}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--color-text-3)",
                  cursor: "pointer",
                  padding: 4,
                  borderRadius: 4,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <X size={14} />
              </button>
            </div>

            <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: 8, marginBottom: 8 }}>
              <div style={{ fontSize: 11, color: "var(--color-text-3)", marginBottom: 8, fontWeight: 500 }}>
                QUICK ACTIONS
              </div>
              {searchResults.map((action) => (
                <button
                  key={action.path}
                  onClick={() => navigateTo(action.path)}
                  className="search-result-btn"
                >
                  <span style={{ fontSize: 14 }}>→</span>
                  {action.label}
                </button>
              ))}
              {searchResults.length === 0 && (
                <div style={{ fontSize: 12, color: "var(--color-text-3)", padding: "8px 12px" }}>
                  No matching pages found.
                </div>
              )}
            </div>

            {searchQuery.length > 2 && (
              <div style={{ fontSize: 11, color: "var(--color-text-3)", textAlign: "center", padding: 8 }}>
                Press Enter to open the first match
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Right: actions ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        {/* Notifications */}
        <button
          aria-label="Notifications"
          className="topnav-btn"
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
          className="topnav-btn"
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
          className="topnav-avatar"
        >
          {initials}
        </div>
      </div>
    </header>
  );
});
