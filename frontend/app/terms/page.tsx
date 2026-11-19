import React from "react";
import Link from "next/link";
import { ArrowLeft, ShieldCheck, Lock, FileText } from "lucide-react";

export const metadata = {
  title: "Terms of Service — NEXUS Risk Intelligence",
  description: "Enterprise Terms of Service and data governance terms for the NEXUS Supply Chain Risk Intelligence Platform.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#060a12] text-[#f7f4ec] py-12 px-6 sm:px-12 selection:bg-[#253654] selection:text-white">
      <div className="max-w-4xl mx-auto">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-[13px] text-[#7e94b0] hover:text-[#f7f4ec] transition-colors mb-10 group"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" />
          <span>Back to Platform</span>
        </Link>

        <div className="border border-[#1b273d]/80 bg-[#0a101d]/90 rounded-2xl p-8 sm:p-12 shadow-2xl relative overflow-hidden">
          <div className="flex items-center gap-3 text-[#7e94b0] mb-4">
            <FileText className="w-5 h-5 text-[#8fa2bc]" />
            <span className="text-[12px] font-mono tracking-wider uppercase">Legal & Compliance Documentation</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-light tracking-tight text-[#f7f4ec] mb-3">
            Terms of Service
          </h1>
          <p className="text-[13px] text-[#6b7f99] font-light mb-8">
            Effective Date: January 15, 2026 · Version 2.4 Enterprise
          </p>

          <div className="space-y-8 text-[14px] text-[#9eb0c7] font-light leading-relaxed">
            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">1. Acceptance of Terms</h2>
              <p>
                By accessing, uploading data to, or executing mitigation operations within the NEXUS Supply Chain Risk
                Intelligence Platform (&quot;Platform&quot;), your organization (&quot;Customer&quot;) agrees to be bound by these
                Terms of Service. If you are entering into this agreement on behalf of a corporation or legal entity,
                you represent that you possess the authority to bind such entity.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">2. Data Sovereignty & Customer Data Ownership</h2>
              <p>
                Customer retains sole and exclusive ownership, rights, and title to all structured data, CSV uploads,
                ERP synchronization records, and supplier topology graphs submitted to the Platform. NEXUS does not
                claim intellectual property over any proprietary supplier networks, pricing agreements, or inventory records.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">3. Local & Offline AI Guarantee</h2>
              <p>
                All statistical inference (including Isolation Forest anomaly detection, Holt-Winters time-series forecasting,
                and NetworkX graph cascade simulations) executes strictly in-process on designated customer instances.
                When configured in offline mode (<code className="text-[#cbd7e6] bg-[#121b2b] px-1.5 py-0.5 rounded text-[12px]">LLM_PROVIDER=offline</code>),
                zero telemetry, transaction records, or supplier names are transmitted to external third-party foundation model APIs.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">4. Human-in-the-Loop Approval Safeguards</h2>
              <p>
                The Platform&apos;s mitigation agent operates under mandatory human-in-the-loop governance. Autonomous rerouting,
                purchase order reallocation, or supplier escalation orders remain staged in pending status until explicitly
                confirmed by an authorized user holding Manager or Admin role credentials via cryptographic session authorization.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">5. Service Availability & Audit Trail</h2>
              <p>
                Enterprise deployments feature an immutable audit logging service tracking every risk scoring calculation,
                counterfactual parameter modification, and agent decision trace. System availability targets 99.9% uptime
                for containerized deployments across supported private cloud or on-premise Kubernetes environments.
              </p>
            </section>
          </div>

          <div className="mt-12 pt-6 border-t border-[#172336] flex flex-wrap items-center justify-between text-[12px] text-[#5e7290]">
            <span>NEXUS Risk Intelligence Platform · Enterprise Edition</span>
            <span>Inquiries: compliance@nexus-supplychain.io</span>
          </div>
        </div>
      </div>
    </div>
  );
}
