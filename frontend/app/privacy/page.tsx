import React from "react";
import Link from "next/link";
import { ArrowLeft, Lock, Shield, EyeOff } from "lucide-react";

export const metadata = {
  title: "Privacy Policy — NEXUS Risk Intelligence",
  description: "Enterprise privacy policy and data governance practices for NEXUS Supply Chain Risk Intelligence.",
};

export default function PrivacyPage() {
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
            <Shield className="w-5 h-5 text-[#8fa2bc]" />
            <span className="text-[12px] font-mono tracking-wider uppercase">Privacy & Data Governance Charter</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-light tracking-tight text-[#f7f4ec] mb-3">
            Enterprise Privacy Policy
          </h1>
          <p className="text-[13px] text-[#6b7f99] font-light mb-8">
            Last Updated: January 15, 2026 · Confidential & Proprietary
          </p>

          <div className="space-y-8 text-[14px] text-[#9eb0c7] font-light leading-relaxed">
            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">1. Principle of Zero Data Retention for Ad-Hoc Sessions</h2>
              <p>
                When utilizing demo sessions or ephemeral analytical workspaces, uploaded CSV files are sanitized, processed
                in transient in-memory tables, and permanently purged upon session termination or manual reset. We do not
                resell, train public models upon, or cross-pollinate customer supply chain topologies.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">2. Untrusted CSV Prompt Sanitization</h2>
              <p>
                Prior to any string injection into language model context buffers, all textual inputs undergo automated regex
                and structural sanitization. Characters matching formula injection vectors (<code className="text-[#cbd7e6] bg-[#121b2b] px-1 py-0.5 rounded text-[12px]">=, @, +, -</code>),
                SQL delimiters, or instruction breakout sequences are strictly stripped and encapsulated in <code className="text-[#cbd7e6] bg-[#121b2b] px-1 py-0.5 rounded text-[12px]">&lt;UNTRUSTED_DATA&gt;</code> tags.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">3. Role-Based Access Control (RBAC) & Encryption</h2>
              <p>
                All data at rest is encrypted with AES-256 GCM. Data in transit across REST and WebSocket channels requires TLS 1.3.
                Access to operational risk mitigation endpoints requires cryptographically signed JWT tokens adhering to rotating
                refresh token architecture, preventing unauthorized session hijacking.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">4. On-Premises & Air-Gapped Compliance</h2>
              <p>
                For aerospace, defense, and healthcare supply chains requiring air-gapped isolation, NEXUS operates entirely
                disconnected from the public Internet. Vector similarity indexing runs over local ChromaDB instances without
                calling remote embedding endpoints.
              </p>
            </section>

            <section className="border-t border-[#172336] pt-6">
              <h2 className="text-base font-normal text-[#f7f4ec] mb-2">5. Compliance & Subject Access Rights</h2>
              <p>
                Enterprise customers retain full rights to export complete data snapshots, request automated database purges,
                and retrieve cryptographic audit traces. For data protection inquiries or Data Processing Addendum (DPA) execution,
                contact our security team at <span className="text-[#cbd7e6]">privacy@nexus-supplychain.io</span>.
              </p>
            </section>
          </div>

          <div className="mt-12 pt-6 border-t border-[#172336] flex flex-wrap items-center justify-between text-[12px] text-[#5e7290]">
            <span>NEXUS Data Protection & Governance Directorate</span>
            <span>ISO/IEC 27001 & SOC 2 Type II Architecture Alignment</span>
          </div>
        </div>
      </div>
    </div>
  );
}
