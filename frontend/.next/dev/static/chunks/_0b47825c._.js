(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
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
"[project]/app/upload/map/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>MapColumnsPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/app/components/ToastContext.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
function MapColumnsPage() {
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const { showToast } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"])();
    const [columns, setColumns] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [mapping, setMapping] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        supplier: "",
        sku: "",
        delay_days: "",
        cost: ""
    });
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "MapColumnsPage.useEffect": ()=>{
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])(`/upload/columns`).then({
                "MapColumnsPage.useEffect": (res)=>{
                    if (!res.ok) throw new Error("Failed to fetch columns");
                    return res.json();
                }
            }["MapColumnsPage.useEffect"]).then({
                "MapColumnsPage.useEffect": (data)=>setColumns(data.columns)
            }["MapColumnsPage.useEffect"]).catch({
                "MapColumnsPage.useEffect": ()=>{
                    showToast("Could not load columns. Is the backend running?", "error");
                }
            }["MapColumnsPage.useEffect"]);
        }
    }["MapColumnsPage.useEffect"], [
        showToast
    ]);
    const handleSubmit = async ()=>{
        if (Object.values(mapping).some((v)=>!v)) {
            showToast("Please map all fields before confirming.", "warning");
            return;
        }
        try {
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiFetch"])(`/upload/confirm`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(mapping)
            });
            router.push("/dashboard");
        } catch  {
            showToast("Failed to confirm mapping.", "error");
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        style: {
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#0e1116",
            color: "#fff",
            fontFamily: "var(--font-sans)"
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: "100%",
                maxWidth: 500,
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: 16,
                padding: 32
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                    style: {
                        fontSize: 24,
                        fontWeight: 600,
                        marginBottom: 24
                    },
                    children: "Map Your CSV Columns"
                }, void 0, false, {
                    fileName: "[project]/app/upload/map/page.tsx",
                    lineNumber: 71,
                    columnNumber: 9
                }, this),
                [
                    "supplier",
                    "sku",
                    "delay_days",
                    "cost"
                ].map((field)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            marginBottom: 16
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                style: {
                                    display: "block",
                                    marginBottom: 8,
                                    fontSize: 12,
                                    opacity: 0.7,
                                    textTransform: "uppercase",
                                    letterSpacing: "0.08em"
                                },
                                children: field.toUpperCase()
                            }, void 0, false, {
                                fileName: "[project]/app/upload/map/page.tsx",
                                lineNumber: 77,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                style: {
                                    width: "100%",
                                    background: "#000",
                                    border: "1px solid rgba(255,255,255,0.2)",
                                    padding: "10px 12px",
                                    borderRadius: 8,
                                    color: "#fff",
                                    fontSize: 14,
                                    outline: "none"
                                },
                                onChange: (e)=>setMapping({
                                        ...mapping,
                                        [field]: e.target.value
                                    }),
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "",
                                        children: "Select column"
                                    }, void 0, false, {
                                        fileName: "[project]/app/upload/map/page.tsx",
                                        lineNumber: 104,
                                        columnNumber: 15
                                    }, this),
                                    columns.map((col)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                            value: col,
                                            children: col
                                        }, col, false, {
                                            fileName: "[project]/app/upload/map/page.tsx",
                                            lineNumber: 106,
                                            columnNumber: 17
                                        }, this))
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/upload/map/page.tsx",
                                lineNumber: 89,
                                columnNumber: 13
                            }, this)
                        ]
                    }, field, true, {
                        fileName: "[project]/app/upload/map/page.tsx",
                        lineNumber: 76,
                        columnNumber: 11
                    }, this)),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: handleSubmit,
                    style: {
                        marginTop: 24,
                        width: "100%",
                        background: "var(--color-accent, #06b6d4)",
                        color: "#000",
                        padding: "14px",
                        borderRadius: 10,
                        fontWeight: 600,
                        fontSize: 14,
                        border: "none",
                        cursor: "pointer"
                    },
                    children: "Confirm & Analyze"
                }, void 0, false, {
                    fileName: "[project]/app/upload/map/page.tsx",
                    lineNumber: 114,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/upload/map/page.tsx",
            lineNumber: 62,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/upload/map/page.tsx",
        lineNumber: 51,
        columnNumber: 5
    }, this);
}
_s(MapColumnsPage, "6rye2GYo5qhcgQVcZUTv+lLO9GE=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$app$2f$components$2f$ToastContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useToast"]
    ];
});
_c = MapColumnsPage;
var _c;
__turbopack_context__.k.register(_c, "MapColumnsPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/node_modules/next/navigation.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {

module.exports = __turbopack_context__.r("[project]/node_modules/next/dist/client/components/navigation.js [app-client] (ecmascript)");
}),
]);

//# sourceMappingURL=_0b47825c._.js.map