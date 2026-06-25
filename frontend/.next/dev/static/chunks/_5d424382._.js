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
"[project]/app/components/Charts.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "SynAreaChart",
    ()=>SynAreaChart,
    "SynBarChart",
    ()=>SynBarChart,
    "SynLineChart",
    ()=>SynLineChart,
    "SynPieChart",
    ()=>SynPieChart
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$BarChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/chart/BarChart.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Bar$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/Bar.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$LineChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/chart/LineChart.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Line$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/Line.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$PieChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/chart/PieChart.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$polar$2f$Pie$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/polar/Pie.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Cell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/component/Cell.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$AreaChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/chart/AreaChart.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Area$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/Area.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/XAxis.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/YAxis.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/cartesian/CartesianGrid.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/component/Tooltip.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/component/ResponsiveContainer.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Legend$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/recharts/es6/component/Legend.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
/* ── Palette-only colour sequence for data series ── */ const COLORS = [
    "#E8FF47",
    /* accent */ "#FF4444",
    /* danger */ "#F59E0B",
    /* warn   */ "#22C55E",
    /* ok     */ "#F5F5F5",
    /* text-1 */ "#888888"
];
const tooltipStyle = {
    backgroundColor: "#111111",
    border: "1px solid #222222",
    borderRadius: "6px",
    color: "#F5F5F5",
    fontSize: "12px",
    boxShadow: "none"
};
const AXIS_TICK = {
    fill: "#555555",
    fontSize: 11
};
const AXIS_LINE = {
    stroke: "#1A1A1A"
};
const GRID_STROKE = "#1A1A1A";
function SynBarChart({ data, dataKey, nameKey = "name", color = "#E8FF47", height = 300 }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
        width: "100%",
        height: height,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$BarChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BarChart"], {
            data: data,
            margin: {
                top: 4,
                right: 16,
                bottom: 4,
                left: 0
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                    strokeDasharray: "0",
                    stroke: GRID_STROKE,
                    vertical: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 65,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["XAxis"], {
                    dataKey: nameKey,
                    tick: AXIS_TICK,
                    axisLine: AXIS_LINE,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 66,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["YAxis"], {
                    tick: AXIS_TICK,
                    axisLine: false,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 67,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Tooltip"], {
                    contentStyle: tooltipStyle,
                    cursor: {
                        fill: "#1A1A1A"
                    }
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 68,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Bar$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Bar"], {
                    dataKey: dataKey,
                    fill: color,
                    radius: [
                        2,
                        2,
                        0,
                        0
                    ]
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 69,
                    columnNumber: 17
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/components/Charts.tsx",
            lineNumber: 64,
            columnNumber: 13
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/components/Charts.tsx",
        lineNumber: 63,
        columnNumber: 9
    }, this);
}
_c = SynBarChart;
function SynLineChart({ data, lines, xKey = "name", height = 300 }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
        width: "100%",
        height: height,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$LineChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineChart"], {
            data: data,
            margin: {
                top: 4,
                right: 16,
                bottom: 4,
                left: 0
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                    strokeDasharray: "0",
                    stroke: GRID_STROKE,
                    vertical: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 92,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["XAxis"], {
                    dataKey: xKey,
                    tick: AXIS_TICK,
                    axisLine: AXIS_LINE,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 93,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["YAxis"], {
                    tick: AXIS_TICK,
                    axisLine: false,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 94,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Tooltip"], {
                    contentStyle: tooltipStyle
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 95,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Legend$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Legend"], {
                    wrapperStyle: {
                        fontSize: 11,
                        color: "#888888"
                    }
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 96,
                    columnNumber: 17
                }, this),
                lines.map((line, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Line$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Line"], {
                        type: "monotone",
                        dataKey: line.key,
                        stroke: line.color || COLORS[i % COLORS.length],
                        strokeWidth: 2,
                        dot: {
                            r: 2,
                            fill: line.color || COLORS[i % COLORS.length]
                        },
                        activeDot: {
                            r: 3
                        },
                        name: line.name || line.key
                    }, line.key, false, {
                        fileName: "[project]/app/components/Charts.tsx",
                        lineNumber: 98,
                        columnNumber: 21
                    }, this))
            ]
        }, void 0, true, {
            fileName: "[project]/app/components/Charts.tsx",
            lineNumber: 91,
            columnNumber: 13
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/components/Charts.tsx",
        lineNumber: 90,
        columnNumber: 9
    }, this);
}
_c1 = SynLineChart;
function SynAreaChart({ data, dataKey, xKey = "name", color = "#E8FF47", height = 300 }) {
    const gradId = `grad-${dataKey}-${color.replace("#", "")}`;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
        width: "100%",
        height: height,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$AreaChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AreaChart"], {
            data: data,
            margin: {
                top: 4,
                right: 16,
                bottom: 4,
                left: 0
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("defs", {
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("linearGradient", {
                        id: gradId,
                        x1: "0",
                        y1: "0",
                        x2: "0",
                        y2: "1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("stop", {
                                offset: "0%",
                                stopColor: color,
                                stopOpacity: 0.12
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 136,
                                columnNumber: 25
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("stop", {
                                offset: "100%",
                                stopColor: color,
                                stopOpacity: 0
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 137,
                                columnNumber: 25
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/components/Charts.tsx",
                        lineNumber: 135,
                        columnNumber: 21
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 134,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$CartesianGrid$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CartesianGrid"], {
                    strokeDasharray: "0",
                    stroke: GRID_STROKE,
                    vertical: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 140,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$XAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["XAxis"], {
                    dataKey: xKey,
                    tick: AXIS_TICK,
                    axisLine: AXIS_LINE,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 141,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$YAxis$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["YAxis"], {
                    tick: AXIS_TICK,
                    axisLine: false,
                    tickLine: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 142,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Tooltip"], {
                    contentStyle: tooltipStyle
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 143,
                    columnNumber: 17
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$cartesian$2f$Area$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Area"], {
                    type: "monotone",
                    dataKey: dataKey,
                    stroke: color,
                    fill: `url(#${gradId})`,
                    strokeWidth: 2,
                    dot: false
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 144,
                    columnNumber: 17
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/components/Charts.tsx",
            lineNumber: 133,
            columnNumber: 13
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/components/Charts.tsx",
        lineNumber: 132,
        columnNumber: 9
    }, this);
}
_c2 = SynAreaChart;
/* ============================
   PIE CHART
   ============================ */ const MAX_SLICES = 6;
function CustomPieTooltip({ active, payload }) {
    if (!active || !payload?.length) return null;
    const d = payload[0];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            background: "#111111",
            border: "1px solid #222222",
            borderRadius: 6,
            padding: "8px 12px",
            fontSize: 12,
            color: "#F5F5F5"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    fontWeight: 600,
                    marginBottom: 4,
                    color: d.payload?.fill || "#E8FF47"
                },
                children: d.name
            }, void 0, false, {
                fileName: "[project]/app/components/Charts.tsx",
                lineNumber: 174,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    color: "#888888"
                },
                children: [
                    typeof d.value === "number" ? d.value.toLocaleString() : d.value,
                    d.payload?.percent != null && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            color: "#555555",
                            marginLeft: 6
                        },
                        children: [
                            "(",
                            (d.payload.percent * 100).toFixed(1),
                            "%)"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/components/Charts.tsx",
                        lineNumber: 180,
                        columnNumber: 21
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/Charts.tsx",
                lineNumber: 177,
                columnNumber: 13
            }, this),
            d.payload?._groupedItems && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    marginTop: 6,
                    paddingTop: 6,
                    borderTop: "1px solid #222222",
                    fontSize: 11,
                    color: "#555555"
                },
                children: [
                    "Includes: ",
                    d.payload._groupedItems.join(", ")
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/Charts.tsx",
                lineNumber: 186,
                columnNumber: 17
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/Charts.tsx",
        lineNumber: 166,
        columnNumber: 9
    }, this);
}
_c3 = CustomPieTooltip;
function SynPieChart({ data, dataKey, nameKey = "name", height = 300 }) {
    _s();
    const [hovered, setHovered] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const { chartData, colorMap } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "SynPieChart.useMemo": ()=>{
            if (!data || data.length === 0) return {
                chartData: [],
                colorMap: {}
            };
            const sorted = [
                ...data
            ].sort({
                "SynPieChart.useMemo.sorted": (a, b)=>(b[dataKey] || 0) - (a[dataKey] || 0)
            }["SynPieChart.useMemo.sorted"]);
            const cMap = {};
            if (sorted.length <= MAX_SLICES) {
                sorted.forEach({
                    "SynPieChart.useMemo": (d, i)=>{
                        cMap[d[nameKey]] = COLORS[i % COLORS.length];
                    }
                }["SynPieChart.useMemo"]);
                return {
                    chartData: sorted,
                    colorMap: cMap
                };
            }
            const topItems = sorted.slice(0, MAX_SLICES - 1);
            const remainingItems = sorted.slice(MAX_SLICES - 1);
            const otherValue = remainingItems.reduce({
                "SynPieChart.useMemo.otherValue": (sum, d)=>sum + (d[dataKey] || 0)
            }["SynPieChart.useMemo.otherValue"], 0);
            const otherNames = remainingItems.map({
                "SynPieChart.useMemo.otherNames": (d)=>d[nameKey]
            }["SynPieChart.useMemo.otherNames"]);
            topItems.forEach({
                "SynPieChart.useMemo": (d, i)=>{
                    cMap[d[nameKey]] = COLORS[i % COLORS.length];
                }
            }["SynPieChart.useMemo"]);
            cMap["Other"] = "#555555";
            const grouped = [
                ...topItems,
                {
                    [nameKey]: "Other",
                    [dataKey]: otherValue,
                    _groupedItems: otherNames
                }
            ];
            return {
                chartData: grouped,
                colorMap: cMap
            };
        }
    }["SynPieChart.useMemo"], [
        data,
        dataKey,
        nameKey
    ]);
    if (chartData.length === 0) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height,
                color: "#555555",
                fontSize: 13
            },
            children: "No data available"
        }, void 0, false, {
            fileName: "[project]/app/components/Charts.tsx",
            lineNumber: 236,
            columnNumber: 13
        }, this);
    }
    const total = chartData.reduce((sum, d)=>sum + (d[dataKey] || 0), 0);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            display: "flex",
            alignItems: "center",
            gap: 16,
            height
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    flex: "0 0 55%",
                    height: "100%"
                },
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$ResponsiveContainer$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ResponsiveContainer"], {
                    width: "100%",
                    height: "100%",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$chart$2f$PieChart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PieChart"], {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$polar$2f$Pie$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Pie"], {
                                data: chartData,
                                dataKey: dataKey,
                                nameKey: nameKey,
                                cx: "50%",
                                cy: "50%",
                                outerRadius: Math.min(height * 0.38, 110),
                                innerRadius: Math.min(height * 0.2, 55),
                                paddingAngle: 2,
                                label: false,
                                labelLine: false,
                                onMouseEnter: (_, index)=>setHovered(index),
                                onMouseLeave: ()=>setHovered(null),
                                stroke: "none",
                                children: chartData.map((entry, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Cell$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Cell"], {
                                        fill: colorMap[entry[nameKey]] || COLORS[i % COLORS.length],
                                        opacity: hovered === null || hovered === i ? 1 : 0.35,
                                        style: {
                                            transition: "opacity 120ms cubic-bezier(0.16,1,0.3,1)",
                                            cursor: "pointer"
                                        }
                                    }, i, false, {
                                        fileName: "[project]/app/components/Charts.tsx",
                                        lineNumber: 265,
                                        columnNumber: 33
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 249,
                                columnNumber: 25
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$recharts$2f$es6$2f$component$2f$Tooltip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Tooltip"], {
                                content: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(CustomPieTooltip, {}, void 0, false, {
                                    fileName: "[project]/app/components/Charts.tsx",
                                    lineNumber: 273,
                                    columnNumber: 43
                                }, void 0)
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 273,
                                columnNumber: 25
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/components/Charts.tsx",
                        lineNumber: 248,
                        columnNumber: 21
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/app/components/Charts.tsx",
                    lineNumber: 247,
                    columnNumber: 17
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/components/Charts.tsx",
                lineNumber: 246,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    flex: "1 1 45%",
                    maxHeight: height - 16,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: 4
                },
                children: chartData.map((entry, i)=>{
                    const val = entry[dataKey] || 0;
                    const pct = total > 0 ? (val / total * 100).toFixed(1) : "0";
                    const name = entry[nameKey];
                    const color = colorMap[name] || COLORS[i % COLORS.length];
                    const isHov = hovered === i;
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        onMouseEnter: ()=>setHovered(i),
                        onMouseLeave: ()=>setHovered(null),
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "4px 8px",
                            borderRadius: 4,
                            background: isHov ? "#1A1A1A" : "transparent",
                            cursor: "pointer",
                            transition: "background 120ms cubic-bezier(0.16,1,0.3,1)"
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    width: 8,
                                    height: 8,
                                    borderRadius: 2,
                                    background: color,
                                    flexShrink: 0
                                }
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 310,
                                columnNumber: 29
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    flex: 1,
                                    fontSize: 11,
                                    color: isHov ? "#F5F5F5" : "#888888",
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    fontWeight: isHov ? 500 : 400,
                                    transition: "color 120ms cubic-bezier(0.16,1,0.3,1)"
                                },
                                children: name
                            }, void 0, false, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 311,
                                columnNumber: 29
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontSize: 11,
                                    color: isHov ? color : "#555555",
                                    fontWeight: 500,
                                    flexShrink: 0,
                                    transition: "color 120ms cubic-bezier(0.16,1,0.3,1)"
                                },
                                children: [
                                    pct,
                                    "%"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/components/Charts.tsx",
                                lineNumber: 323,
                                columnNumber: 29
                            }, this)
                        ]
                    }, i, true, {
                        fileName: "[project]/app/components/Charts.tsx",
                        lineNumber: 295,
                        columnNumber: 25
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/app/components/Charts.tsx",
                lineNumber: 279,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/Charts.tsx",
        lineNumber: 245,
        columnNumber: 9
    }, this);
}
_s(SynPieChart, "/660sZzy5oMGcDaMCtcI0YuIMkc=");
_c4 = SynPieChart;
var _c, _c1, _c2, _c3, _c4;
__turbopack_context__.k.register(_c, "SynBarChart");
__turbopack_context__.k.register(_c1, "SynLineChart");
__turbopack_context__.k.register(_c2, "SynAreaChart");
__turbopack_context__.k.register(_c3, "CustomPieTooltip");
__turbopack_context__.k.register(_c4, "SynPieChart");
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/analytics/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>AnalyticsPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/Sidebar.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/TopNav.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/Charts.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";
/* ── Demo data ── */ const DEMO_SUMMARY = {
    total_records: 2847,
    avg_delay_days: 4.7,
    max_delay_days: 21,
    total_cost: 4892500
};
const DEMO_SUPPLIERS = [
    {
        supplier: "Apex Materials",
        avg_delay: 8.3,
        total_cost: 892000,
        risk_score: 82,
        total_shipments: 187
    },
    {
        supplier: "GlobalTech Co",
        avg_delay: 6.9,
        total_cost: 654000,
        risk_score: 76,
        total_shipments: 142
    },
    {
        supplier: "SteelMax Inc",
        avg_delay: 5.2,
        total_cost: 521000,
        risk_score: 68,
        total_shipments: 98
    },
    {
        supplier: "ProLogix Asia",
        avg_delay: 4.8,
        total_cost: 780000,
        risk_score: 65,
        total_shipments: 221
    },
    {
        supplier: "NorthStar Parts",
        avg_delay: 4.1,
        total_cost: 445000,
        risk_score: 58,
        total_shipments: 167
    },
    {
        supplier: "Delta Logistics",
        avg_delay: 2.8,
        total_cost: 356000,
        risk_score: 45,
        total_shipments: 312
    }
];
const DEMO_TIME_SERIES = {
    delay_trend: [
        {
            period: "Jan",
            avg_delay: 3.2
        },
        {
            period: "Feb",
            avg_delay: 3.8
        },
        {
            period: "Mar",
            avg_delay: 4.1
        },
        {
            period: "Apr",
            avg_delay: 5.2
        },
        {
            period: "May",
            avg_delay: 4.7
        },
        {
            period: "Jun",
            avg_delay: 4.9
        }
    ],
    volume_trend: [
        {
            period: "Jan",
            count: 280
        },
        {
            period: "Feb",
            count: 310
        },
        {
            period: "Mar",
            count: 295
        },
        {
            period: "Apr",
            count: 340
        },
        {
            period: "May",
            count: 320
        },
        {
            period: "Jun",
            count: 350
        }
    ]
};
const DEMO_QUALITY = {
    completeness_pct: 94,
    columns: {}
};
/* ── Sub-components ── */ function KpiCard({ label, value, delta, deltaDir }) {
    const dotColor = deltaDir === "up" ? "#22C55E" : deltaDir === "down" ? "#FF4444" : "#F59E0B";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            padding: 20,
            transition: `border-color 120ms ${EASE}`
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
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 61,
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
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 64,
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
                        fileName: "[project]/app/analytics/page.tsx",
                        lineNumber: 69,
                        columnNumber: 11
                    }, this),
                    delta
                ]
            }, void 0, true, {
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 68,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/analytics/page.tsx",
        lineNumber: 52,
        columnNumber: 5
    }, this);
}
_c = KpiCard;
function ChartCard({ title, children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            padding: 20
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    fontSize: 11,
                    fontWeight: 500,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "var(--color-text-2)",
                    marginBottom: 16
                },
                children: title
            }, void 0, false, {
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 83,
                columnNumber: 7
            }, this),
            children
        ]
    }, void 0, true, {
        fileName: "[project]/app/analytics/page.tsx",
        lineNumber: 79,
        columnNumber: 5
    }, this);
}
_c1 = ChartCard;
function NoData({ msg }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: 200,
            fontSize: 13,
            color: "var(--color-text-3)"
        },
        children: msg ?? "Upload data to see analytics."
    }, void 0, false, {
        fileName: "[project]/app/analytics/page.tsx",
        lineNumber: 93,
        columnNumber: 5
    }, this);
}
_c2 = NoData;
function AnalyticsPage() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const [summary, setSummary] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [suppliers, setSuppliers] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [timeSeries, setTimeSeries] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [quality, setQuality] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AnalyticsPage.useEffect": ()=>{
            async function load() {
                const safe = {
                    "AnalyticsPage.useEffect.load.safe": async (path)=>{
                        try {
                            const r = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])(path);
                            return r.ok ? await r.json() : null;
                        } catch  {
                            return null;
                        }
                    }
                }["AnalyticsPage.useEffect.load.safe"];
                const [sumData, supData, tsData, qData] = await Promise.all([
                    safe("/analytics/summary"),
                    safe("/analytics/suppliers"),
                    safe("/analytics/time-series"),
                    safe("/analytics/data-quality")
                ]);
                setSummary(sumData ?? DEMO_SUMMARY);
                setSuppliers(supData ?? DEMO_SUPPLIERS);
                setTimeSeries(tsData ?? DEMO_TIME_SERIES);
                setQuality(qData ?? DEMO_QUALITY);
                setLoading(false);
            }
            load();
        }
    }["AnalyticsPage.useEffect"], []);
    if (loading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "app-layout",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                    fileName: "[project]/app/analytics/page.tsx",
                    lineNumber: 137,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "main-wrapper",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                            fileName: "[project]/app/analytics/page.tsx",
                            lineNumber: 139,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                            className: "main-content",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(4,1fr)",
                                        gap: 16,
                                        marginBottom: 24
                                    },
                                    children: [
                                        ...Array(4)
                                    ].map((_, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                background: "var(--color-surface)",
                                                border: "1px solid var(--color-border)",
                                                borderRadius: 6,
                                                padding: 20,
                                                height: 96
                                            }
                                        }, i, false, {
                                            fileName: "[project]/app/analytics/page.tsx",
                                            lineNumber: 143,
                                            columnNumber: 17
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/app/analytics/page.tsx",
                                    lineNumber: 141,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        background: "var(--color-surface)",
                                        border: "1px solid var(--color-border)",
                                        borderRadius: 6,
                                        height: 300
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/app/analytics/page.tsx",
                                    lineNumber: 146,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/analytics/page.tsx",
                            lineNumber: 140,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/analytics/page.tsx",
                    lineNumber: 138,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/analytics/page.tsx",
            lineNumber: 136,
            columnNumber: 7
        }, this);
    }
    /* ── Derived series ── */ const delayDist = suppliers.map((s)=>({
            name: s.supplier?.length > 11 ? s.supplier.slice(0, 11) + "…" : s.supplier,
            avg_delay: s.avg_delay,
            total_cost: s.total_cost,
            risk_score: s.risk_score ?? 0,
            shipments: s.total_shipments ?? s.rows ?? 0
        }));
    const costBySupplier = suppliers.map((s)=>({
            name: s.supplier?.length > 11 ? s.supplier.slice(0, 11) + "…" : s.supplier,
            value: s.total_cost
        }));
    const completeness = quality?.completeness_pct ?? 0;
    const qualityColumns = Object.entries(quality?.columns ?? {});
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "app-layout",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 172,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "main-wrapper",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                        fileName: "[project]/app/analytics/page.tsx",
                        lineNumber: 174,
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
                                                children: "Intelligence"
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 183,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                                style: {
                                                    fontSize: 22,
                                                    fontWeight: 600,
                                                    color: "var(--color-text-1)",
                                                    lineHeight: 1.2
                                                },
                                                children: "Analytics"
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 184,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                style: {
                                                    fontSize: 13,
                                                    color: "var(--color-text-2)",
                                                    marginTop: 2
                                                },
                                                children: "Supply chain metrics, trends, and data quality across all suppliers"
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 187,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 182,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            gap: 8,
                                            flexShrink: 0
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: ()=>router.push("/upload"),
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
                                                    transition: `background 120ms ${EASE}`
                                                },
                                                onMouseEnter: (e)=>e.currentTarget.style.background = "var(--color-surface-2)",
                                                onMouseLeave: (e)=>e.currentTarget.style.background = "transparent",
                                                children: "Upload New Data"
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 192,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                onClick: ()=>router.push("/export"),
                                                style: {
                                                    display: "inline-flex",
                                                    alignItems: "center",
                                                    padding: "8px 16px",
                                                    borderRadius: 4,
                                                    fontSize: 13,
                                                    fontWeight: 600,
                                                    fontFamily: "var(--font-sans)",
                                                    background: "var(--color-accent)",
                                                    color: "#0A0A0A",
                                                    border: "none",
                                                    cursor: "pointer",
                                                    transition: `opacity 120ms ${EASE}`
                                                },
                                                onMouseEnter: (e)=>e.currentTarget.style.opacity = "0.88",
                                                onMouseLeave: (e)=>e.currentTarget.style.opacity = "1",
                                                children: "Export CSV"
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 206,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 191,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/analytics/page.tsx",
                                lineNumber: 178,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "grid",
                                    gridTemplateColumns: "repeat(4, 1fr)",
                                    gap: 16,
                                    marginBottom: 24
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(KpiCard, {
                                        label: "Total Records",
                                        value: summary?.total_records?.toLocaleString() ?? "0",
                                        delta: `${suppliers.length} suppliers`,
                                        deltaDir: "neutral"
                                    }, void 0, false, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 225,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(KpiCard, {
                                        label: "Avg Delay",
                                        value: `${(summary?.avg_delay_days ?? 0).toFixed(1)}d`,
                                        delta: (summary?.avg_delay_days ?? 0) > 5 ? "Above threshold" : "Within range",
                                        deltaDir: (summary?.avg_delay_days ?? 0) > 5 ? "down" : "up"
                                    }, void 0, false, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 231,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(KpiCard, {
                                        label: "Max Delay",
                                        value: `${summary?.max_delay_days ?? 0}d`,
                                        delta: "Worst recorded shipment",
                                        deltaDir: "down"
                                    }, void 0, false, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 237,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(KpiCard, {
                                        label: "Data Completeness",
                                        value: `${completeness}%`,
                                        delta: completeness >= 90 ? "Excellent quality" : completeness >= 70 ? "Acceptable" : "Review required",
                                        deltaDir: completeness >= 90 ? "up" : completeness >= 70 ? "neutral" : "down"
                                    }, void 0, false, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 243,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/analytics/page.tsx",
                                lineNumber: 224,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "grid",
                                    gridTemplateColumns: "1fr 340px",
                                    gap: 16,
                                    alignItems: "start"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            flexDirection: "column",
                                            gap: 16
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Average Delay by Supplier",
                                                children: delayDist.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynBarChart"], {
                                                    data: delayDist,
                                                    dataKey: "avg_delay",
                                                    nameKey: "name",
                                                    color: "#F59E0B",
                                                    height: 260
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 260,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {}, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 262,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 258,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Delay Trend Over Time",
                                                children: timeSeries?.delay_trend?.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynAreaChart"], {
                                                    data: timeSeries.delay_trend,
                                                    dataKey: "avg_delay",
                                                    xKey: "period",
                                                    color: "#F59E0B",
                                                    height: 220
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 269,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {
                                                    msg: "Upload time-stamped data for trend analysis."
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 271,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 267,
                                                columnNumber: 15
                                            }, this),
                                            qualityColumns.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    background: "var(--color-surface)",
                                                    border: "1px solid var(--color-border)",
                                                    borderRadius: 6,
                                                    overflow: "hidden"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            padding: "14px 20px",
                                                            borderBottom: "1px solid var(--color-border)"
                                                        },
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 11,
                                                                fontWeight: 500,
                                                                textTransform: "uppercase",
                                                                letterSpacing: "0.05em",
                                                                color: "var(--color-text-2)"
                                                            },
                                                            children: "Data Quality Report"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/analytics/page.tsx",
                                                            lineNumber: 284,
                                                            columnNumber: 21
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/analytics/page.tsx",
                                                        lineNumber: 281,
                                                        columnNumber: 19
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                                                        style: {
                                                            width: "100%",
                                                            borderCollapse: "collapse",
                                                            fontSize: 13
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                    children: [
                                                                        "COLUMN",
                                                                        "TYPE",
                                                                        "MISSING",
                                                                        "UNIQUE VALUES",
                                                                        "QUALITY"
                                                                    ].map((h)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                                            style: {
                                                                                textAlign: "left",
                                                                                padding: "10px 16px",
                                                                                fontSize: 11,
                                                                                fontWeight: 500,
                                                                                textTransform: "uppercase",
                                                                                letterSpacing: "0.05em",
                                                                                color: "var(--color-text-3)",
                                                                                borderBottom: "1px solid var(--color-border)",
                                                                                background: "var(--color-surface)"
                                                                            },
                                                                            children: h
                                                                        }, h, false, {
                                                                            fileName: "[project]/app/analytics/page.tsx",
                                                                            lineNumber: 292,
                                                                            columnNumber: 27
                                                                        }, this))
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/analytics/page.tsx",
                                                                    lineNumber: 290,
                                                                    columnNumber: 23
                                                                }, this)
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                lineNumber: 289,
                                                                columnNumber: 21
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                                                children: qualityColumns.map(([col, info])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                        style: {
                                                                            transition: `background 120ms ${EASE}`
                                                                        },
                                                                        onMouseEnter: (e)=>e.currentTarget.style.background = "var(--color-surface-2)",
                                                                        onMouseLeave: (e)=>e.currentTarget.style.background = "transparent",
                                                                        children: [
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    fontWeight: 500,
                                                                                    color: "var(--color-text-1)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: col
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 313,
                                                                                columnNumber: 27
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    color: "var(--color-text-3)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: info.dtype
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 316,
                                                                                columnNumber: 27
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                    style: {
                                                                                        fontWeight: 500,
                                                                                        color: info.missing_pct > 10 ? "#FF4444" : info.missing_pct > 0 ? "#F59E0B" : "#22C55E"
                                                                                    },
                                                                                    children: [
                                                                                        info.missing_pct,
                                                                                        "%"
                                                                                    ]
                                                                                }, void 0, true, {
                                                                                    fileName: "[project]/app/analytics/page.tsx",
                                                                                    lineNumber: 320,
                                                                                    columnNumber: 29
                                                                                }, this)
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 319,
                                                                                columnNumber: 27
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    color: "var(--color-text-2)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: info.unique_values
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 324,
                                                                                columnNumber: 27
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                    style: {
                                                                                        width: 64,
                                                                                        height: 4,
                                                                                        borderRadius: 999,
                                                                                        background: "var(--color-surface-2)",
                                                                                        overflow: "hidden"
                                                                                    },
                                                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                        style: {
                                                                                            width: `${100 - info.missing_pct}%`,
                                                                                            height: "100%",
                                                                                            borderRadius: 999,
                                                                                            background: info.missing_pct > 10 ? "#FF4444" : "#22C55E",
                                                                                            transition: `width 160ms ${EASE}`
                                                                                        }
                                                                                    }, void 0, false, {
                                                                                        fileName: "[project]/app/analytics/page.tsx",
                                                                                        lineNumber: 329,
                                                                                        columnNumber: 31
                                                                                    }, this)
                                                                                }, void 0, false, {
                                                                                    fileName: "[project]/app/analytics/page.tsx",
                                                                                    lineNumber: 328,
                                                                                    columnNumber: 29
                                                                                }, this)
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 327,
                                                                                columnNumber: 27
                                                                            }, this)
                                                                        ]
                                                                    }, col, true, {
                                                                        fileName: "[project]/app/analytics/page.tsx",
                                                                        lineNumber: 307,
                                                                        columnNumber: 25
                                                                    }, this))
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                lineNumber: 305,
                                                                columnNumber: 21
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/app/analytics/page.tsx",
                                                        lineNumber: 288,
                                                        columnNumber: 19
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 277,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    background: "var(--color-surface)",
                                                    border: "1px solid var(--color-border)",
                                                    borderRadius: 6,
                                                    overflow: "hidden"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            padding: "14px 20px",
                                                            borderBottom: "1px solid var(--color-border)"
                                                        },
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontSize: 11,
                                                                fontWeight: 500,
                                                                textTransform: "uppercase",
                                                                letterSpacing: "0.05em",
                                                                color: "var(--color-text-2)"
                                                            },
                                                            children: "Supplier Detail"
                                                        }, void 0, false, {
                                                            fileName: "[project]/app/analytics/page.tsx",
                                                            lineNumber: 349,
                                                            columnNumber: 19
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/app/analytics/page.tsx",
                                                        lineNumber: 348,
                                                        columnNumber: 17
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                                                        style: {
                                                            width: "100%",
                                                            borderCollapse: "collapse",
                                                            fontSize: 13
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                    children: [
                                                                        "SUPPLIER",
                                                                        "RISK SCORE",
                                                                        "AVG DELAY",
                                                                        "SHIPMENTS",
                                                                        "TOTAL COST"
                                                                    ].map((h)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                                            style: {
                                                                                textAlign: "left",
                                                                                padding: "10px 16px",
                                                                                fontSize: 11,
                                                                                fontWeight: 500,
                                                                                textTransform: "uppercase",
                                                                                letterSpacing: "0.05em",
                                                                                color: "var(--color-text-3)",
                                                                                borderBottom: "1px solid var(--color-border)",
                                                                                background: "var(--color-surface)"
                                                                            },
                                                                            children: h
                                                                        }, h, false, {
                                                                            fileName: "[project]/app/analytics/page.tsx",
                                                                            lineNumber: 357,
                                                                            columnNumber: 25
                                                                        }, this))
                                                                }, void 0, false, {
                                                                    fileName: "[project]/app/analytics/page.tsx",
                                                                    lineNumber: 355,
                                                                    columnNumber: 21
                                                                }, this)
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                lineNumber: 354,
                                                                columnNumber: 19
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                                                children: delayDist.map((s, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                                        style: {
                                                                            transition: `background 120ms ${EASE}`
                                                                        },
                                                                        onMouseEnter: (e)=>e.currentTarget.style.background = "var(--color-surface-2)",
                                                                        onMouseLeave: (e)=>e.currentTarget.style.background = "transparent",
                                                                        children: [
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    fontWeight: 500,
                                                                                    color: "var(--color-text-1)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: suppliers[i]?.supplier
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 378,
                                                                                columnNumber: 25
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                    style: {
                                                                                        display: "flex",
                                                                                        alignItems: "center",
                                                                                        gap: 8
                                                                                    },
                                                                                    children: [
                                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                                            style: {
                                                                                                fontWeight: 600,
                                                                                                minWidth: 28,
                                                                                                color: s.risk_score >= 70 ? "#FF4444" : s.risk_score >= 40 ? "#F59E0B" : "#22C55E"
                                                                                            },
                                                                                            children: s.risk_score
                                                                                        }, void 0, false, {
                                                                                            fileName: "[project]/app/analytics/page.tsx",
                                                                                            lineNumber: 383,
                                                                                            columnNumber: 29
                                                                                        }, this),
                                                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                            style: {
                                                                                                width: 64,
                                                                                                height: 4,
                                                                                                borderRadius: 999,
                                                                                                background: "var(--color-surface-2)",
                                                                                                overflow: "hidden"
                                                                                            },
                                                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                                                style: {
                                                                                                    width: `${s.risk_score}%`,
                                                                                                    height: "100%",
                                                                                                    borderRadius: 999,
                                                                                                    background: s.risk_score >= 70 ? "#FF4444" : s.risk_score >= 40 ? "#F59E0B" : "#22C55E"
                                                                                                }
                                                                                            }, void 0, false, {
                                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                                lineNumber: 387,
                                                                                                columnNumber: 31
                                                                                            }, this)
                                                                                        }, void 0, false, {
                                                                                            fileName: "[project]/app/analytics/page.tsx",
                                                                                            lineNumber: 386,
                                                                                            columnNumber: 29
                                                                                        }, this)
                                                                                    ]
                                                                                }, void 0, true, {
                                                                                    fileName: "[project]/app/analytics/page.tsx",
                                                                                    lineNumber: 382,
                                                                                    columnNumber: 27
                                                                                }, this)
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 381,
                                                                                columnNumber: 25
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    color: "var(--color-text-1)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: [
                                                                                    s.avg_delay,
                                                                                    "d"
                                                                                ]
                                                                            }, void 0, true, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 394,
                                                                                columnNumber: 25
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    color: "var(--color-text-2)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: s.shipments
                                                                            }, void 0, false, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 397,
                                                                                columnNumber: 25
                                                                            }, this),
                                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                                                style: {
                                                                                    padding: "0 16px",
                                                                                    height: 44,
                                                                                    color: "var(--color-text-2)",
                                                                                    borderBottom: "1px solid var(--color-border)",
                                                                                    verticalAlign: "middle"
                                                                                },
                                                                                children: [
                                                                                    "₹",
                                                                                    s.total_cost?.toLocaleString()
                                                                                ]
                                                                            }, void 0, true, {
                                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                                lineNumber: 400,
                                                                                columnNumber: 25
                                                                            }, this)
                                                                        ]
                                                                    }, i, true, {
                                                                        fileName: "[project]/app/analytics/page.tsx",
                                                                        lineNumber: 372,
                                                                        columnNumber: 23
                                                                    }, this))
                                                            }, void 0, false, {
                                                                fileName: "[project]/app/analytics/page.tsx",
                                                                lineNumber: 370,
                                                                columnNumber: 19
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/app/analytics/page.tsx",
                                                        lineNumber: 353,
                                                        columnNumber: 17
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 344,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 255,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            flexDirection: "column",
                                            gap: 16
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Cost Distribution",
                                                children: costBySupplier.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynPieChart"], {
                                                    data: costBySupplier,
                                                    dataKey: "value",
                                                    nameKey: "name",
                                                    height: 220
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 417,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {}, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 419,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 415,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Risk Score vs Avg Delay",
                                                children: delayDist.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynLineChart"], {
                                                    data: delayDist,
                                                    lines: [
                                                        {
                                                            key: "risk_score",
                                                            color: "#FF4444",
                                                            name: "Risk Score"
                                                        },
                                                        {
                                                            key: "avg_delay",
                                                            color: "#F59E0B",
                                                            name: "Avg Delay"
                                                        }
                                                    ],
                                                    xKey: "name",
                                                    height: 220
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 426,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {}, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 436,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 424,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Volume Trend",
                                                children: timeSeries?.volume_trend?.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynAreaChart"], {
                                                    data: timeSeries.volume_trend,
                                                    dataKey: "count",
                                                    xKey: "period",
                                                    color: "#888888",
                                                    height: 180
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 443,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {
                                                    msg: "Upload time-stamped data for volume trend."
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 445,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 441,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ChartCard, {
                                                title: "Shipment Volume by Supplier",
                                                children: delayDist.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Charts$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SynBarChart"], {
                                                    data: delayDist,
                                                    dataKey: "shipments",
                                                    nameKey: "name",
                                                    color: "#22C55E",
                                                    height: 200
                                                }, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 452,
                                                    columnNumber: 19
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(NoData, {}, void 0, false, {
                                                    fileName: "[project]/app/analytics/page.tsx",
                                                    lineNumber: 454,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/app/analytics/page.tsx",
                                                lineNumber: 450,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/analytics/page.tsx",
                                        lineNumber: 412,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/analytics/page.tsx",
                                lineNumber: 252,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/analytics/page.tsx",
                        lineNumber: 175,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/analytics/page.tsx",
                lineNumber: 173,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/analytics/page.tsx",
        lineNumber: 171,
        columnNumber: 5
    }, this);
}
_s(AnalyticsPage, "4pc3IynuGHnpwkuhpHgN8VzfzN4=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c3 = AnalyticsPage;
var _c, _c1, _c2, _c3;
__turbopack_context__.k.register(_c, "KpiCard");
__turbopack_context__.k.register(_c1, "ChartCard");
__turbopack_context__.k.register(_c2, "NoData");
__turbopack_context__.k.register(_c3, "AnalyticsPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_5d424382._.js.map