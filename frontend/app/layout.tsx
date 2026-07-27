import "../styles/globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import { ToastProvider } from "./components/feedback/ToastContext";

export const metadata: Metadata = {
  title: "NEXUS — Autonomous Data Intelligence Platform",
  description:
    "Enterprise-grade supply chain intelligence with Causal Genome, multi-source connectors, and AI autonomy.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
