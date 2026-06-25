"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Upload, BarChart3, Network, Bot, Download,
  Brain, Dna, Plug, GitBranch, ChevronLeft, ChevronRight,
  TrendingUp, Settings,
} from "lucide-react";
import { useState } from "react";

const NAV = [
  {
    section: "Overview",
    items: [
      { label: "Command Center", href: "/dashboard",  icon: LayoutDashboard },
      { label: "Upload Data",    href: "/upload",     icon: Upload          },
    ],
  },
  {
    section: "Intelligence",
    items: [
      { label: "Analytics",        href: "/analytics",  icon: BarChart3  },
      { label: "Graph Network",    href: "/graph",      icon: Network    },
      { label: "AI Co-Pilot",      href: "/copilot",    icon: Bot        },
      { label: "Risk Propagation", href: "/causal",     icon: TrendingUp },
      { label: "Explainability",   href: "/xai",        icon: Brain      },
    ],
  },
  {
    section: "Operations",
    items: [
      { label: "Connectors",  href: "/connectors", icon: Plug      },
      { label: "Pipeline",    href: "/pipeline",   icon: GitBranch },
      { label: "Export",      href: "/export",     icon: Download  },
    ],
  },
];

const T = {
  ease: "cubic-bezier(0.16, 1, 0.3, 1)",
};

export default function Sidebar() {
  const pathname  = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      style={{
        width:          collapsed ? "var(--sidebar-collapsed)" : "var(--sidebar-width)",
        height:         "100vh",
        display:        "flex",
        flexDirection:  "column",
        background:     "var(--color-bg)",
        borderRight:    "1px solid var(--color-border)",
        flexShrink:     0,
        overflowY:      "auto",
        overflowX:      "hidden",
        transition:     `width 160ms ${T.ease}`,
      }}
    >
      {/* ── Logo ── */}
      <Link
        href="/"
        style={{
          display:        "flex",
          alignItems:     "center",
          gap:            10,
          padding:        collapsed ? "14px 12px" : "14px 16px",
          borderBottom:   "1px solid var(--color-border)",
          textDecoration: "none",
          overflow:       "hidden",
        }}
      >
        <div
          style={{
            width:          28,
            height:         28,
            borderRadius:   4,
            background:     "var(--color-accent)",
            display:        "flex",
            alignItems:     "center",
            justifyContent: "center",
            fontWeight:     700,
            fontSize:       13,
            color:          "#0A0A0A",
            flexShrink:     0,
          }}
        >
          N
        </div>
        {!collapsed && (
          <span
            style={{
              fontSize:    14,
              fontWeight:  700,
              color:       "var(--color-text-1)",
              letterSpacing: "0.02em",
              whiteSpace:  "nowrap",
              opacity:     1,
              transition:  `opacity 120ms ${T.ease}`,
            }}
          >
            NEXUS
          </span>
        )}
      </Link>

      {/* ── Nav ── */}
      <nav style={{ flex: 1, padding: "8px" }}>
        {NAV.map((group) => (
          <div key={group.section}>
            {!collapsed && (
              <div
                style={{
                  fontSize:      10,
                  fontWeight:    500,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color:         "var(--color-text-3)",
                  padding:       "14px 8px 4px",
                }}
              >
                {group.section}
              </div>
            )}
            {group.items.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  title={collapsed ? item.label : undefined}
                  style={{
                    display:       "flex",
                    alignItems:    "center",
                    gap:           8,
                    padding:       "7px 12px",
                    paddingLeft:   active ? 10 : 12,
                    borderRadius:  4,
                    borderLeft:    active ? "2px solid var(--color-accent)" : "2px solid transparent",
                    color:         active ? "var(--color-accent)" : "var(--color-text-2)",
                    fontWeight:    active ? 500 : 400,
                    fontSize:      13,
                    textDecoration:"none",
                    whiteSpace:    "nowrap",
                    transition:    `background 120ms ${T.ease}, color 120ms ${T.ease}`,
                    overflow:      "hidden",
                    position:      "relative",
                  }}
                  onMouseEnter={(e) => {
                    if (!active) {
                      (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
                      (e.currentTarget as HTMLElement).style.color      = "var(--color-text-1)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!active) {
                      (e.currentTarget as HTMLElement).style.background = "transparent";
                      (e.currentTarget as HTMLElement).style.color      = "var(--color-text-2)";
                    }
                  }}
                >
                  <item.icon size={15} style={{ flexShrink: 0 }} />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* ── Footer ── */}
      <div
        style={{
          padding:      "8px",
          borderTop:    "1px solid var(--color-border)",
          display:      "flex",
          flexDirection:"column",
          gap:          4,
        }}
      >
        {/* Status */}
        {!collapsed && (
          <div
            style={{
              display:     "flex",
              alignItems:  "center",
              gap:         6,
              padding:     "6px 12px",
              borderRadius:4,
            }}
          >
            <span
              style={{
                width:        6,
                height:       6,
                borderRadius: "50%",
                background:   "var(--color-ok)",
                flexShrink:   0,
              }}
            />
            <span style={{ fontSize: 11, color: "var(--color-text-3)" }}>
              v3.0 · Online
            </span>
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          style={{
            display:        "flex",
            alignItems:     "center",
            justifyContent: collapsed ? "center" : "flex-start",
            gap:            8,
            padding:        "7px 12px",
            borderRadius:   4,
            border:         "none",
            background:     "transparent",
            color:          "var(--color-text-3)",
            cursor:         "pointer",
            fontSize:       13,
            fontFamily:     "var(--font-sans)",
            width:          "100%",
            transition:     `background 120ms ${T.ease}, color 120ms ${T.ease}`,
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-1)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = "transparent";
            (e.currentTarget as HTMLElement).style.color      = "var(--color-text-3)";
          }}
        >
          {collapsed ? <ChevronRight size={14} /> : <><ChevronLeft size={14} /><span>Collapse</span></>}
        </button>
      </div>
    </aside>
  );
}
