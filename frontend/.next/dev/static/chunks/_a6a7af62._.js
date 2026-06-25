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
"[project]/app/components/SafeMarkdown.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Safe markdown-like text renderer.
 * Converts **bold** to <strong> and splits by newline for paragraphs.
 * Returns an array of React elements — NO dangerouslySetInnerHTML.
 */ __turbopack_context__.s([
    "SafeMarkdown",
    ()=>SafeMarkdown
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
;
function SafeMarkdown({ text }) {
    if (!text) return null;
    const lines = text.split("\n");
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: lines.map((line, i)=>{
            // Convert **bold** to strong elements
            const parts = line.split(/(\*\*.*?\*\*)/g);
            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                children: [
                    parts.map((part, j)=>{
                        if (part.startsWith("**") && part.endsWith("**")) {
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                children: part.slice(2, -2)
                            }, j, false, {
                                fileName: "[project]/app/components/SafeMarkdown.tsx",
                                lineNumber: 20,
                                columnNumber: 24
                            }, this);
                        }
                        // Convert - bullet to •
                        if (part.startsWith("- ")) {
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                children: [
                                    "• ",
                                    part.slice(2)
                                ]
                            }, j, true, {
                                fileName: "[project]/app/components/SafeMarkdown.tsx",
                                lineNumber: 24,
                                columnNumber: 24
                            }, this);
                        }
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            children: part
                        }, j, false, {
                            fileName: "[project]/app/components/SafeMarkdown.tsx",
                            lineNumber: 26,
                            columnNumber: 22
                        }, this);
                    }),
                    i < lines.length - 1 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {}, void 0, false, {
                        fileName: "[project]/app/components/SafeMarkdown.tsx",
                        lineNumber: 28,
                        columnNumber: 38
                    }, this)
                ]
            }, i, true, {
                fileName: "[project]/app/components/SafeMarkdown.tsx",
                lineNumber: 17,
                columnNumber: 11
            }, this);
        })
    }, void 0, false);
}
_c = SafeMarkdown;
var _c;
__turbopack_context__.k.register(_c, "SafeMarkdown");
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
"[project]/app/components/hooks/use-file-input.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useFileInput",
    ()=>useFileInput
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
function useFileInput({ accept, maxSize }) {
    _s();
    const [fileName, setFileName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [selectedFile, setSelectedFile] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const fileInputRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const [fileSize, setFileSize] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const handleFileSelect = (e)=>{
        const file = e.target.files?.[0];
        validateAndSetFile(file);
    };
    const validateAndSetFile = (file)=>{
        setError("");
        if (file) {
            if (maxSize && file.size > maxSize * 1024 * 1024) {
                setError(`File size must be less than ${maxSize}MB`);
                return;
            }
            if (accept && !file.type.match(accept.replace("/*", "/"))) {
                setError(`File type must be ${accept}`);
                return;
            }
            setFileSize(file.size);
            setFileName(file.name);
            setSelectedFile(file);
        }
    };
    const clearFile = ()=>{
        setFileName("");
        setSelectedFile(null);
        setError("");
        setFileSize(0);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };
    return {
        fileName,
        selectedFile,
        error,
        fileInputRef,
        handleFileSelect,
        validateAndSetFile,
        clearFile,
        fileSize
    };
}
_s(useFileInput, "9TTm4MPljhXvF04PIcgWGrCobLE=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/components/hooks/use-auto-resize-textarea.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAutoResizeTextarea",
    ()=>useAutoResizeTextarea
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
function useAutoResizeTextarea({ minHeight, maxHeight }) {
    _s();
    const textareaRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const adjustHeight = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAutoResizeTextarea.useCallback[adjustHeight]": (reset)=>{
            const textarea = textareaRef.current;
            if (!textarea) return;
            if (reset) {
                textarea.style.height = `${minHeight}px`;
                return;
            }
            // Temporarily shrink to get the right scrollHeight
            textarea.style.height = `${minHeight}px`;
            // Calculate new height
            const newHeight = Math.max(minHeight, Math.min(textarea.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY));
            textarea.style.height = `${newHeight}px`;
        }
    }["useAutoResizeTextarea.useCallback[adjustHeight]"], [
        minHeight,
        maxHeight
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useAutoResizeTextarea.useEffect": ()=>{
            // Set initial height
            const textarea = textareaRef.current;
            if (textarea) {
                textarea.style.height = `${minHeight}px`;
            }
        }
    }["useAutoResizeTextarea.useEffect"], [
        minHeight
    ]);
    // Adjust height on window resize
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useAutoResizeTextarea.useEffect": ()=>{
            const handleResize = {
                "useAutoResizeTextarea.useEffect.handleResize": ()=>adjustHeight()
            }["useAutoResizeTextarea.useEffect.handleResize"];
            window.addEventListener("resize", handleResize);
            return ({
                "useAutoResizeTextarea.useEffect": ()=>window.removeEventListener("resize", handleResize)
            })["useAutoResizeTextarea.useEffect"];
        }
    }["useAutoResizeTextarea.useEffect"], [
        adjustHeight
    ]);
    return {
        textareaRef,
        adjustHeight
    };
}
_s(useAutoResizeTextarea, "dY5gUJDyLTt7nR3p8fNJ7y+Lo90=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/components/ui/ai-input-with-file.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AIInputWithFile",
    ()=>AIInputWithFile
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$corner$2d$right$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CornerRightUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/corner-right-up.js [app-client] (ecmascript) <export default as CornerRightUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/file-up.js [app-client] (ecmascript) <export default as FileUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$paperclip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Paperclip$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/paperclip.js [app-client] (ecmascript) <export default as Paperclip>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$file$2d$input$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/hooks/use-file-input.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$auto$2d$resize$2d$textarea$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/hooks/use-auto-resize-textarea.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
function FileDisplay({ fileName, onClear }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "4px 12px",
            borderRadius: "var(--radius-md)",
            background: "var(--color-surface-2)",
            border: "1px solid var(--color-border)",
            fontSize: 12,
            color: "var(--color-text-secondary)",
            marginBottom: 6
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileUp$3e$__["FileUp"], {
                size: 14,
                color: "var(--color-text-muted)"
            }, void 0, false, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 29,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                style: {
                    maxWidth: 200,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap"
                },
                children: fileName
            }, void 0, false, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 30,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                onClick: onClear,
                style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: 2,
                    borderRadius: "50%",
                    border: "none",
                    background: "none",
                    cursor: "pointer",
                    color: "var(--color-text-muted)",
                    lineHeight: 1
                },
                title: "Remove file",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                    size: 12
                }, void 0, false, {
                    fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                    lineNumber: 50,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 33,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
        lineNumber: 15,
        columnNumber: 5
    }, this);
}
_c = FileDisplay;
function AIInputWithFile({ id = "ai-input-with-file", placeholder = "Ask anything or upload context (max 5MB)…", minHeight = 52, maxHeight = 200, accept = "image/*,application/pdf,text/plain", maxFileSize = 5, onSubmit }) {
    _s();
    const [inputValue, setInputValue] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [hoverAttach, setHoverAttach] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [hoverSend, setHoverSend] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const { fileName, fileInputRef, handleFileSelect, clearFile, selectedFile } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$file$2d$input$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useFileInput"])({
        accept,
        maxSize: maxFileSize
    });
    const { textareaRef, adjustHeight } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$auto$2d$resize$2d$textarea$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAutoResizeTextarea"])({
        minHeight,
        maxHeight
    });
    const handleSubmit = ()=>{
        if (inputValue.trim() || selectedFile) {
            onSubmit?.(inputValue, selectedFile ?? undefined);
            setInputValue("");
            clearFile();
            adjustHeight(true);
        }
    };
    const canSend = inputValue.trim().length > 0 || !!selectedFile;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            width: "100%",
            maxWidth: 800,
            margin: "0 auto"
        },
        children: [
            fileName && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(FileDisplay, {
                fileName: fileName,
                onClear: clearFile
            }, void 0, false, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 102,
                columnNumber: 20
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    position: "relative",
                    borderRadius: "var(--radius-lg)",
                    border: "1px solid var(--color-border)",
                    background: "var(--color-surface)",
                    boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
                    transition: "border-color var(--transition-fast), box-shadow var(--transition-fast)"
                },
                onFocus: ()=>{},
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>fileInputRef.current?.click(),
                        onMouseEnter: ()=>setHoverAttach(true),
                        onMouseLeave: ()=>setHoverAttach(false),
                        title: "Attach file",
                        style: {
                            position: "absolute",
                            left: 12,
                            top: "50%",
                            transform: "translateY(-50%)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 30,
                            height: 30,
                            borderRadius: "var(--radius-md)",
                            border: "none",
                            background: hoverAttach ? "var(--color-surface-2)" : "transparent",
                            color: hoverAttach ? "var(--color-text)" : "var(--color-text-muted)",
                            cursor: "pointer",
                            transition: "all var(--transition-fast)"
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$paperclip$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Paperclip$3e$__["Paperclip"], {
                            size: 15,
                            style: {
                                transform: "rotate(45deg) scaleX(-1)"
                            }
                        }, void 0, false, {
                            fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                            lineNumber: 141,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 117,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                        type: "file",
                        style: {
                            display: "none"
                        },
                        ref: fileInputRef,
                        onChange: handleFileSelect,
                        accept: accept
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 145,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                        id: id,
                        ref: textareaRef,
                        value: inputValue,
                        placeholder: placeholder,
                        onChange: (e)=>{
                            setInputValue(e.target.value);
                            adjustHeight();
                        },
                        onKeyDown: (e)=>{
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit();
                            }
                        },
                        style: {
                            width: "100%",
                            paddingLeft: 50,
                            paddingRight: 52,
                            paddingTop: 14,
                            paddingBottom: 14,
                            minHeight: minHeight,
                            maxHeight: maxHeight,
                            background: "transparent",
                            border: "none",
                            outline: "none",
                            resize: "none",
                            color: "var(--color-text)",
                            fontSize: 14,
                            fontFamily: "var(--font-sans)",
                            lineHeight: 1.5,
                            overflowY: "auto",
                            display: "block",
                            boxSizing: "border-box"
                        }
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 154,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: handleSubmit,
                        disabled: !canSend,
                        onMouseEnter: ()=>setHoverSend(true),
                        onMouseLeave: ()=>setHoverSend(false),
                        title: "Send",
                        style: {
                            position: "absolute",
                            right: 10,
                            top: "50%",
                            transform: "translateY(-50%)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 34,
                            height: 34,
                            borderRadius: "var(--radius-md)",
                            border: "none",
                            background: canSend ? hoverSend ? "var(--color-primary-hover)" : "var(--color-primary)" : "var(--color-surface-2)",
                            color: canSend ? "#fff" : "var(--color-text-muted)",
                            cursor: canSend ? "pointer" : "not-allowed",
                            opacity: canSend ? 1 : 0.5,
                            transition: "all var(--transition-fast)",
                            boxShadow: canSend ? "0 0 12px rgba(99,102,241,0.3)" : "none"
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$corner$2d$right$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CornerRightUp$3e$__["CornerRightUp"], {
                            size: 15
                        }, void 0, false, {
                            fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                            lineNumber: 223,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 192,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 105,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    fontSize: 11,
                    color: "var(--color-text-muted)",
                    marginTop: 6,
                    paddingLeft: 2
                },
                children: [
                    "Press ",
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("kbd", {
                        style: {
                            fontSize: 10,
                            fontFamily: "var(--font-mono)",
                            padding: "1px 5px",
                            borderRadius: 4,
                            background: "var(--color-surface-2)",
                            border: "1px solid var(--color-border)",
                            color: "var(--color-text-muted)"
                        },
                        children: "Enter"
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 234,
                        columnNumber: 15
                    }, this),
                    " to send · ",
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("kbd", {
                        style: {
                            fontSize: 10,
                            fontFamily: "var(--font-mono)",
                            padding: "1px 5px",
                            borderRadius: 4,
                            background: "var(--color-surface-2)",
                            border: "1px solid var(--color-border)",
                            color: "var(--color-text-muted)"
                        },
                        children: "Shift+Enter"
                    }, void 0, false, {
                        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                        lineNumber: 242,
                        columnNumber: 34
                    }, this),
                    " for new line"
                ]
            }, void 0, true, {
                fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
                lineNumber: 228,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/components/ui/ai-input-with-file.tsx",
        lineNumber: 100,
        columnNumber: 5
    }, this);
}
_s(AIInputWithFile, "Hn+oDxXzo2S4iNe5xa08dsRd210=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$file$2d$input$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useFileInput"],
        __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$hooks$2f$use$2d$auto$2d$resize$2d$textarea$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAutoResizeTextarea"]
    ];
});
_c1 = AIInputWithFile;
var _c, _c1;
__turbopack_context__.k.register(_c, "FileDisplay");
__turbopack_context__.k.register(_c1, "AIInputWithFile");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/app/copilot/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>CopilotPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/Sidebar.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/TopNav.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$SafeMarkdown$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/SafeMarkdown.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/ToastContext.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bot$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bot$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/bot.js [app-client] (ecmascript) <export default as Bot>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$lightbulb$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Lightbulb$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/lightbulb.js [app-client] (ecmascript) <export default as Lightbulb>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-client] (ecmascript) <export default as AlertTriangle>");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ui$2f$ai$2d$input$2d$with$2d$file$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/ui/ai-input-with-file.tsx [app-client] (ecmascript)");
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
;
const QUICK_PROMPTS = [
    "What is the overall risk status?",
    "Why is the top supplier risky?",
    "What if the top supplier fails?",
    "What if port congestion increases 30%?",
    "Suggest alternative suppliers",
    "What is the financial impact of delays?"
];
function CopilotPage() {
    _s();
    const { showToast } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"])();
    const [messages, setMessages] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [input, setInput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [mode, setMode] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("ask");
    const bottomRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "CopilotPage.useEffect": ()=>{
            // Load initial executive summary
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])(`/copilot/summary`).then({
                "CopilotPage.useEffect": (r)=>{
                    if (!r.ok) throw new Error("Failed to load summary");
                    return r.json();
                }
            }["CopilotPage.useEffect"]).then({
                "CopilotPage.useEffect": (data)=>{
                    if (data.narrative) {
                        setMessages([
                            {
                                role: "ai",
                                content: `**Executive Summary**\n\n${data.narrative}\n\n**Risk Level: ${data.overall_risk_level}**`,
                                data: data
                            }
                        ]);
                    }
                }
            }["CopilotPage.useEffect"]).catch({
                "CopilotPage.useEffect": ()=>{}
            }["CopilotPage.useEffect"]);
        }
    }["CopilotPage.useEffect"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "CopilotPage.useEffect": ()=>{
            bottomRef.current?.scrollIntoView({
                behavior: "smooth"
            });
        }
    }["CopilotPage.useEffect"], [
        messages
    ]);
    const sendMessage = async (text)=>{
        const msg = text || input;
        if (!msg.trim()) return;
        setMessages((prev)=>[
                ...prev,
                {
                    role: "user",
                    content: msg
                }
            ]);
        setInput("");
        setLoading(true);
        try {
            const endpoint = mode === "whatif" ? "/copilot/what-if" : "/copilot/ask";
            const body = mode === "whatif" ? {
                scenario: msg
            } : {
                question: msg
            };
            const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiPostJSON"])(endpoint, body);
            // Format response
            let content = "";
            if (data.answer) {
                content = data.answer;
            } else if (data.narrative) {
                content = data.narrative;
            } else if (data.ripple_effects) {
                content = `**Scenario:** ${data.scenario}\n**Severity:** ${data.severity || "N/A"}\n\n`;
                content += data.ripple_effects.join("\n\n");
                if (data.mitigation_suggestions) {
                    content += "\n\n**Mitigation:**\n" + data.mitigation_suggestions.map((s)=>`- ${s}`).join("\n");
                }
                if (data.financial_impact) {
                    content += `\n\n**Financial Impact:**\n- Cost at risk: ₹${data.financial_impact.direct_cost_at_risk?.toLocaleString() || "N/A"}`;
                }
            } else {
                content = JSON.stringify(data, null, 2);
            }
            setMessages((prev)=>[
                    ...prev,
                    {
                        role: "ai",
                        content,
                        data
                    }
                ]);
        } catch  {
            setMessages((prev)=>[
                    ...prev,
                    {
                        role: "ai",
                        content: "⚠️ Failed to process your request. Make sure the backend is running."
                    }
                ]);
            showToast("AI request failed. Check backend connectivity.", "error");
        } finally{
            setLoading(false);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "app-layout",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                fileName: "[project]/app/copilot/page.tsx",
                lineNumber: 107,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "main-wrapper",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$TopNav$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {}, void 0, false, {
                        fileName: "[project]/app/copilot/page.tsx",
                        lineNumber: 109,
                        columnNumber: 13
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                        className: "main-content",
                        style: {
                            display: "flex",
                            flexDirection: "column"
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    marginBottom: 16
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                        style: {
                                            fontFamily: "var(--font-plex)",
                                            fontSize: 28,
                                            fontWeight: 700,
                                            marginBottom: 4
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$bot$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Bot$3e$__["Bot"], {
                                                size: 24,
                                                style: {
                                                    display: "inline",
                                                    marginRight: 10,
                                                    verticalAlign: "middle"
                                                }
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 114,
                                                columnNumber: 25
                                            }, this),
                                            "AI Co-Pilot"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 113,
                                        columnNumber: 21
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        style: {
                                            color: "var(--text-secondary)",
                                            fontSize: 13
                                        },
                                        children: "Ask questions, run what-if simulations, and get AI-powered supply chain intelligence"
                                    }, void 0, false, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 117,
                                        columnNumber: 21
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/copilot/page.tsx",
                                lineNumber: 112,
                                columnNumber: 17
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    gap: 8,
                                    marginBottom: 16
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        onClick: ()=>setMode("ask"),
                                        style: {
                                            padding: "6px 16px",
                                            borderRadius: 8,
                                            border: "1px solid var(--border-medium)",
                                            background: mode === "ask" ? "var(--accent-soft)" : "transparent",
                                            color: mode === "ask" ? "#facc15" : "var(--text-secondary)",
                                            cursor: "pointer",
                                            fontSize: 12,
                                            fontWeight: 600,
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 6
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$lightbulb$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Lightbulb$3e$__["Lightbulb"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 140,
                                                columnNumber: 25
                                            }, this),
                                            " Ask Questions"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 124,
                                        columnNumber: 21
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        onClick: ()=>setMode("whatif"),
                                        style: {
                                            padding: "6px 16px",
                                            borderRadius: 8,
                                            border: "1px solid var(--border-medium)",
                                            background: mode === "whatif" ? "rgba(239,68,68,0.08)" : "transparent",
                                            color: mode === "whatif" ? "#ef4444" : "var(--text-secondary)",
                                            cursor: "pointer",
                                            fontSize: 12,
                                            fontWeight: 600,
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 6
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__AlertTriangle$3e$__["AlertTriangle"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 158,
                                                columnNumber: 25
                                            }, this),
                                            " What-If Simulation"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 142,
                                        columnNumber: 21
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/copilot/page.tsx",
                                lineNumber: 123,
                                columnNumber: 17
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    flexWrap: "wrap",
                                    gap: 6,
                                    marginBottom: 16
                                },
                                children: QUICK_PROMPTS.map((p)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        onClick: ()=>sendMessage(p),
                                        style: {
                                            padding: "4px 12px",
                                            borderRadius: 8,
                                            border: "1px solid var(--border-subtle)",
                                            background: "transparent",
                                            color: "var(--text-secondary)",
                                            cursor: "pointer",
                                            fontSize: 11,
                                            transition: "all 0.2s"
                                        },
                                        onMouseOver: (e)=>{
                                            e.target.style.borderColor = "var(--accent)";
                                            e.target.style.color = "var(--accent)";
                                        },
                                        onMouseOut: (e)=>{
                                            e.target.style.borderColor = "var(--border-subtle)";
                                            e.target.style.color = "var(--text-secondary)";
                                        },
                                        children: p
                                    }, p, false, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 165,
                                        columnNumber: 25
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/app/copilot/page.tsx",
                                lineNumber: 163,
                                columnNumber: 17
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "chat-messages",
                                style: {
                                    flex: 1
                                },
                                children: [
                                    messages.length === 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            textAlign: "center",
                                            padding: "60px 0",
                                            color: "var(--text-muted)"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                                size: 32,
                                                style: {
                                                    marginBottom: 12,
                                                    opacity: 0.4
                                                }
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 196,
                                                columnNumber: 29
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                style: {
                                                    fontSize: 14
                                                },
                                                children: "Ask me anything about your supply chain"
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 197,
                                                columnNumber: 29
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                style: {
                                                    fontSize: 12,
                                                    marginTop: 4
                                                },
                                                children: 'Try: "Why is Supplier A risky?" or "What if lead times increase 20%?"'
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 198,
                                                columnNumber: 29
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 195,
                                        columnNumber: 25
                                    }, this),
                                    messages.map((msg, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            className: `chat-message ${msg.role}`,
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$SafeMarkdown$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SafeMarkdown"], {
                                                text: msg.content
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 205,
                                                columnNumber: 29
                                            }, this)
                                        }, i, false, {
                                            fileName: "[project]/app/copilot/page.tsx",
                                            lineNumber: 204,
                                            columnNumber: 25
                                        }, this)),
                                    loading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "chat-message ai",
                                        style: {
                                            opacity: 0.5
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                                size: 14,
                                                style: {
                                                    animation: "pulse-glow 1.5s infinite"
                                                }
                                            }, void 0, false, {
                                                fileName: "[project]/app/copilot/page.tsx",
                                                lineNumber: 210,
                                                columnNumber: 29
                                            }, this),
                                            " Analyzing..."
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 209,
                                        columnNumber: 25
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        ref: bottomRef
                                    }, void 0, false, {
                                        fileName: "[project]/app/copilot/page.tsx",
                                        lineNumber: 213,
                                        columnNumber: 21
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/copilot/page.tsx",
                                lineNumber: 193,
                                columnNumber: 17
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    marginTop: 16,
                                    paddingBottom: 16
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ui$2f$ai$2d$input$2d$with$2d$file$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AIInputWithFile"], {
                                    placeholder: mode === "whatif" ? 'Describe a scenario… e.g. "What if Supplier A fails?"' : 'Ask a question… e.g. "Why is Supplier B risky?"',
                                    onSubmit: (msg, file)=>{
                                        if (msg.trim()) {
                                            sendMessage(msg);
                                        }
                                        if (file) {
                                            console.log("Selected file:", file);
                                            showToast(`File attached: ${file.name}. Ensure you process it in the backend!`, "success");
                                        }
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/app/copilot/page.tsx",
                                    lineNumber: 218,
                                    columnNumber: 21
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/app/copilot/page.tsx",
                                lineNumber: 217,
                                columnNumber: 17
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/copilot/page.tsx",
                        lineNumber: 110,
                        columnNumber: 13
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/copilot/page.tsx",
                lineNumber: 108,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/copilot/page.tsx",
        lineNumber: 106,
        columnNumber: 9
    }, this);
}
_s(CopilotPage, "zJE6DutTYInFE7xaQ8e3HMwC52I=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"]
    ];
});
_c = CopilotPage;
var _c;
__turbopack_context__.k.register(_c, "CopilotPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_a6a7af62._.js.map