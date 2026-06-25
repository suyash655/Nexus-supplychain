# Supply Chain Command Center (Dashboard) — Complete Guide

## Overview

The **Supply Chain Command Center** is the main dashboard of SynChain 2.0. It provides a unified, real-time view of your entire supply chain's health, risks, and operational metrics. Think of it as the "mission control" for supply chain managers.

**URL**: `http://localhost:3000/dashboard` (or click "Command Center" in the sidebar)

---

## Dashboard Components (Top to Bottom)

### 1. **Header Section**
```
Supply Chain Command Center
Real-time intelligence across your supply chain network
```
- **Title**: Indicates you're in the main intelligence hub
- **Subtitle**: Reminds you this is live, real-time data (unless in demo mode)

---

### 2. **Demo Mode Banner** (Shows when backend is offline)
```
🎯 Demo Mode — Sample Data
You're viewing demo analytics. Start the backend or upload your own data for real insights.
[Upload Data →]
```

**When you see this:**
- Backend server is not running
- System is showing sample/demo data
- Click "Upload Data" to add your own CSV/Excel file
- Or start the backend with: `.\start-backend.ps1`

---

### 3. **Executive Risk Banner**
```
⚠️ Overall Risk Level: [HIGH/CRITICAL/MEDIUM/LOW]
[Natural language narrative about current supply chain health]
```

**What it shows:**
- Single, most important finding about your supply chain
- Color-coded by severity (red = critical, orange = high, yellow = medium, green = low)
- AI-generated summary of the main risk driver
- Updated automatically after data analysis

**Example:**
```
Overall Risk Level: CRITICAL

Your supply chain faces elevated disruption risk due to:
- 3 suppliers in the critical risk tier (70+ risk score)
- Southeast Asia region showing increasing volatility
- 12% delayed shipments in the last 30 days
```

---

### 4. **Global Intelligence Pulse** (Two-part card)

#### **Left Side: Active Disruptions**
Shows real-time global events that might impact your supply chain:

```
Active Disruptions:
- Port Strike in Singapore | CRITICAL
  Long-haul vessels delayed; expect 5-7 day impact
  
- Cyclone Warning - Bay of Bengal | HIGH
  Shipping routes diverted; estimated 2-3% cost increase
  
- Chip Shortage Update | MEDIUM
  Inventory shortages continue; allocate 15% buffer
```

**What each event shows:**
- Event title
- Severity level (CRITICAL / HIGH / MEDIUM)
- Brief description of impact
- Affects your risk calculations automatically

#### **Right Side: Supplier Ripple Analysis**
Shows which of YOUR suppliers are affected by the global events:

```
"Singapore Port strike will disrupt 12% of incoming shipments, 
primarily electronics and textiles destined for North America."

Affected Suppliers:
- China_Electronics +8% risk elevation
- Vietnam_Textiles +12% risk elevation
- India_Components +5% risk elevation
- Japan_Precision +3% risk elevation
```

**What it means:**
- Which suppliers are in the affected regions
- How much their risk scores have increased
- Proactive warning before disruption hits

---

### 5. **Digital Twin Stress Test** (Interactive Simulation)

This is your **"what-if" simulator** for supply chain failures.

#### **Left Side: Simulation Controls**
```
Select multiple nodes to simulate simultaneous failure and 
assess global network fragility.

[Supplier_A] [Supplier_B] [Supplier_C] [Warehouse_1]
[Warehouse_2] [SKU_Premium] [Region_NA] [Region_EU]

[Simulate 3 Node Failure]
```

**How to use it:**
1. Click supplier/warehouse names to select them (they turn yellow)
2. Click "Simulate N Node Failure" to run the scenario
3. System calculates what happens if those nodes fail simultaneously

#### **Right Side: Impact Assessment**
```
Impact Assessment: SEVERE

Total Affected Nodes: 47
Recovery Complexity: EXTREME

Primary Affected Downstream:
- SKU_A, SKU_B, SKU_C, Warehouse_Singapore, Region_NA +27 more
```

**What each metric means:**
- **Total Affected Nodes**: How many products/warehouses/regions lose supply if selected node(s) fail
- **Recovery Complexity**: Time/cost to restore operations (Low < Medium < High < Extreme)
- **Risk Assessment**: Overall impact (Low, Medium, High, Critical, Catastrophic)
- **Downstream Cascade**: Which items would be affected directly

---

### 6. **Shadow Tier Reveal** (Advanced Feature)

```
👁️ Shadow Tier Reveal
PROPRIETARY INFERENCE

[REVEAL INVISIBLE TIERS]
```

**What it does:**
- Detects suppliers hidden deeper in your supply chain (Tier 3, 4, 5 suppliers)
- Uses alternative signals: news, logistics data, financial reports
- Shows suppliers you didn't know were in your network

**After clicking "REVEAL":**
```
China_Electronics_Tier3
Type: COMPONENT_SUPPLIER
Confidence: 87%
Inferred via: shared SKU co-occurrence with known Tier-1 suppliers
(two or more of your direct suppliers share this SKU — possible shared component)

Vietnam_Assembly_Sub
Type: ASSEMBLY_PARTNER
Confidence: 72%
Inferred via: shared SKU co-occurrence with known Tier-1 suppliers
```

> **How inference works**: The system identifies suppliers that share ≥2 SKUs
> with your direct (Tier 1) suppliers. This may indicate a shared component
> source — but it can also mean two suppliers are simply competing to supply
> the same product to you. The confidence score reflects SKU overlap strength,
> not external data sources. Treat these as leads to investigate, not confirmed
> sub-tier relationships.

---

### 7. **KPI Grid** (8 Key Metrics)

Eight card panels showing critical supply chain metrics:

| Metric | What It Shows | Example |
|--------|--------|---------|
| **Total Records** | Number of shipments/transactions uploaded | 1,247 |
| **Suppliers** | Count of unique suppliers in your network | 24 |
| **Avg Delay** | Average number of days shipments are late | 3.2d |
| **Anomalies** | Number of unusual transactions detected (deduplicated) | 156 |
| **Regions** | Count of destination regions | 8 |
| **Cost Impact** | Total shipment/logistics cost | ₹2,540K |
| **Resilience** | Network structural robustness (0-100%) | 68% |
| **Shipment Volatility** | Week-to-week shipment count variability (CV of weekly shipments). Higher = more erratic ordering cadence. Not the same as the academic Bullwhip Effect ratio, which requires two-tier order/demand data. | 0.42 |

**Color coding:**
- 🟡 Yellow/Orange = Accent (important but not critical)
- 🔴 Red = Danger (needs attention)
- 🟢 Green = Healthy/Good

---

### 8. **Charts Row** (Two visualizations)

#### **Left: Supplier Risk Scores (Bar Chart)**
```
Bar chart showing the 8 suppliers with highest risk scores

Supplier_A ████████████████░░░░ 78
Supplier_B ██████████████░░░░░░░ 72
Supplier_C ████████████░░░░░░░░░ 65
[... 5 more ...]
```

**What it shows:**
- 0-100 risk score for each supplier
- Bars colored by severity (red 70+, orange 40-70, green 0-40)
- Easy visual comparison across suppliers
- Click a bar to see more details about that supplier

#### **Right: Risk Distribution (Pie Chart)**
```
Risk Distribution
🔴 Critical: 3 suppliers
🟡 Elevated: 8 suppliers
🟢 Stable: 13 suppliers
```

**What it means:**
- Summary breakdown of your supplier base by risk tier
- Quick health check of portfolio diversification
- If too many in "Critical" = concentrated risk

---

### 9. **Time Series Charts** (Two trend lines)

#### **Left: Delay Trend (Area Chart)**
```
Timeline showing average delays over time
         
         ╱╲
    ╱╲  ╱  ╲
   ╱  ╲╱    ╲__
Week 1  Week 2  Week 3  Week 4

Current: 3.2 days
Trend: Improving (⬇️)
Forecast: 2.8 ± 0.5 days next week
```

**What it shows:**
- Are delays getting better or worse?
- Seasonal patterns (spikes in certain months)
- Forecast for next period
- Upload time-stamped data to see trends

#### **Right: Cost Trend (Area Chart)**
```
Timeline showing total costs over time

Shows whether costs are rising or stable
```

**What it shows:**
- Cost inflation/deflation pattern
- Identify expensive time periods
- Forecast future cost burden

---

### 10. **Supplier Risk Leaderboard** (Detailed Table)

Comprehensive table of all suppliers ranked by risk:

```
Supplier         Risk  Tier      Avg Delay  Shipments  Cost      Level
                 Score                                             
─────────────────────────────────────────────────────────────────────
China_Factory    78    Critical  8.2d       145        ₹2,340K   ████
Vietnam_Textil  72    Elevated  6.1d       203        ₹1,890K   ███░
Mexico_Steel    65    Elevated  4.3d       87         ₹956K     ██░░
India_Componen  58    Stable    2.1d       412        ₹4,210K   ██░░
Japan_Precision 42    Stable    1.5d       156        ₹2,100K   ██░░
... more rows ...
```

**Each column explained:**

| Column | Meaning |
|--------|---------|
| **Supplier** | Name/ID of supplier |
| **Risk Score** | 0-100 composite risk (higher = riskier) |
| **Tier** | Classification (Critical/Elevated/Stable) |
| **Avg Delay** | Average days late per transaction |
| **Shipments** | Number of transactions from this supplier |
| **Total Cost** | Total rupees spent with this supplier |
| **Risk Level** | Visual bar showing risk intensity |

**How to use:**
- **Sort by Risk Score** to find most dangerous suppliers
- **Filter by Tier** to see all "Critical" suppliers
- **Compare Costs vs. Risk** to find best suppliers to keep/cut
- **Analyze Shipment Volume** to identify key dependencies

---

### 11. **Supply Chain Lifecycle** (Interactive Timeline)

```
         Phase 1                Phase 2               Phase 3
      DATA INGESTION         RISK ANALYSIS         SIMULATION
         ✓ Completed          ✓ Completed          🔄 In Progress
         [Details...]         [Details...]         [Details...]
             │                    │                    │
             └────────────────────┴────────────────────┘
                                  │
                         Phase 4: INSIGHTS
                         ⏳ Pending
                         [Details...]
                         
                         Phase 5: OPTIMIZATION
                         ⏳ Pending
                         [Details...]
```

**Five phases of your supply chain analysis:**

1. **Data Ingestion** ✓
   - Your CSV/Excel data is uploaded
   - Schema auto-detected and validated
   - Raw records stored in database

2. **Risk Analysis** ✓
   - ML models compute risk scores for each supplier
   - Anomalies detected across 3 methods
   - Composite risk metrics calculated

3. **Simulation** 🔄
   - Digital Twin stress-tests failure scenarios
   - Cascade effects computed
   - Resilience score calculated

4. **Insights** ⏳ (Pending)
   - AI Copilot generates executive summary
   - Actionable recommendations created
   - Impact scores estimated

5. **Optimization** ⏳ (Pending)
   - Suggestions applied (shipper re-routing, supplier swaps)
   - Safety stock adjusted
   - Cycle repeats continuously

**Click any phase to expand and see details.**

---

### 12. **AI Recommendations Card**

```
AI Recommendations
─────────────────────────────────────────────────────────────

CRITICAL
Diversify Vietnam Supply
Reduce single-supplier dependency on VietnamTextileCorp
(Currently 40% of apparel sourcing; industry risk elevated with port strikes)
Est. impact: +8% resilience | [SIMULATE FIX]

HIGH
Activate Mexico Steel Backup
Mexico_Steel capacity increased 20%; reroute 15% volume from China
(Reduces China risk concentration; only adds 2% cost)
Est. impact: +12% resilience | [SIMULATE FIX]

HIGH
Pre-position Emergency Inventory
Add 2-week safety stock for SKU_A, SKU_B in Singapore
(Mitigates port strike cascades; costs ₹450K but prevents ₹2M loss)
Est. impact: +18% resilience | [SIMULATE FIX]

MEDIUM
Monitor Japan Components Geopolitical Risk
Japan tensions rising; adjust 10% hedging in contracts
(Low cost, high strategic value for political stability)
Est. impact: +3% resilience | [SIMULATE FIX]
```

**Each recommendation shows:**
- **Priority** (CRITICAL / HIGH / MEDIUM): How urgent
- **Action**: What to do
- **Detail**: Why it matters and what the constraint is
- **Estimated Impact**: How much resilience improves if applied
- **SIMULATE FIX Button**: Test the recommendation's effect before applying

---

## How to Read This Dashboard

### **Quick Assessment (30 seconds)**
1. Look at **Executive Risk Banner** — Is my supply chain in trouble?
2. Check **KPI Grid** → specifically **Anomalies** and **Resilience**
3. Scan **Global Intelligence Pulse** — Any active disruptions?

### **Detailed Analysis (5 minutes)**
1. Review **Supplier Risk Leaderboard** — Which suppliers are risky?
2. Examine **Risk Distribution Pie** — How concentrated is my risk?
3. Check **Delay/Cost Trends** — Are things improving or worsening?
4. Run **Digital Twin Stress Test** — What if my top 3 suppliers fail?

### **Strategic Planning (15 minutes)**
1. Read **AI Recommendations** — What should I do first?
2. Review **Supply Chain Lifecycle** — Where is my data in the pipeline?
3. Click **REVEAL Invisible Tiers** — Are there hidden sub-suppliers?
4. Analyze **Total Cost vs. Risk** — Am I paying for reliable suppliers?

---

## Common Scenarios & What to Look For

### Scenario 1: "Our supply chain is fragile"
**What to check:**
- Resilience score < 50%
- Shipment Volatility Index > 0.5 (very erratic ordering cadence)
- Bottleneck nodes in Digital Twin (high centrality)
- Few suppliers per SKU category

### Scenario 2: "We keep getting blindsided by delays"
**What to check:**
- High Anomalies count
- Avg Delay rising in trend charts
- Many suppliers in Critical tier
- Forecast showing 7+ day delays

### Scenario 3: "Our costs are spiraling"
**What to check:**
- Cost Trend going up
- High-cost suppliers also high-risk
- Shipment Volatility Index > 0.3 (erratic ordering pattern driving cost spikes)
- Regional cost variances (compare regions in leaderboard)

### Scenario 4: "A geopolitical event just occurred"
**What to check:**
1. Check **Global Intelligence Pulse** for related events
2. Identify affected suppliers in **Supplier Risk Leaderboard**
3. Run **Digital Twin Stress Test** on those suppliers
4. Review **AI Recommendations** for mitigation steps
5. Simulate applying recommended fixes

---

## Data Refresh & Updates

- **Real-time metrics**: KPI Grid, anomalies, risk scores update every 5 minutes
- **Batch updates**: Trends, forecasts, ML models refresh after you upload new data
- **Manual triggers**: Click "Run Analysis" button (if available) to force immediate refresh
- **Demo data**: Same demo always shown; upload real data to see your metrics

---

## Exporting & Reporting

From the Command Center:
1. Take screenshots for executive presentations
2. Export individual charts (right-click → download)
3. Use data in **Analytics** tab for deeper dives
4. Generate reports via **Export** page → select metrics and date range

---

## Next Steps from Command Center

**Want more detail?** Navigate to:
- **Analytics** tab → Detailed trend analysis
- **Graph** tab → Interactive network visualization
- **XAI** tab → Explainability of risk drivers
- **Copilot** tab → Ask questions in natural language
- **Pipeline** tab → Monitor data quality

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Demo Mode" always showing | Start backend: `.\start-backend.ps1` |
| Charts are empty | Upload data via `/upload` page |
| Metrics look wrong | Check data in Upload page for errors |
| Recommendations not shown | Backend must finish Risk Analysis phase |
| Trends not updating | Ensure timestamps in your data |

---

**Your Command Center is now ready to monitor, analyze, and optimize your supply chain!**
