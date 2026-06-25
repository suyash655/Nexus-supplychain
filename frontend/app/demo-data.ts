/**
 * NEXUS Demo Data — Fallback data when backend is unavailable.
 * Used to let users explore the dashboard without sign-in or backend.
 */

export const DEMO_SUMMARY = {
  total_records: 2847,
  unique_suppliers: 42,
  unique_skus: 156,
  unique_regions: 8,
  unique_warehouses: 12,
  avg_delay_days: 4.7,
  max_delay_days: 21,
  total_cost: 4892500,
  delayed_shipments_pct: 34.2,
  median_delay: 3.0,
  avg_quality: 87.3,
};

export const DEMO_SUPPLIERS = [
  { supplier: "Apex Materials", risk_score: 82, tier: "critical", total_shipments: 187, avg_delay: 8.3, max_delay: 21, total_cost: 892000, reliability_score: 42 },
  { supplier: "GlobalTech Co", risk_score: 76, tier: "critical", total_shipments: 142, avg_delay: 6.9, max_delay: 18, total_cost: 654000, reliability_score: 51 },
  { supplier: "SteelMax Inc", risk_score: 68, tier: "elevated", total_shipments: 98, avg_delay: 5.2, max_delay: 14, total_cost: 521000, reliability_score: 58 },
  { supplier: "ProLogix Asia", risk_score: 65, tier: "elevated", total_shipments: 221, avg_delay: 4.8, max_delay: 12, total_cost: 780000, reliability_score: 62 },
  { supplier: "NorthStar Parts", risk_score: 58, tier: "elevated", total_shipments: 167, avg_delay: 4.1, max_delay: 10, total_cost: 445000, reliability_score: 68 },
  { supplier: "Delta Logistics", risk_score: 45, tier: "stable", total_shipments: 312, avg_delay: 2.8, max_delay: 8, total_cost: 356000, reliability_score: 78 },
  { supplier: "OceanBridge Ltd", risk_score: 38, tier: "stable", total_shipments: 89, avg_delay: 2.1, max_delay: 6, total_cost: 234000, reliability_score: 84 },
  { supplier: "QuickShip Pro", risk_score: 22, tier: "stable", total_shipments: 445, avg_delay: 1.2, max_delay: 4, total_cost: 178000, reliability_score: 91 },
  { supplier: "EcoSupply Grp", risk_score: 31, tier: "stable", total_shipments: 198, avg_delay: 1.8, max_delay: 5, total_cost: 289000, reliability_score: 86 },
  { supplier: "PreciseParts", risk_score: 52, tier: "elevated", total_shipments: 134, avg_delay: 3.6, max_delay: 9, total_cost: 412000, reliability_score: 71 },
];

export const DEMO_EXECUTIVE = {
  overall_risk_level: "ELEVATED",
  risk_color: "#f59e0b",
  narrative: "**Supply chain risk is currently ELEVATED.** 2 of 10 tracked suppliers are in the critical tier, with Apex Materials showing a concerning 82/100 risk score driven by persistent delays averaging 8.3 days. The network shows moderate resilience but has single-point-of-failure vulnerabilities in the Asia-Pacific corridor.\n\nKey concern: **Apex Materials** and **GlobalTech Co** together account for 38% of total shipments but carry risk scores above 75. Diversification is urgently recommended.",
  recommendations: [
    { priority: "critical", action: "Diversify away from Apex Materials", detail: "Apex Materials has sustained 8+ day delays. Identify 2-3 alternative suppliers in the same material category to reduce concentration risk.", estimated_impact: "Risk reduction: 15-20%" },
    { priority: "high", action: "Audit GlobalTech Co quality metrics", detail: "GlobalTech's reliability has declined 12% month-over-month. Schedule quality audit and establish SLAs with penalty clauses.", estimated_impact: "Quality improvement: 8-15%" },
    { priority: "medium", action: "Increase safety stock for high-risk SKUs", detail: "23 SKUs sourced exclusively from critical-tier suppliers. Increase buffer inventory by 2 weeks to mitigate disruption impact.", estimated_impact: "Disruption buffer: +14 days" },
    { priority: "medium", action: "Negotiate dual-sourcing for critical components", detail: "Establish backup contracts with stable-tier suppliers for the top 10 critical SKUs.", estimated_impact: "Supply continuity: +25%" },
  ],
  key_metrics: { avg_risk: 53.7, critical_count: 2, elevated_count: 3 },
};

export const DEMO_ANOMALIES = {
  anomaly_count: 23,
  methods_used: ["Isolation Forest", "Z-Score", "IQR"],
  anomalies: [
    { type: "delay_spike", severity: "high", supplier: "Apex Materials", risk_score: 82 },
    { type: "cost_anomaly", severity: "medium", supplier: "GlobalTech Co", risk_score: 76 },
    { type: "quality_dip", severity: "high", supplier: "SteelMax Inc", risk_score: 68 },
  ],
};

export const DEMO_TIME_SERIES = {
  delay_trend: [
    { period: "Jan", avg_delay: 3.2 }, { period: "Feb", avg_delay: 3.8 },
    { period: "Mar", avg_delay: 4.1 }, { period: "Apr", avg_delay: 5.2 },
    { period: "May", avg_delay: 4.7 }, { period: "Jun", avg_delay: 4.9 },
    { period: "Jul", avg_delay: 5.8 }, { period: "Aug", avg_delay: 4.3 },
    { period: "Sep", avg_delay: 3.9 }, { period: "Oct", avg_delay: 4.7 },
  ],
  cost_trend: [
    { period: "Jan", total_cost: 380000 }, { period: "Feb", total_cost: 420000 },
    { period: "Mar", total_cost: 465000 }, { period: "Apr", total_cost: 510000 },
    { period: "May", total_cost: 489000 }, { period: "Jun", total_cost: 502000 },
    { period: "Jul", total_cost: 548000 }, { period: "Aug", total_cost: 475000 },
    { period: "Sep", total_cost: 445000 }, { period: "Oct", total_cost: 489250 },
  ],
};

export const DEMO_BULLWHIP = {
  bullwhip_ratio: "1.42",
  status: "moderate",
  interpretation: "Moderate demand amplification detected across the supply chain.",
};

export const DEMO_RESILIENCE = {
  network_resilience_score: 67,
  structural_robustness: "Medium",
  critical_nodes: ["Apex Materials", "GlobalTech Co"],
};

export const DEMO_WORLD_EVENTS: any[] = [
  { id: 1, title: "Red Sea Shipping Crisis", description: "Houthi attacks force rerouting through Cape of Good Hope, adding 10-14 days transit.", severity: "CRITICAL", region: "Middle East", impact_score: 8.5, status: "active" },
  { id: 2, title: "Taiwan Strait Tensions", description: "Increased military activity raising insurance premiums for Asia-Pacific routes.", severity: "HIGH", region: "Asia-Pacific", impact_score: 7.2, status: "monitoring" },
  { id: 3, title: "EU CBAM Phase-In", description: "Carbon border adjustment mechanism increasing compliance costs for imported goods.", severity: "MEDIUM", region: "Europe", impact_score: 5.8, status: "active" },
];

export const DEMO_WORLD_IMPACT = {
  impact_summary: "Red Sea crisis is projected to increase lead times by 12-18% for 3 of your critical suppliers routing through the Suez Canal. Estimated cost impact: ₹1.2M over next quarter.",
  disrupted_suppliers: [
    { id: "Apex Materials", reason: "Primary route via Suez Canal", risk_increment: 12 },
    { id: "ProLogix Asia", reason: "Secondary shipments through Red Sea", risk_increment: 8 },
    { id: "GlobalTech Co", reason: "Component sourcing from affected region", risk_increment: 6 },
    { id: "SteelMax Inc", reason: "Raw material transit delays", risk_increment: 4 },
  ],
};
