"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { memo, useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Bot,
  Brain,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  GitBranch,
  LayoutDashboard,
  Menu,
  Monitor,
  Network,
  Plug,
  ShieldCheck,
  TrendingUp,
  Upload,
  Users,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { useApi } from "@/hooks/useApi";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const NAV: { section: string; items: NavItem[] }[] = [
  {
    section: "Overview",
    items: [
      { label: "Command Center", href: "/dashboard", icon: LayoutDashboard },
      { label: "Upload Data", href: "/upload", icon: Upload },
    ],
  },
  {
    section: "Planning",
    items: [
      { label: "S&OP Executive", href: "/sop", icon: Users },
      { label: "Unified IBP", href: "/ibp-unified", icon: Workflow },
    ],
  },
  {
    section: "Intelligence",
    items: [
      { label: "Analytics", href: "/analytics", icon: BarChart3 },
      { label: "Reports", href: "/analytics-reports", icon: FileText },
      { label: "Graph Network", href: "/graph", icon: Network },
      { label: "AI Co-Pilot", href: "/copilot", icon: Bot },
      { label: "Risk Propagation", href: "/causal", icon: TrendingUp },
      { label: "Explainability", href: "/xai", icon: Brain },
    ],
  },
  {
    section: "Operations",
    items: [
      { label: "Control Tower", href: "/control-tower", icon: Monitor },
      { label: "Mitigation Loop", href: "/mitigation", icon: ShieldCheck },
      { label: "Agent Traces", href: "/agent-traces", icon: Activity },
      { label: "Connectors", href: "/connectors", icon: Plug },
      { label: "Pipeline", href: "/pipeline", icon: GitBranch },
      { label: "Export", href: "/export", icon: Download },
    ],
  },
];

/* Mobile bottom bar: the most-used pages plus the drawer trigger */
const QUICK: (NavItem & { short: string })[] = [
  { label: "Command Center", short: "Command", href: "/dashboard", icon: LayoutDashboard },
  { label: "Upload Data", short: "Upload", href: "/upload", icon: Upload },
  { label: "Graph Network", short: "Graph", href: "/graph", icon: Network },
  { label: "AI Co-Pilot", short: "Co-Pilot", href: "/copilot", icon: Bot },
];

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(href + "/");
}

export default memo(function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [open, setOpen] = useState(false);
  const [mobile, setMobile] = useState(false);

  /* Real backend status instead of a hardcoded "Online" */
  const { data: health, error: healthError } = useApi<unknown>("/system/health", {
    ttl: 30000,
  });
  const unreachable =
    !!healthError &&
    (healthError.code === "network" ||
      healthError.code === "timeout" ||
      healthError.code === "server_5xx");
  const status: "checking" | "online" | "offline" = unreachable
    ? "offline"
    : health || healthError
      ? "online"
      : "checking";
  const statusColor =
    status === "online"
      ? "var(--color-ok)"
      : status === "offline"
        ? "var(--color-danger)"
        : "var(--color-text-3)";
  const statusText =
    status === "online" ? "Online" : status === "offline" ? "Offline" : "Checking";

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 768px)");
    const update = () => setMobile(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  /* Collapsing only applies on desktop; the mobile drawer is always full width */
  const isCollapsed = collapsed && !mobile;
  const closeDrawer = () => setOpen(false);

  return (
    <>
      <aside
        id="nx-sidebar"
        className={`sidebar ${open ? "open" : ""}`}
        aria-label="Primary navigation"
        style={
          mobile
            ? undefined
            : {
              width: isCollapsed ? "var(--sidebar-collapsed)" : undefined,
              transition: "width 200ms var(--ease)",
            }
        }
      >
        <Link
          href="/"
          className="sidebar-logo"
          aria-label="NEXUS home"
          onClick={closeDrawer}
          style={isCollapsed ? { padding: "18px 14px 14px" } : undefined}
        >
          <span className="sidebar-logo-icon">N</span>
          {!isCollapsed && <span className="sidebar-logo-text">NEXUS</span>}
        </Link>

        <nav className="sidebar-nav">
          {NAV.map((group) => (
            <div key={group.section}>
              {!isCollapsed && <div className="sidebar-section">{group.section}</div>}
              {isCollapsed && <div style={{ height: 12 }} aria-hidden="true" />}
              {group.items.map((item) => {
                const active = isActive(pathname, item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    title={isCollapsed ? item.label : undefined}
                    aria-label={item.label}
                    aria-current={active ? "page" : undefined}
                    className={`sidebar-link ${active ? "active" : ""}`}
                    onClick={closeDrawer}
                    style={
                      isCollapsed
                        ? { justifyContent: "center", padding: "9px 0" }
                        : undefined
                    }
                  >
                    <item.icon size={16} strokeWidth={1.6} style={{ flexShrink: 0 }} />
                    {!isCollapsed && <span>{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        <div
          style={{
            padding: 8,
            borderTop: "1px solid var(--color-border)",
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {!isCollapsed && (
            <div
              role="status"
              style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px" }}
            >
              <span
                aria-hidden="true"
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: statusColor,
                  flexShrink: 0,
                }}
              />
              <span style={{ fontSize: 11, color: "var(--color-text-3)" }}>
                v3.0 · {statusText}
              </span>
            </div>
          )}

          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!isCollapsed}
            className={`sidebar-collapse-btn max-md:hidden ${isCollapsed ? "justify-center" : ""}`}
          >
            {isCollapsed ? (
              <ChevronRight size={14} />
            ) : (
              <>
                <ChevronLeft size={14} />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      {/* Mobile: backdrop for the drawer */}
      {open && (
        <div
          className="modal-backdrop fixed inset-0 z-[90] md:hidden"
          onClick={closeDrawer}
          aria-hidden="true"
        />
      )}

      {/* Mobile: bottom bar (hidden above 768px by globals.css) */}
      <nav className="bottom-nav" aria-label="Quick navigation">
        {QUICK.map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-label={item.label}
              aria-current={active ? "page" : undefined}
              className={`bottom-nav-item ${active ? "active" : ""}`}
            >
              <item.icon size={18} strokeWidth={1.6} />
              <span>{item.short}</span>
            </Link>
          );
        })}
        <button
          type="button"
          className="bottom-nav-item"
          aria-label="Open menu"
          aria-expanded={open}
          aria-controls="nx-sidebar"
          onClick={() => setOpen(true)}
          style={{ background: "transparent", border: "none", cursor: "pointer" }}
        >
          <Menu size={18} strokeWidth={1.6} />
          <span>Menu</span>
        </button>
      </nav>
    </>
  );
});