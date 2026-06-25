/**
 * NEXUS Design Tokens
 * ====================
 * Single source of truth for all design values.
 * Import these in components for type-safe token access.
 */

export const tokens = {
  colors: {
    primary: "#6366f1",
    primaryHover: "#4f46e5",
    primaryLight: "rgba(99, 102, 241, 0.15)",
    primaryGlow: "rgba(99, 102, 241, 0.3)",

    accent: "#06b6d4",
    accentHover: "#0891b2",
    pink: "#ec4899",
    amber: "#f59e0b",

    success: "#22c55e",
    warning: "#f59e0b",
    danger: "#ef4444",
    info: "#06b6d4",

    // Dark theme (default)
    dark: {
      bg: "#0f172a",
      bgAlt: "#0b1120",
      surface: "#1e293b",
      surface2: "#334155",
      surface3: "#475569",
      text: "#f1f5f9",
      textSecondary: "#cbd5e1",
      textMuted: "#94a3b8",
      border: "#334155",
      borderSubtle: "rgba(148, 163, 184, 0.1)",
    },

    // Light theme
    light: {
      bg: "#f8fafc",
      bgAlt: "#f1f5f9",
      surface: "#ffffff",
      surface2: "#f1f5f9",
      surface3: "#e2e8f0",
      text: "#0f172a",
      textSecondary: "#334155",
      textMuted: "#64748b",
      border: "#e2e8f0",
      borderSubtle: "rgba(0, 0, 0, 0.06)",
    },
  },

  radius: {
    sm: "8px",
    md: "12px",
    lg: "16px",
    xl: "20px",
    full: "9999px",
  },

  shadows: {
    sm: "0 1px 3px rgba(0, 0, 0, 0.1)",
    md: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    lg: "0 20px 25px -5px rgb(0 0 0 / 0.15), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    glow: "0 0 0 3px rgba(99, 102, 241, 0.3)",
    cardHover: "0 20px 25px -5px rgb(0 0 0 / 0.2), 0 0 0 1px #6366f1",
  },

  fonts: {
    sans: '"Inter", system-ui, -apple-system, sans-serif',
    display: '"Space Grotesk", system-ui, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", monospace',
  },

  fontSizes: {
    display: "32px",
    displayLineHeight: "40px",
    heading: "24px",
    headingLineHeight: "28px",
    subheading: "18px",
    body: "16px",
    small: "14px",
    caption: "12px",
    micro: "10px",
  },

  fontWeights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "32px",
    "2xl": "48px",
    "3xl": "64px",
  },

  transitions: {
    fast: "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    normal: "250ms cubic-bezier(0.4, 0, 0.2, 1)",
    spring: "400ms cubic-bezier(0.34, 1.56, 0.64, 1)",
    slow: "600ms cubic-bezier(0.4, 0, 0.2, 1)",
  },

  // ── Motion Token System (from design spec) ──
  motion: {
    // Named easing curves
    easeStandard: "cubic-bezier(0.4, 0, 0.2, 1)",   // UI transitions
    easeEnter: "cubic-bezier(0, 0, 0.2, 1)",         // Elements entering viewport
    easeExit: "cubic-bezier(0.4, 0, 1, 1)",          // Elements leaving
    easeSpring: "cubic-bezier(0.34, 1.56, 0.64, 1)", // Bouncy interactions

    // Duration tokens
    durFast: "160ms",     // Hover states, button feedback
    durMedium: "320ms",   // Section transitions, card reveals
    durSlow: "600ms",     // Hero element entrance, full-section transitions
    durCrawl: "1200ms",   // Background parallax, ambient elements
  },

  // ── Typography Scale (from design spec) ──
  typography: {
    display:   { size: "72px", weight: 800, letterSpacing: "-0.03em", lineHeight: "1.05" },
    headline:  { size: "48px", weight: 700, letterSpacing: "-0.02em", lineHeight: "1.1" },
    title:     { size: "32px", weight: 600, letterSpacing: "-0.01em", lineHeight: "1.2" },
    subtitle:  { size: "24px", weight: 500, letterSpacing: "0",       lineHeight: "1.3" },
    body:      { size: "16px", weight: 400, letterSpacing: "0",       lineHeight: "1.6" },
    caption:   { size: "13px", weight: 400, letterSpacing: "0.01em",  lineHeight: "1.5" },
    label:     { size: "11px", weight: 600, letterSpacing: "0.06em",  lineHeight: "1.4" }, // uppercase only
  },

  layout: {
    sidebarWidth: "260px",
    sidebarCollapsed: "72px",
    topNavHeight: "60px",
    maxContent: "1280px",
    rightSidebar: "320px",
  },

  // ── 8px-Based Spacing Scale ──
  space: {
    1: "8px",
    2: "16px",
    3: "24px",
    4: "32px",
    6: "48px",
    8: "64px",
    12: "96px",
    16: "128px",
  },

  zIndex: {
    sidebar: 40,
    topnav: 50,
    modal: 60,
    overlay: 55,
    toast: 70,
    tooltip: 80,
  },
} as const;

// Animation presets for framer-motion
export const animations = {
  fadeInUp: {
    initial: { opacity: 0, y: 40 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, ease: "easeOut" },
  },
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.4 },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    transition: { duration: 0.3, ease: "easeOut" },
  },
  slideInRight: {
    initial: { opacity: 0, x: 40 },
    animate: { opacity: 1, x: 0 },
    transition: { duration: 0.4, ease: "easeOut" },
  },
  staggerContainer: {
    animate: { transition: { staggerChildren: 0.08 } },
  },
  staggerItem: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4, ease: "easeOut" },
  },
  springHover: {
    whileHover: { scale: 1.02, y: -4 },
    transition: { type: "spring", stiffness: 400, damping: 17 },
  },
  modalEnter: {
    initial: { opacity: 0, scale: 0.95, y: 20 },
    animate: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.95, y: 20 },
    transition: { type: "spring", bounce: 0.3 },
  },
} as const;
