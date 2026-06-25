(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/app/components/Sidebar.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Sidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$dashboard$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutDashboard$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/layout-dashboard.js [app-client] (ecmascript) <export default as LayoutDashboard>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$upload$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Upload$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/upload.js [app-client] (ecmascript) <export default as Upload>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chart-column.js [app-client] (ecmascript) <export default as BarChart3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$network$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Network$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/network.js [app-client] (ecmascript) <export default as Network>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bot$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bot$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/bot.js [app-client] (ecmascript) <export default as Bot>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/download.js [app-client] (ecmascript) <export default as Download>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/brain.js [app-client] (ecmascript) <export default as Brain>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plug$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plug$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/plug.js [app-client] (ecmascript) <export default as Plug>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-branch.js [app-client] (ecmascript) <export default as GitBranch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-left.js [app-client] (ecmascript) <export default as ChevronLeft>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-right.js [app-client] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trending-up.js [app-client] (ecmascript) <export default as TrendingUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
const NAV = [
    {
        section: "Overview",
        items: [
            {
                label: "Command Center",
                href: "/dashboard",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$dashboard$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutDashboard$3e$__["LayoutDashboard"]
            },
            {
                label: "Upload Data",
                href: "/upload",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$upload$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Upload$3e$__["Upload"]
            }
        ]
    },
    {
        section: "Intelligence",
        items: [
            {
                label: "Analytics",
                href: "/analytics",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"]
            },
            {
                label: "Graph Network",
                href: "/graph",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$network$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Network$3e$__["Network"]
            },
            {
                label: "AI Co-Pilot",
                href: "/copilot",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bot$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bot$3e$__["Bot"]
            },
            {
                label: "Risk Propagation",
                href: "/causal",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trending$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TrendingUp$3e$__["TrendingUp"]
            },
            {
                label: "Explainability",
                href: "/xai",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__["Brain"]
            }
        ]
    },
    {
        section: "Operations",
        items: [
            {
                label: "Connectors",
                href: "/connectors",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plug$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plug$3e$__["Plug"]
            },
            {
                label: "Pipeline",
                href: "/pipeline",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"]
            },
            {
                label: "Export",
                href: "/export",
                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__["Download"]
            }
        ]
    }
];
const T = {
    ease: "cubic-bezier(0.16, 1, 0.3, 1)"
};
function Sidebar() {
    _s();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const [collapsed, setCollapsed] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        style: {
            width: collapsed ? "var(--sidebar-collapsed)" : "var(--sidebar-width)",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            background: "var(--color-bg)",
            borderRight: "1px solid var(--color-border)",
            flexShrink: 0,
            overflowY: "auto",
            overflowX: "hidden",
            transition: `width 160ms ${T.ease}`
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                href: "/",
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: collapsed ? "14px 12px" : "14px 16px",
                    borderBottom: "1px solid var(--color-border)",
                    textDecoration: "none",
                    overflow: "hidden"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            width: 28,
                            height: 28,
                            borderRadius: 4,
                            background: "var(--color-accent)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontWeight: 700,
                            fontSize: 13,
                            color: "#0A0A0A",
                            flexShrink: 0
                        },
                        children: "N"
                    }, void 0, false, {
                        fileName: "[project]/app/components/Sidebar.tsx",
                        lineNumber: 76,
                        columnNumber: 9
                    }, this),
                    !collapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            fontSize: 14,
                            fontWeight: 700,
                            color: "var(--color-text-1)",
                            letterSpacing: "0.02em",
                            whiteSpace: "nowrap",
                            opacity: 1,
                            transition: `opacity 120ms ${T.ease}`
                        },
                        children: "NEXUS"
                    }, void 0, false, {
                        fileName: "[project]/app/components/Sidebar.tsx",
                        lineNumber: 94,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/Sidebar.tsx",
                lineNumber: 64,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                style: {
                    flex: 1,
                    padding: "8px"
                },
                children: NAV.map((group)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            !collapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontSize: 10,
                                    fontWeight: 500,
                                    textTransform: "uppercase",
                                    letterSpacing: "0.05em",
                                    color: "var(--color-text-3)",
                                    padding: "14px 8px 4px"
                                },
                                children: group.section
                            }, void 0, false, {
                                fileName: "[project]/app/components/Sidebar.tsx",
                                lineNumber: 115,
                                columnNumber: 15
                            }, this),
                            group.items.map((item)=>{
                                const active = pathname === item.href;
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: item.href,
                                    title: collapsed ? item.label : undefined,
                                    style: {
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 8,
                                        padding: "7px 12px",
                                        paddingLeft: active ? 10 : 12,
                                        borderRadius: 4,
                                        borderLeft: active ? "2px solid var(--color-accent)" : "2px solid transparent",
                                        color: active ? "var(--color-accent)" : "var(--color-text-2)",
                                        fontWeight: active ? 500 : 400,
                                        fontSize: 13,
                                        textDecoration: "none",
                                        whiteSpace: "nowrap",
                                        transition: `background 120ms ${T.ease}, color 120ms ${T.ease}`,
                                        overflow: "hidden",
                                        position: "relative"
                                    },
                                    onMouseEnter: (e)=>{
                                        if (!active) {
                                            e.currentTarget.style.background = "var(--color-surface-2)";
                                            e.currentTarget.style.color = "var(--color-text-1)";
                                        }
                                    },
                                    onMouseLeave: (e)=>{
                                        if (!active) {
                                            e.currentTarget.style.background = "transparent";
                                            e.currentTarget.style.color = "var(--color-text-2)";
                                        }
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(item.icon, {
                                            size: 15,
                                            style: {
                                                flexShrink: 0
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/app/components/Sidebar.tsx",
                                            lineNumber: 165,
                                            columnNumber: 19
                                        }, this),
                                        !collapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            children: item.label
                                        }, void 0, false, {
                                            fileName: "[project]/app/components/Sidebar.tsx",
                                            lineNumber: 166,
                                            columnNumber: 34
                                        }, this)
                                    ]
                                }, item.href, true, {
                                    fileName: "[project]/app/components/Sidebar.tsx",
                                    lineNumber: 131,
                                    columnNumber: 17
                                }, this);
                            })
                        ]
                    }, group.section, true, {
                        fileName: "[project]/app/components/Sidebar.tsx",
                        lineNumber: 113,
                        columnNumber: 11
                    }, this))
            }, void 0, false, {
                fileName: "[project]/app/components/Sidebar.tsx",
                lineNumber: 111,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: "8px",
                    borderTop: "1px solid var(--color-border)",
                    display: "flex",
                    flexDirection: "column",
                    gap: 4
                },
                children: [
                    !collapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 6,
                            padding: "6px 12px",
                            borderRadius: 4
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    width: 6,
                                    height: 6,
                                    borderRadius: "50%",
                                    background: "var(--color-ok)",
                                    flexShrink: 0
                                }
                            }, void 0, false, {
                                fileName: "[project]/app/components/Sidebar.tsx",
                                lineNumber: 195,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontSize: 11,
                                    color: "var(--color-text-3)"
                                },
                                children: "v3.0 · Online"
                            }, void 0, false, {
                                fileName: "[project]/app/components/Sidebar.tsx",
                                lineNumber: 204,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/components/Sidebar.tsx",
                        lineNumber: 186,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>setCollapsed(!collapsed),
                        style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: collapsed ? "center" : "flex-start",
                            gap: 8,
                            padding: "7px 12px",
                            borderRadius: 4,
                            border: "none",
                            background: "transparent",
                            color: "var(--color-text-3)",
                            cursor: "pointer",
                            fontSize: 13,
                            fontFamily: "var(--font-sans)",
                            width: "100%",
                            transition: `background 120ms ${T.ease}, color 120ms ${T.ease}`
                        },
                        onMouseEnter: (e)=>{
                            e.currentTarget.style.background = "var(--color-surface-2)";
                            e.currentTarget.style.color = "var(--color-text-1)";
                        },
                        onMouseLeave: (e)=>{
                            e.currentTarget.style.background = "transparent";
                            e.currentTarget.style.color = "var(--color-text-3)";
                        },
                        children: collapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                            size: 14
                        }, void 0, false, {
                            fileName: "[project]/app/components/Sidebar.tsx",
                            lineNumber: 238,
                            columnNumber: 24
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__["ChevronLeft"], {
                                    size: 14
                                }, void 0, false, {
                                    fileName: "[project]/app/components/Sidebar.tsx",
                                    lineNumber: 238,
                                    columnNumber: 55
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    children: "Collapse"
                                }, void 0, false, {
                                    fileName: "[project]/app/components/Sidebar.tsx",
                                    lineNumber: 238,
                                    columnNumber: 80
                                }, this)
                            ]
                        }, void 0, true)
                    }, void 0, false, {
                        fileName: "[project]/app/components/Sidebar.tsx",
                        lineNumber: 211,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/Sidebar.tsx",
                lineNumber: 175,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/Sidebar.tsx",
        lineNumber: 49,
        columnNumber: 5
    }, this);
}
_s(Sidebar, "08JhlLD2LM6Uel+hWLLKL/dSZrM=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"]
    ];
});
_c = Sidebar;
var _c;
__turbopack_context__.k.register(_c, "Sidebar");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/components/TopNav.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>TopNav
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Search$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/search.js [app-client] (ecmascript) <export default as Search>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/bell.js [app-client] (ecmascript) <export default as Bell>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/log-out.js [app-client] (ecmascript) <export default as LogOut>");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
// Breadcrumb map: pathname → [Section, Page]
const BREADCRUMBS = {
    "/dashboard": [
        "Overview",
        "Command Center"
    ],
    "/upload": [
        "Overview",
        "Upload Data"
    ],
    "/analytics": [
        "Intelligence",
        "Analytics"
    ],
    "/graph": [
        "Intelligence",
        "Graph Network"
    ],
    "/copilot": [
        "Intelligence",
        "AI Co-Pilot"
    ],
    "/causal": [
        "Intelligence",
        "Risk Propagation"
    ],
    "/xai": [
        "Intelligence",
        "Explainability"
    ],
    "/connectors": [
        "Operations",
        "Connectors"
    ],
    "/pipeline": [
        "Operations",
        "Pipeline"
    ],
    "/export": [
        "Operations",
        "Export"
    ]
};
const T = "cubic-bezier(0.16, 1, 0.3, 1)";
function TopNav() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"])();
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TopNav.useEffect": ()=>{
            try {
                const u = localStorage.getItem("nexus_user");
                if (u) setUser(JSON.parse(u));
            } catch  {}
        }
    }["TopNav.useEffect"], []);
    const handleLogout = ()=>{
        localStorage.removeItem("nexus_token");
        localStorage.removeItem("nexus_user");
        document.cookie = "nexus_token=; path=/; max-age=0; SameSite=Lax";
        router.push("/login");
    };
    const [section, page] = BREADCRUMBS[pathname] ?? [
        "",
        "Nexus"
    ];
    const initials = user?.full_name ? user.full_name.split(" ").map((n)=>n[0]).join("").slice(0, 2).toUpperCase() : user?.username?.slice(0, 2).toUpperCase() ?? "NX";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("header", {
        style: {
            height: "var(--topnav-height)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 24px",
            borderBottom: "1px solid var(--color-border)",
            background: "var(--color-bg)",
            position: "sticky",
            top: 0,
            zIndex: 50,
            flexShrink: 0
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    minWidth: 0
                },
                children: [
                    section && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontSize: 12,
                                    color: "var(--color-text-3)",
                                    whiteSpace: "nowrap"
                                },
                                children: section
                            }, void 0, false, {
                                fileName: "[project]/app/components/TopNav.tsx",
                                lineNumber: 68,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontSize: 12,
                                    color: "var(--color-border-hi)"
                                },
                                children: "/"
                            }, void 0, false, {
                                fileName: "[project]/app/components/TopNav.tsx",
                                lineNumber: 71,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            fontSize: 12,
                            color: "var(--color-text-2)",
                            fontWeight: 500,
                            whiteSpace: "nowrap"
                        },
                        children: page
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 74,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/TopNav.tsx",
                lineNumber: 65,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                tabIndex: 0,
                role: "button",
                "aria-label": "Search (⌘K)",
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "6px 12px",
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--color-text-3)",
                    fontSize: 12,
                    cursor: "pointer",
                    minWidth: 220,
                    maxWidth: 320,
                    transition: `border-color 120ms ${T}`
                },
                onMouseEnter: (e)=>e.currentTarget.style.borderColor = "var(--color-border-hi)",
                onMouseLeave: (e)=>e.currentTarget.style.borderColor = "var(--color-border)",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Search$3e$__["Search"], {
                        size: 13
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 102,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            flex: 1
                        },
                        children: "Search…"
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 103,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("kbd", {
                        style: {
                            fontSize: 10,
                            fontFamily: "var(--font-mono)",
                            padding: "1px 5px",
                            background: "var(--color-surface-2)",
                            borderRadius: 3,
                            color: "var(--color-text-3)"
                        },
                        children: "⌘K"
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 104,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/TopNav.tsx",
                lineNumber: 80,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 4
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        "aria-label": "Notifications",
                        style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 32,
                            height: 32,
                            borderRadius: "var(--radius-sm)",
                            border: "none",
                            background: "transparent",
                            color: "var(--color-text-2)",
                            cursor: "pointer",
                            position: "relative",
                            transition: `background 120ms ${T}, color 120ms ${T}`
                        },
                        onMouseEnter: (e)=>{
                            e.currentTarget.style.background = "var(--color-surface-2)";
                            e.currentTarget.style.color = "var(--color-text-1)";
                        },
                        onMouseLeave: (e)=>{
                            e.currentTarget.style.background = "transparent";
                            e.currentTarget.style.color = "var(--color-text-2)";
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bell$3e$__["Bell"], {
                                size: 15
                            }, void 0, false, {
                                fileName: "[project]/app/components/TopNav.tsx",
                                lineNumber: 146,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    position: "absolute",
                                    top: 6,
                                    right: 6,
                                    width: 5,
                                    height: 5,
                                    borderRadius: "50%",
                                    background: "var(--color-danger)",
                                    border: "1px solid var(--color-bg)"
                                }
                            }, void 0, false, {
                                fileName: "[project]/app/components/TopNav.tsx",
                                lineNumber: 148,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 121,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: handleLogout,
                        "aria-label": "Log out",
                        style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 32,
                            height: 32,
                            borderRadius: "var(--radius-sm)",
                            border: "none",
                            background: "transparent",
                            color: "var(--color-text-2)",
                            cursor: "pointer",
                            transition: `background 120ms ${T}, color 120ms ${T}`
                        },
                        onMouseEnter: (e)=>{
                            e.currentTarget.style.background = "var(--color-surface-2)";
                            e.currentTarget.style.color = "var(--color-text-1)";
                        },
                        onMouseLeave: (e)=>{
                            e.currentTarget.style.background = "transparent";
                            e.currentTarget.style.color = "var(--color-text-2)";
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$log$2d$out$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__LogOut$3e$__["LogOut"], {
                            size: 15
                        }, void 0, false, {
                            fileName: "[project]/app/components/TopNav.tsx",
                            lineNumber: 188,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 163,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            width: 1,
                            height: 20,
                            background: "var(--color-border)",
                            margin: "0 4px"
                        }
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 192,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        title: user?.email ?? "Account",
                        style: {
                            width: 28,
                            height: 28,
                            borderRadius: "var(--radius-full)",
                            background: "var(--color-surface-2)",
                            border: "1px solid var(--color-border-hi)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 11,
                            fontWeight: 600,
                            color: "var(--color-text-1)",
                            cursor: "pointer",
                            flexShrink: 0,
                            transition: `border-color 120ms ${T}`
                        },
                        onMouseEnter: (e)=>e.currentTarget.style.borderColor = "var(--color-accent)",
                        onMouseLeave: (e)=>e.currentTarget.style.borderColor = "var(--color-border-hi)",
                        children: initials
                    }, void 0, false, {
                        fileName: "[project]/app/components/TopNav.tsx",
                        lineNumber: 202,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/TopNav.tsx",
                lineNumber: 119,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/TopNav.tsx",
        lineNumber: 49,
        columnNumber: 5
    }, this);
}
_s(TopNav, "uurm+gofQzvdIBYM5J9qmGbcDIg=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["usePathname"]
    ];
});
_c = TopNav;
var _c;
__turbopack_context__.k.register(_c, "TopNav");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/api.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "API_BASE",
    ()=>API_BASE,
    "apiFetch",
    ()=>apiFetch,
    "apiFetchJSON",
    ()=>apiFetchJSON,
    "apiFetchSafe",
    ()=>apiFetchSafe,
    "apiPostJSON",
    ()=>apiPostJSON
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
/**
 * Centralized API Client for NEXUS
 * - Attaches auth token to every request
 * - Validates res.ok before parsing
 * - Single source of truth for API base URL
 */ const API_BASE = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
;
async function apiFetch(path, options = {}) {
    let token = null;
    if ("TURBOPACK compile-time truthy", 1) {
        token = localStorage.getItem("nexus_token");
    }
    const headers = new Headers(options.headers || {});
    if (token && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
    }
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers
    });
    return res;
}
async function apiFetchJSON(path, options = {}) {
    const res = await apiFetch(path, options);
    if (!res.ok) {
        throw new Error(`API ${res.status}: ${res.statusText}`);
    }
    return res.json();
}
async function apiPostJSON(path, body, options = {}) {
    const res = await apiFetch(path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...options.headers || {}
        },
        body: JSON.stringify(body),
        ...options
    });
    if (!res.ok) {
        throw new Error(`API ${res.status}: ${res.statusText}`);
    }
    return res.json();
}
async function apiFetchSafe(path) {
    try {
        const r = await apiFetch(path);
        return r.ok ? await r.json() : null;
    } catch  {
        return null;
    }
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/hooks/useApi.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "invalidateApi",
    ()=>invalidateApi,
    "useApi",
    ()=>useApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
;
// Module-level singletons for cache and deduplication
const cache = new Map();
const inflight = new Map();
const listeners = new Map();
function invalidateApi(endpoint) {
    if (endpoint) {
        cache.delete(endpoint);
        listeners.get(endpoint)?.forEach((fn)=>fn());
    } else {
        cache.clear();
        listeners.forEach((set)=>set.forEach((fn)=>fn()));
    }
}
function useApi(path, options = {}) {
    _s();
    const { ttl = 30000, fallback, enabled = true, timeout = 8000 } = options;
    const [data, setData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "useApi.useState": ()=>{
            // Synchronous cache hit on initial render
            if (enabled && cache.has(path)) {
                const entry = cache.get(path);
                if (Date.now() - entry.timestamp < ttl) {
                    return entry.data;
                }
            }
            return fallback ?? null;
        }
    }["useApi.useState"]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(!cache.has(path) && enabled);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const fetchRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const fetchData = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useApi.useCallback[fetchData]": async (ignoreCache = false)=>{
            if (!enabled) return;
            // Check cache
            if (!ignoreCache && cache.has(path)) {
                const entry = cache.get(path);
                if (Date.now() - entry.timestamp < ttl) {
                    setData(entry.data);
                    setError(null);
                    setLoading(false);
                    return;
                }
            }
            const currentFetch = ++fetchRef.current;
            setLoading(true);
            setError(null);
            try {
                // Deduplication: if another component is fetching this, wait for it
                let reqPromise = inflight.get(path);
                if (!reqPromise) {
                    const controller = new AbortController();
                    const timeoutId = setTimeout({
                        "useApi.useCallback[fetchData].timeoutId": ()=>controller.abort()
                    }["useApi.useCallback[fetchData].timeoutId"], timeout);
                    reqPromise = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])(path, {
                        signal: controller.signal
                    }).finally({
                        "useApi.useCallback[fetchData]": ()=>{
                            clearTimeout(timeoutId);
                            inflight.delete(path); // Cleanup
                        }
                    }["useApi.useCallback[fetchData]"]).then({
                        "useApi.useCallback[fetchData]": async (res)=>{
                            if (!res.ok) {
                                const code = res.status >= 500 ? "server_5xx" : "client_4xx";
                                throw {
                                    code,
                                    message: res.statusText,
                                    status: res.status
                                };
                            }
                            try {
                                return await res.json();
                            } catch  {
                                throw {
                                    code: "parse",
                                    message: "Failed to parse JSON response"
                                };
                            }
                        }
                    }["useApi.useCallback[fetchData]"]).catch({
                        "useApi.useCallback[fetchData]": (err)=>{
                            if (err.name === "AbortError") {
                                throw {
                                    code: "timeout",
                                    message: "Request timed out"
                                };
                            }
                            if (err.code) throw err; // Already formatted
                            throw {
                                code: "network",
                                message: err.message || "Network error"
                            };
                        }
                    }["useApi.useCallback[fetchData]"]);
                    inflight.set(path, reqPromise);
                }
                const result = await reqPromise;
                // Only update state if this is still the most recent fetch call
                if (currentFetch === fetchRef.current) {
                    cache.set(path, {
                        data: result,
                        timestamp: Date.now()
                    });
                    setData(result);
                    setError(null);
                }
            } catch (err) {
                if (currentFetch === fetchRef.current) {
                    setError(err);
                    setData(fallback ?? null);
                }
            } finally{
                if (currentFetch === fetchRef.current) {
                    setLoading(false);
                }
            }
        }
    }["useApi.useCallback[fetchData]"], [
        path,
        ttl,
        fallback,
        enabled,
        timeout
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useApi.useEffect": ()=>{
            fetchData();
            // Setup listener for manual invalidation
            const listener = {
                "useApi.useEffect.listener": ()=>fetchData(true)
            }["useApi.useEffect.listener"];
            let set = listeners.get(path);
            if (!set) {
                set = new Set();
                listeners.set(path, set);
            }
            set.add(listener);
            return ({
                "useApi.useEffect": ()=>{
                    set?.delete(listener);
                    if (set?.size === 0) listeners.delete(path);
                }
            })["useApi.useEffect"];
        }
    }["useApi.useEffect"], [
        fetchData,
        path
    ]);
    const retry = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useApi.useCallback[retry]": ()=>fetchData(true)
    }["useApi.useCallback[retry]"], [
        fetchData
    ]);
    return {
        data,
        loading,
        error,
        retry
    };
}
_s(useApi, "xWPGf7v3MSjtoFbbCrF7FJXoopQ=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/components/Cards/KpiCard.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "KpiCard",
    ()=>KpiCard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
"use client";
;
function KpiCard({ label, value, delta, deltaDir, sub }) {
    const dotColor = deltaDir === "up" ? "#22C55E" : deltaDir === "down" ? "#FF4444" : "#F59E0B";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            padding: 20,
            transition: "border-color 120ms cubic-bezier(0.16,1,0.3,1)"
        },
        onMouseEnter: (e)=>e.currentTarget.style.borderColor = "var(--color-border-hi)",
        onMouseLeave: (e)=>e.currentTarget.style.borderColor = "var(--color-border)",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    fontSize: 11,
                    fontWeight: 500,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "var(--color-text-2)",
                    marginBottom: 8
                },
                children: label
            }, void 0, false, {
                fileName: "[project]/app/components/Cards/KpiCard.tsx",
                lineNumber: 33,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    fontSize: 32,
                    fontWeight: 700,
                    color: "var(--color-text-1)",
                    lineHeight: 1.1,
                    letterSpacing: "-0.02em"
                },
                children: value
            }, void 0, false, {
                fileName: "[project]/app/components/Cards/KpiCard.tsx",
                lineNumber: 45,
                columnNumber: 7
            }, this),
            delta && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 4,
                    marginTop: 8,
                    fontSize: 11,
                    fontWeight: 500,
                    color: dotColor
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            width: 6,
                            height: 6,
                            borderRadius: "50%",
                            background: dotColor,
                            flexShrink: 0
                        }
                    }, void 0, false, {
                        fileName: "[project]/app/components/Cards/KpiCard.tsx",
                        lineNumber: 68,
                        columnNumber: 11
                    }, this),
                    delta
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/Cards/KpiCard.tsx",
                lineNumber: 57,
                columnNumber: 9
            }, this),
            sub && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    marginTop: 8,
                    fontSize: 11,
                    color: "var(--color-text-3)"
                },
                children: sub
            }, void 0, false, {
                fileName: "[project]/app/components/Cards/KpiCard.tsx",
                lineNumber: 81,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/Cards/KpiCard.tsx",
        lineNumber: 22,
        columnNumber: 5
    }, this);
}
_c = KpiCard;
var _c;
__turbopack_context__.k.register(_c, "KpiCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/upload/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>UploadPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/Sidebar.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/TopNav.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useApi$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/useApi.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Cards$2f$KpiCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/Cards/KpiCard.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
;
const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";
function UploadPage() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [file, setFile] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [dragOver, setDragOver] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [analyzing, setAnalyzing] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [progress, setProgress] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const [result, setResult] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [preview, setPreview] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const handleFile = async (f)=>{
        setFile(f);
        setResult(null);
        setPreview(null);
        const formData = new FormData();
        formData.append("file", f);
        try {
            const res = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])("/upload/preview", {
                method: "POST",
                body: formData
            });
            if (res.ok) setPreview(await res.json());
        } catch  {}
    };
    const handleDrop = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "UploadPage.useCallback[handleDrop]": (e)=>{
            e.preventDefault();
            setDragOver(false);
            const f = e.dataTransfer.files[0];
            if (f) handleFile(f);
        }
    }["UploadPage.useCallback[handleDrop]"], []);
    const pollStatus = ()=>{
        const interval = setInterval(async ()=>{
            try {
                const res = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])("/system/health");
                const data = await res.json();
                if (!data.is_analyzing) {
                    clearInterval(interval);
                    setAnalyzing(false);
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useApi$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["invalidateApi"])();
                    setProgress(100);
                    setTimeout(()=>router.push("/dashboard"), 1200);
                } else {
                    setProgress((p)=>Math.min(p + 5, 94));
                }
            } catch  {}
        }, 2000);
    };
    const handleUpload = async ()=>{
        if (!file) return;
        setLoading(true);
        setProgress(15);
        const formData = new FormData();
        formData.append("file", file);
        try {
            const res = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])("/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (res.status === 422 && data.detail?.error === "ambiguous_column_mapping") {
                setLoading(false);
                router.push("/upload/map");
                return;
            }
            setResult(data);
            if (data.status === "success") {
                setLoading(false);
                setAnalyzing(true);
                setProgress(40);
                pollStatus();
            } else {
                setResult({
                    status: "error",
                    message: data.detail || "Upload failed."
                });
                setLoading(false);
            }
        } catch  {
            setResult({
                status: "error",
                message: "Upload failed. Check backend connectivity."
            });
            setLoading(false);
        }
    };
    const isActive = !loading && !result;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "app-layout",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                fileName: "[project]/app/upload/page.tsx",
                lineNumber: 102,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "main-wrapper",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                        fileName: "[project]/app/upload/page.tsx",
                        lineNumber: 104,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                        className: "main-content",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "flex-start",
                                    justifyContent: "space-between",
                                    paddingBottom: 16,
                                    marginBottom: 24,
                                    borderBottom: "1px solid var(--color-border)"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 11,
                                                    color: "var(--color-text-3)",
                                                    marginBottom: 4
                                                },
                                                children: "Overview"
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 113,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                                style: {
                                                    fontSize: 22,
                                                    fontWeight: 600,
                                                    color: "var(--color-text-1)",
                                                    lineHeight: 1.2
                                                },
                                                children: "Upload Data"
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 114,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                style: {
                                                    fontSize: 13,
                                                    color: "var(--color-text-2)",
                                                    marginTop: 2
                                                },
                                                children: "Ingest CSV or Excel files. Columns are auto-detected and mapped to the canonical schema."
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 117,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 112,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        onClick: ()=>router.push("/dashboard"),
                                        style: {
                                            display: "inline-flex",
                                            alignItems: "center",
                                            padding: "8px 16px",
                                            borderRadius: 4,
                                            fontSize: 13,
                                            fontWeight: 600,
                                            fontFamily: "var(--font-sans)",
                                            background: "transparent",
                                            border: "1px solid var(--color-border-hi)",
                                            color: "var(--color-text-1)",
                                            cursor: "pointer",
                                            flexShrink: 0,
                                            transition: `background 120ms ${EASE}`
                                        },
                                        onMouseEnter: (e)=>e.currentTarget.style.background = "var(--color-surface-2)",
                                        onMouseLeave: (e)=>e.currentTarget.style.background = "transparent",
                                        children: "View Dashboard"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 121,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/upload/page.tsx",
                                lineNumber: 108,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "grid",
                                    gridTemplateColumns: "repeat(4, 1fr)",
                                    gap: 16,
                                    marginBottom: 32
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Cards$2f$KpiCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["KpiCard"], {
                                        label: "Supported Formats",
                                        value: "3",
                                        sub: "CSV · XLSX · XLS"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 139,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Cards$2f$KpiCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["KpiCard"], {
                                        label: "Row Limit",
                                        value: "1M+",
                                        sub: "Auto-chunked for large files"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 140,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Cards$2f$KpiCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["KpiCard"], {
                                        label: "Auto-Mapping",
                                        value: "Active",
                                        sub: "Synonym-based column detection"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 141,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Cards$2f$KpiCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["KpiCard"], {
                                        label: "File Selected",
                                        value: file ? "1" : "—",
                                        sub: file ? `${(file.size / 1024).toFixed(1)} KB · ${file.name}` : "No file chosen"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 142,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/upload/page.tsx",
                                lineNumber: 138,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    maxWidth: 720
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                        htmlFor: "file-input",
                                        id: "upload-dropzone",
                                        className: "upload-dropzone",
                                        onDragOver: (e)=>{
                                            e.preventDefault();
                                            setDragOver(true);
                                        },
                                        onDragLeave: ()=>setDragOver(false),
                                        onDrop: handleDrop,
                                        style: {
                                            display: "block",
                                            borderColor: dragOver ? "var(--color-accent)" : file ? "var(--color-border-hi)" : "var(--color-border)",
                                            borderWidth: 1,
                                            borderStyle: "dashed",
                                            borderRadius: 6,
                                            padding: 40,
                                            textAlign: "center",
                                            cursor: "pointer",
                                            background: dragOver ? "rgba(232,255,71,0.04)" : "var(--color-surface)",
                                            transition: `border-color 120ms ${EASE}, background 120ms ${EASE}`,
                                            position: "relative"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                id: "file-input",
                                                className: "file-input",
                                                type: "file",
                                                accept: ".csv,.xlsx,.xls",
                                                "aria-label": "Upload data file",
                                                "aria-describedby": "upload-instructions",
                                                style: {
                                                    opacity: 0,
                                                    width: "0.1px",
                                                    height: "0.1px",
                                                    position: "absolute",
                                                    zIndex: -1
                                                },
                                                onChange: (e)=>{
                                                    const f = e.target.files?.[0];
                                                    if (f) handleFile(f);
                                                }
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 174,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "upload-dropzone-content",
                                                children: file ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 13,
                                                                fontWeight: 500,
                                                                color: "var(--color-text-1)",
                                                                marginBottom: 4
                                                            },
                                                            children: file.name
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 194,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 12,
                                                                color: "var(--color-text-3)"
                                                            },
                                                            children: [
                                                                (file.size / 1024).toFixed(1),
                                                                " KB · Click to replace"
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 197,
                                                            columnNumber: 21
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/upload/page.tsx",
                                                    lineNumber: 193,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    id: "upload-instructions",
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 15,
                                                                fontWeight: 400,
                                                                color: "var(--color-text-2)",
                                                                marginBottom: 4
                                                            },
                                                            children: "Drag & drop your file here, or click to browse"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 203,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 12,
                                                                color: "var(--color-text-3)"
                                                            },
                                                            children: "Supports .csv, .xlsx, .xls — up to 1M+ rows"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 206,
                                                            columnNumber: 21
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/upload/page.tsx",
                                                    lineNumber: 202,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 191,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 153,
                                        columnNumber: 13
                                    }, this),
                                    preview && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 16,
                                            background: "var(--color-surface)",
                                            border: "1px solid var(--color-border)",
                                            borderRadius: 6,
                                            overflow: "hidden"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    padding: "12px 16px",
                                                    borderBottom: "1px solid var(--color-border)",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    justifyContent: "space-between"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            fontSize: 11,
                                                            fontWeight: 500,
                                                            textTransform: "uppercase",
                                                            letterSpacing: "0.05em",
                                                            color: "var(--color-text-2)"
                                                        },
                                                        children: "Auto-Detected Column Mapping"
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/upload/page.tsx",
                                                        lineNumber: 224,
                                                        columnNumber: 19
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            fontSize: 11,
                                                            color: "var(--color-text-3)"
                                                        },
                                                        children: [
                                                            Object.keys(preview.auto_mapping ?? {}).length,
                                                            " columns mapped"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/app/upload/page.tsx",
                                                        lineNumber: 227,
                                                        columnNumber: 19
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 220,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    padding: "12px 16px",
                                                    display: "flex",
                                                    flexWrap: "wrap",
                                                    gap: 6,
                                                    borderBottom: "1px solid var(--color-border)"
                                                },
                                                children: Object.entries(preview.auto_mapping ?? {}).map(([target, source])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            background: "rgba(232,255,71,0.06)",
                                                            border: "1px solid rgba(232,255,71,0.18)",
                                                            borderRadius: 999,
                                                            padding: "2px 10px",
                                                            fontSize: 11,
                                                            fontWeight: 500,
                                                            color: "var(--color-accent)"
                                                        },
                                                        children: [
                                                            source?.mapped_to ?? source,
                                                            " → ",
                                                            target
                                                        ]
                                                    }, target, true, {
                                                        fileName: "[project]/app/upload/page.tsx",
                                                        lineNumber: 235,
                                                        columnNumber: 21
                                                    }, this))
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 233,
                                                columnNumber: 17
                                            }, this),
                                            preview.preview_rows?.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    overflowX: "auto"
                                                },
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                                                    style: {
                                                        width: "100%",
                                                        borderCollapse: "collapse",
                                                        fontSize: 12
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                children: preview.columns?.slice(0, 7).map((c)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                                        style: {
                                                                            textAlign: "left",
                                                                            padding: "8px 12px",
                                                                            fontSize: 11,
                                                                            fontWeight: 500,
                                                                            textTransform: "uppercase",
                                                                            letterSpacing: "0.05em",
                                                                            color: "var(--color-text-3)",
                                                                            borderBottom: "1px solid var(--color-border)",
                                                                            background: "var(--color-surface)"
                                                                        },
                                                                        children: c
                                                                    }, c, false, {
                                                                        fileName: "[project]/app/upload/page.tsx",
                                                                        lineNumber: 259,
                                                                        columnNumber: 29
                                                                    }, this))
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/upload/page.tsx",
                                                                lineNumber: 257,
                                                                columnNumber: 25
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 256,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                                            children: preview.preview_rows.slice(0, 4).map((row, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                    children: preview.columns?.slice(0, 7).map((c)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                            style: {
                                                                                padding: "8px 12px",
                                                                                height: 36,
                                                                                borderBottom: "1px solid var(--color-border)",
                                                                                color: "var(--color-text-2)",
                                                                                fontSize: 12,
                                                                                verticalAlign: "middle",
                                                                                maxWidth: 160,
                                                                                overflow: "hidden",
                                                                                textOverflow: "ellipsis",
                                                                                whiteSpace: "nowrap"
                                                                            },
                                                                            children: String(row[c] ?? "—")
                                                                        }, c, false, {
                                                                            fileName: "[project]/app/upload/page.tsx",
                                                                            lineNumber: 276,
                                                                            columnNumber: 31
                                                                        }, this))
                                                                }, i, false, {
                                                                    fileName: "[project]/app/upload/page.tsx",
                                                                    lineNumber: 274,
                                                                    columnNumber: 27
                                                                }, this))
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 272,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/app/upload/page.tsx",
                                                    lineNumber: 255,
                                                    columnNumber: 21
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 254,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 216,
                                        columnNumber: 15
                                    }, this),
                                    (loading || analyzing) && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 16
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    height: 4,
                                                    borderRadius: 999,
                                                    background: "var(--color-surface-2)",
                                                    overflow: "hidden"
                                                },
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        width: `${progress}%`,
                                                        height: "100%",
                                                        borderRadius: 999,
                                                        background: "var(--color-accent)",
                                                        transition: "width 400ms cubic-bezier(0.16,1,0.3,1)"
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/app/upload/page.tsx",
                                                    lineNumber: 299,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 298,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    marginTop: 8,
                                                    fontSize: 12,
                                                    color: "var(--color-text-3)"
                                                },
                                                children: analyzing ? `Running analysis pipeline... ${progress}%` : `Uploading and validating... ${progress}%`
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 305,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 297,
                                        columnNumber: 15
                                    }, this),
                                    result && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 16,
                                            background: "var(--color-surface)",
                                            border: `1px solid var(--color-border)`,
                                            borderLeft: `4px solid ${result.status === "success" ? "#22C55E" : "#FF4444"}`,
                                            borderRadius: 6,
                                            padding: 16
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontWeight: 600,
                                                    fontSize: 14,
                                                    color: "var(--color-text-1)",
                                                    marginBottom: 4
                                                },
                                                children: result.status === "success" ? `${result.rows_inserted?.toLocaleString()} rows imported successfully` : "Upload failed"
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 323,
                                                columnNumber: 17
                                            }, this),
                                            result.message && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 12,
                                                    color: "var(--color-text-2)",
                                                    marginTop: 4
                                                },
                                                children: typeof result.message === "string" ? result.message : JSON.stringify(result.message)
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 329,
                                                columnNumber: 19
                                            }, this),
                                            (result.rows_rejected ?? 0) > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 12,
                                                    color: "var(--color-text-3)",
                                                    marginTop: 4
                                                },
                                                children: [
                                                    result.rows_rejected,
                                                    " rows skipped — invalid or missing required fields"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 334,
                                                columnNumber: 19
                                            }, this),
                                            result.status === "success" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 12,
                                                    color: "#22C55E",
                                                    marginTop: 8
                                                },
                                                children: "Redirecting to dashboard…"
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 339,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 315,
                                        columnNumber: 15
                                    }, this),
                                    file && isActive && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        id: "upload-submit-btn",
                                        onClick: handleUpload,
                                        style: {
                                            marginTop: 20,
                                            width: "100%",
                                            background: "var(--color-accent)",
                                            color: "#0A0A0A",
                                            border: "none",
                                            borderRadius: 4,
                                            padding: "10px 16px",
                                            fontWeight: 600,
                                            fontSize: 13,
                                            fontFamily: "var(--font-sans)",
                                            cursor: "pointer",
                                            transition: `opacity 120ms ${EASE}`
                                        },
                                        onMouseEnter: (e)=>e.currentTarget.style.opacity = "0.88",
                                        onMouseLeave: (e)=>e.currentTarget.style.opacity = "1",
                                        children: "Upload & Analyze"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 348,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 24,
                                            padding: "14px 16px",
                                            border: "1px solid var(--color-border)",
                                            borderRadius: 6
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 11,
                                                    fontWeight: 500,
                                                    textTransform: "uppercase",
                                                    letterSpacing: "0.05em",
                                                    color: "var(--color-text-3)",
                                                    marginBottom: 12
                                                },
                                                children: "Expected Column Schema"
                                            }, void 0, false, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 377,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                                                style: {
                                                    width: "100%",
                                                    borderCollapse: "collapse",
                                                    fontSize: 12
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                            children: [
                                                                "Column",
                                                                "Type",
                                                                "Required",
                                                                "Description"
                                                            ].map((h)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                                    style: {
                                                                        textAlign: "left",
                                                                        padding: "6px 8px",
                                                                        fontSize: 11,
                                                                        fontWeight: 500,
                                                                        textTransform: "uppercase",
                                                                        letterSpacing: "0.05em",
                                                                        color: "var(--color-text-3)",
                                                                        borderBottom: "1px solid var(--color-border)"
                                                                    },
                                                                    children: h
                                                                }, h, false, {
                                                                    fileName: "[project]/app/upload/page.tsx",
                                                                    lineNumber: 384,
                                                                    columnNumber: 23
                                                                }, this))
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/upload/page.tsx",
                                                            lineNumber: 382,
                                                            columnNumber: 19
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/upload/page.tsx",
                                                        lineNumber: 381,
                                                        columnNumber: 17
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                                        children: [
                                                            [
                                                                "supplier_id",
                                                                "string",
                                                                "Yes",
                                                                "Unique supplier identifier"
                                                            ],
                                                            [
                                                                "shipment_date",
                                                                "date",
                                                                "Yes",
                                                                "ISO 8601 or YYYY-MM-DD"
                                                            ],
                                                            [
                                                                "delay_days",
                                                                "number",
                                                                "Yes",
                                                                "Integer days late (0 = on time)"
                                                            ],
                                                            [
                                                                "cost",
                                                                "number",
                                                                "Yes",
                                                                "Shipment cost in local currency"
                                                            ],
                                                            [
                                                                "sku",
                                                                "string",
                                                                "No",
                                                                "Product SKU"
                                                            ],
                                                            [
                                                                "region",
                                                                "string",
                                                                "No",
                                                                "Geographic region"
                                                            ],
                                                            [
                                                                "warehouse_id",
                                                                "string",
                                                                "No",
                                                                "Destination warehouse"
                                                            ],
                                                            [
                                                                "quality_score",
                                                                "number",
                                                                "No",
                                                                "0.0–1.0 quality rating"
                                                            ]
                                                        ].map(([col, type, req, desc])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                style: {
                                                                    transition: `background 120ms ${EASE}`
                                                                },
                                                                onMouseEnter: (e)=>e.currentTarget.style.background = "var(--color-surface-2)",
                                                                onMouseLeave: (e)=>e.currentTarget.style.background = "transparent",
                                                                children: [
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                        style: {
                                                                            padding: "8px 8px",
                                                                            height: 36,
                                                                            color: "var(--color-text-1)",
                                                                            fontWeight: 500,
                                                                            borderBottom: "1px solid var(--color-border)",
                                                                            verticalAlign: "middle"
                                                                        },
                                                                        children: col
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/upload/page.tsx",
                                                                        lineNumber: 412,
                                                                        columnNumber: 23
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                        style: {
                                                                            padding: "8px 8px",
                                                                            height: 36,
                                                                            color: "var(--color-text-3)",
                                                                            borderBottom: "1px solid var(--color-border)",
                                                                            verticalAlign: "middle"
                                                                        },
                                                                        children: type
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/upload/page.tsx",
                                                                        lineNumber: 413,
                                                                        columnNumber: 23
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                        style: {
                                                                            padding: "8px 8px",
                                                                            height: 36,
                                                                            borderBottom: "1px solid var(--color-border)",
                                                                            verticalAlign: "middle"
                                                                        },
                                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                            style: {
                                                                                padding: "1px 6px",
                                                                                borderRadius: 999,
                                                                                fontSize: 10,
                                                                                fontWeight: 500,
                                                                                background: req === "Yes" ? "rgba(232,255,71,0.08)" : "transparent",
                                                                                color: req === "Yes" ? "var(--color-accent)" : "var(--color-text-3)",
                                                                                border: req === "Yes" ? "1px solid rgba(232,255,71,0.2)" : "1px solid var(--color-border)"
                                                                            },
                                                                            children: req
                                                                        }, void 0, false, {
                                                                            fileName: "[project]/app/upload/page.tsx",
                                                                            lineNumber: 415,
                                                                            columnNumber: 25
                                                                        }, this)
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/upload/page.tsx",
                                                                        lineNumber: 414,
                                                                        columnNumber: 23
                                                                    }, this),
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                        style: {
                                                                            padding: "8px 8px",
                                                                            height: 36,
                                                                            color: "var(--color-text-2)",
                                                                            borderBottom: "1px solid var(--color-border)",
                                                                            verticalAlign: "middle"
                                                                        },
                                                                        children: desc
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/app/upload/page.tsx",
                                                                        lineNumber: 424,
                                                                        columnNumber: 23
                                                                    }, this)
                                                                ]
                                                            }, col, true, {
                                                                fileName: "[project]/app/upload/page.tsx",
                                                                lineNumber: 407,
                                                                columnNumber: 21
                                                            }, this))
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/upload/page.tsx",
                                                        lineNumber: 396,
                                                        columnNumber: 17
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/upload/page.tsx",
                                                lineNumber: 380,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/upload/page.tsx",
                                        lineNumber: 373,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/upload/page.tsx",
                                lineNumber: 150,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/upload/page.tsx",
                        lineNumber: 105,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/upload/page.tsx",
                lineNumber: 103,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/upload/page.tsx",
        lineNumber: 101,
        columnNumber: 5
    }, this);
}
_s(UploadPage, "Mk0DvBbOB7/IB1QZTmR2JRF5mM0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = UploadPage;
var _c;
__turbopack_context__.k.register(_c, "UploadPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_4f210aee._.js.map