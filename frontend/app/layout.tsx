import "../styles/globals.css";
import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import type { CSSProperties, ReactNode } from "react";
import { ToastProvider } from "./components/feedback/ToastContext";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500", "600"],
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: {
    default: "NEXUS — Autonomous Data Intelligence Platform",
    template: "%s · NEXUS",
  },
  description:
    "Supply chain intelligence with risk propagation, multi-source connectors, and offline-safe AI workflows.",
};

export const viewport: Viewport = {
  themeColor: "#060a12",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  /* next/font generates the real font-family strings. Feeding them into the
     CSS variables means globals.css picks them up with no further edits. */
  const fontVars = {
    "--font-sans": inter.style.fontFamily,
    "--font-mono": mono.style.fontFamily,
  } as CSSProperties;

  return (
    <html lang="en" data-theme="dark" style={fontVars} suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}