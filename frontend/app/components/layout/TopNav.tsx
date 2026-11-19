"use client";

import { memo, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, Search, X } from "lucide-react";

// Breadcrumb map: pathname -> [Section, Page]
const BREADCRUMBS: Record<string, [string, string]> = {
  "/dashboard": ["Overview", "Command Center"],
  "/upload": ["Overview", "Upload Data"],
  "/upload/map": ["Overview", "Map Columns"],
  "/analytics": ["Intelligence", "Analytics"],
  "/analytics-reports": ["Intelligence", "Analytics Reports"],
  "/graph": ["Intelligence", "Graph Network"],
  "/copilot": ["Intelligence", "AI Co-Pilot"],
  "/causal": ["Intelligence", "Risk Propagation"],
  "/xai": ["Intelligence", "Explainability"],
  "/sop": ["Planning", "S&OP Executive"],
  "/ibp-unified": ["Planning", "Unified IBP"],
  "/connectors": ["Operations", "Connectors"],
  "/pipeline": ["Operations", "Pipeline"],
  "/export": ["Operations", "Export"],
  "/control-tower": ["Operations", "Control Tower"],
  "/mitigation": ["Operations", "Mitigation Loop"],
  "/agent-traces": ["Operations", "Agent Traces"],
};

function resolveCrumb(pathname: string): [string, string] {
  if (BREADCRUMBS[pathname]) return BREADCRUMBS[pathname];
  const match = Object.keys(BREADCRUMBS)
    .filter((k) => pathname.startsWith(k + "/"))
    .sort((a, b) => b.length - a.length)[0];
  return match ? BREADCRUMBS[match] : ["", "NEXUS"];
}

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
  { label: "Mitigation Loop", keywords: "mitigation agent approval plan", path: "/mitigation" },
  { label: "Agent Traces", keywords: "agent traces langgraph logs", path: "/agent-traces" },
];

interface StoredUser {
  full_name?: string;
  username?: string;
  email?: string;
}

export default memo(function TopNav() {
  const router = useRouter();
  const pathname = usePathname();
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const [isMac, setIsMac] = useState(false);
  const [user, setUser] = useState<StoredUser | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  /* Read browser-only state after mount so server and client markup match */
  useEffect(() => {
    queueMicrotask(() => {
      setIsMac(/Mac|iPhone|iPad/i.test(navigator.platform));
      try {
        const raw = localStorage.getItem("nexus_user");
        if (raw) setUser(JSON.parse(raw));
      } catch {
        /* ignore malformed stored user */
      }
    });
  }, []);

  // Close search when clicking outside
  useEffect(() => {
    const onDown = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  // Keyboard shortcut: Ctrl/Cmd + K, Escape to close
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
        setActiveIndex(0);
      }
      if (event.key === "Escape") setSearchOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const normalizedQuery = searchQuery.trim().toLowerCase();
  const searchResults = normalizedQuery
    ? SEARCH_ACTIONS.filter((a) =>
      `${a.label} ${a.keywords}`.toLowerCase().includes(normalizedQuery)
    ).slice(0, 8)
    : SEARCH_ACTIONS.slice(0, 5);

  const closeSearch = () => {
    setSearchOpen(false);
    setSearchQuery("");
    setActiveIndex(0);
  };

  const navigateTo = (path: string) => {
    router.push(path);
    closeSearch();
  };

  const handleLogout = () => {
    localStorage.removeItem("nexus_token");
    localStorage.removeItem("nexus_user");
    localStorage.removeItem("nexus_demo_mode");
    document.cookie = "nexus_token=; path=/; max-age=0; SameSite=Lax";
    router.push("/login");
  };

  const [section, page] = resolveCrumb(pathname);

  const initials = user?.full_name
    ? user.full_name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase()
    : user?.username?.slice(0, 2).toUpperCase() ?? "NX";

  return (
    <header className="topnav">
      {/* Left: breadcrumb (hidden on phones to leave room for search) */}
      <div className="hidden min-w-0 items-center gap-2 sm:flex">
        {section && (
          <>
            <span style={{ fontSize: 12, color: "var(--color-text-3)", whiteSpace: "nowrap" }}>
              {section}
            </span>
            <span aria-hidden="true" style={{ fontSize: 12, color: "var(--color-border-hi)" }}>
              /
            </span>
          </>
        )}
        <span
          aria-current="page"
          style={{ fontSize: 12, color: "var(--color-text-1)", fontWeight: 500, whiteSpace: "nowrap" }}
        >
          {page}
        </span>
      </div>

      {/* Centre: search */}
      <div ref={searchRef} className="relative min-w-0 flex-1 sm:w-[360px] sm:flex-none lg:w-[420px]">
        <button
          type="button"
          className="topnav-search w-full"
          aria-label="Search pages"
          aria-haspopup="dialog"
          aria-expanded={searchOpen}
          onClick={() => {
            setSearchOpen(true);
            setActiveIndex(0);
          }}
        >
          <Search size={14} aria-hidden="true" />
          <span style={{ flex: 1, textAlign: "left" }}>Search…</span>
          <kbd aria-hidden="true">{isMac ? "⌘K" : "Ctrl K"}</kbd>
        </button>

        {searchOpen && (
          <div
            role="dialog"
            aria-label="Search pages"
            className="menu-panel fixed left-4 right-4 top-[calc(var(--topnav-height)+8px)] z-[100] p-3 md:absolute md:left-0 md:right-0 md:top-[calc(100%+8px)] md:min-w-[360px]"
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <Search size={15} aria-hidden="true" style={{ color: "var(--color-text-3)" }} />
              <input
                autoFocus
                type="text"
                aria-label="Search pages"
                placeholder="Search pages and tools"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setActiveIndex(0);
                }}
                onKeyDown={(e) => {
                  if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setActiveIndex((i) => Math.min(i + 1, searchResults.length - 1));
                  } else if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActiveIndex((i) => Math.max(i - 1, 0));
                  } else if (e.key === "Enter" && searchResults[activeIndex]) {
                    navigateTo(searchResults[activeIndex].path);
                  }
                }}
                style={{
                  flex: 1,
                  background: "transparent",
                  border: "none",
                  color: "var(--color-text-1)",
                  fontSize: 14,
                  outline: "none",
                  minWidth: 0,
                }}
              />
              <button
                type="button"
                onClick={closeSearch}
                aria-label="Close search"
                className="topnav-btn"
                style={{ width: 28, height: 28 }}
              >
                <X size={14} />
              </button>
            </div>

            <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: 8 }}>
              <div className="text-micro" style={{ padding: "0 4px 6px" }}>
                {normalizedQuery ? "Results" : "Quick actions"}
              </div>
              {searchResults.map((action, i) => (
                <button
                  key={action.path}
                  type="button"
                  className="search-result-btn"
                  onClick={() => navigateTo(action.path)}
                  onMouseEnter={() => setActiveIndex(i)}
                  style={
                    i === activeIndex
                      ? { background: "rgba(140, 170, 220, 0.09)" }
                      : undefined
                  }
                >
                  <span>{action.label}</span>
                  <span
                    style={{
                      marginLeft: "auto",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      color: "var(--color-text-3)",
                    }}
                  >
                    {action.path}
                  </span>
                </button>
              ))}
              {searchResults.length === 0 && (
                <div style={{ fontSize: 12, color: "var(--color-text-3)", padding: "8px 12px" }}>
                  No matching pages found.
                </div>
              )}
            </div>

            <div
              className="max-md:hidden"
              style={{
                marginTop: 8,
                paddingTop: 8,
                borderTop: "1px solid var(--color-border)",
                fontSize: 11,
                color: "var(--color-text-3)",
                display: "flex",
                gap: 16,
              }}
            >
              <span>↑↓ to move</span>
              <span>Enter to open</span>
              <span>Esc to close</span>
            </div>
          </div>
        )}
      </div>

      {/* Right: account actions */}
      <div className="topnav-actions">
        <button
          type="button"
          onClick={handleLogout}
          aria-label="Log out"
          title="Log out"
          className="topnav-btn"
        >
          <LogOut size={16} strokeWidth={1.6} />
        </button>

        <div
          aria-hidden="true"
          style={{ width: 1, height: 20, background: "var(--color-border)", margin: "0 4px" }}
        />

        <div
          role="img"
          aria-label={user?.email ?? "Account"}
          title={user?.email ?? "Account"}
          className="topnav-avatar"
        >
          {initials}
        </div>
      </div>
    </header>
  );
});