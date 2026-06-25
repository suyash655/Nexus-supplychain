# SynChain 2.0 — Data Ingestion & ML Pipeline Critique
## Technical Review: Column Mapping, Prediction Pipeline, and Validation Claims

---

## Part 1 — Column Auto-Mapper: Real-World Failure Modes

### How the current mapper works

The mapper uses three passes: (1) exact match against high-confidence synonyms,
(2) exact match against low-confidence synonyms (blocks ingestion and requires
user confirmation), (3) token-overlap fuzzy match against high-confidence only.
Ambiguous matches below the 0.8 confidence threshold are blocked.

This is better than the original version, but the synonym list is still a static
lookup table built from one developer's mental model of supply chain data.
Real enterprise data breaks it in at least 10 structural ways.

---

### Failure modes in real-world supply chain data

**F1 — ERP column names are internal codes, not English words**

SAP MM exports use field names from the data dictionary: `LIFNR` (vendor),
`MATNR` (material/SKU), `LGORT` (storage location / warehouse), `REGIO`
(region), `BEDAT` (order date), `EINDT` (delivery date), `NETWR` (cost).
None of these match any synonym in the current table. The mapper returns
zero mappings. The upload succeeds with every field null.

Oracle TMS exports use: `CarrierCode`, `Pro#`, `OrigZip`, `DestZip`,
`TransitDays`, `FreightCharge`. `TransitDays` is close to `delay_days`
but `FreightCharge` does not match `cost` at all.

See: `data/adversarial_tests/01_sap_erp_export.csv`

**F2 — 3PL exports use logistics vocabulary, not procurement vocabulary**

3PLs describe movement, not sourcing. Their columns are things like
`carrier_id`, `origin`, `destination`, `reference` (BOL number),
`transit_days`, `freight_cost`, `condition_score`.
`origin` → `region`? Maybe. `carrier_id` → `supplier`? Arguably.
`condition_score` → `quality_score`? Plausible but risky.
The token overlap pass will produce low-confidence guesses on all of these.
A user who clicks "confirm" without reading will corrupt supplier identity.

See: `data/adversarial_tests/07_3pl_column_collision.csv`

**F3 — Customs declaration files have no supply chain field names at all**

UK CHIEF / CDS exports contain: `Declaration No`, `Declarant`, `HS Code`,
`Country of Origin`, `Port of Loading`, `Port of Discharge`, `MRN`,
`Date of Acceptance`, `Release Date`, `CIF Value (USD)`.
`Declarant` could be supplier. `CIF Value` could be cost.
`Country of Origin` could be region. But `Date of Acceptance` is not
an order date — it is the customs acceptance date, which can be weeks
after the order was placed. Mapping it to `order_date` corrupts all
time-series analysis.

See: `data/adversarial_tests/03_customs_declaration.csv`

**F4 — Mixed date formats in one file**

When a company merges data from multiple systems, each ERP writes dates
differently: `15/01/2024` (UK), `2024-01-16` (ISO), `Jan 17 2024` (US
long form), `01-18-2024` (US short), `20240119` (SAP compact).
`pd.to_datetime(..., errors="coerce")` handles most of these but silently
drops the ones it cannot parse (`errors="coerce"` → NaT). A file with
30% unparseable dates produces a time series with 30% missing periods,
making Holt-Winters forecasts meaningless. The user sees no error.

See: `data/adversarial_tests/04_mixed_date_formats.csv`

**F5 — Cost values are locale-formatted strings with currency symbols**

German formatting uses `.` as thousands separator and `,` as decimal:
`3.200,50` means 3200.50. Brazilian Real uses `R$ 2.100,25`. Indian
Rupee uses lakh notation: `₹4,30,000.00` = 430,000. A US-centric parser
reads `3.200,50` as 3.2 (truncating at the comma), and `¥1,200,750` as
NaN (currency symbol). `_safe_float()` returns 0.0 on failure. Every cost
for non-USD suppliers silently becomes 0, making cost-based risk scoring
and Monte Carlo simulations entirely wrong for international data.

See: `data/adversarial_tests/06_cost_format_ambiguity.csv`

**F6 — Unicode column headers (non-Latin ERPs)**

Chinese ERPs export column headers in Chinese: `供应商` (supplier),
`物料编号` (material number / SKU), `仓库` (warehouse), `费用` (cost).
German exports have umlauts: `Müller GmbH` as supplier name, `Prüflos`
as quality score column. Arabic and Russian are also common in MENA and
Eastern European supply chains. The normaliser (`c.lower().strip()`) does
not strip CJK or Arabic characters, and none of them appear in the synonym
tables. Zero mappings. Zero data.

See: `data/adversarial_tests/05_unicode_and_encoding.csv`

**F7 — No supply-chain columns exist at all (invoice/finance exports)**

Finance teams often export accounts-payable data as a proxy for supply
chain data: `transaction_id`, `company_name`, `product_description`,
`invoice_date`, `invoice_amount`, `payment_terms`, `country`.
`company_name` → `supplier` (low confidence). `invoice_date` → `order_date`
(low confidence). `invoice_amount` → `cost` (low confidence). But
`payment_terms`, `product_description`, and `country` map to nothing.
Critically, `delay_days` does not exist at all. The system ingests the
data with zero delay information, then reports 0% delayed shipments —
a falsely clean picture.

See: `data/adversarial_tests/08_missing_critical_columns.csv`

**F8 — Statistical edge cases that break ML assumptions**

A single row with `delay_days=999, cost=99999999` will dominate Z-score
normalisation across the entire dataset — every other row looks normal
next to it. Negative `delay_days` (-1) is physically impossible but
occurs in data from systems that record estimated delivery as future dates.
`delivery_date < order_date` produces negative implied delay. `cost=inf`
or `cost=nan` pass through `_safe_float()` correctly as 0.0, but silently
remove the economic signal for those rows. Isolation Forest trained on a
dataset with one extreme outlier will mark it anomalous and declare
everything else normal — defeating the purpose.

See: `data/adversarial_tests/09_statistical_edge_cases.csv`

**F9 — Single supplier dominance collapses risk scoring**

If 90% of rows are from one supplier (`MegaSupplier_X`), the global
normalisation in `RiskScorer` treats that supplier's delay distribution
as the baseline. All other suppliers are scored relative to MegaSupplier_X.
`global_max_delay = df["delay_days"].max()` — if MegaSupplier_X has delays
of 8 days, a tiny supplier with 1-day delays scores near-zero risk even
if its quality is poor. Single-supplier datasets also cause Isolation Forest
to find no meaningful cluster structure, producing arbitrary anomaly labels.

See: `data/adversarial_tests/10_single_supplier_dominance.csv`

**F10 — Same column name, completely different semantics**

`reference` in a 3PL context = Bill of Lading number (maps to `shipment_id`).
`reference` in an ERP context = internal accounting reference (maps to nothing useful).
`origin` in a shipping context = pickup city (not a supply region).
`origin` in a procurement context = country of manufacture (correct for `region`).
`transit_days` = carrier transit time (not the same as `delay_days`, which is
transit time minus promised lead time).
The mapper cannot distinguish these without knowing the file's provenance.

---

### 10 adversarial CSV files to use as tests

| File | What it breaks |
|---|---|
| `01_sap_erp_export.csv` | All-code SAP column names — zero mappings |
| `02_oracle_tms_export.csv` | Oracle TMS fields — carrier vocab, no supplier |
| `03_customs_declaration.csv` | UK customs export — wrong date semantics |
| `04_mixed_date_formats.csv` | 8 different date formats in one file |
| `05_unicode_and_encoding.csv` | Chinese, Arabic, Russian, German umlaut headers |
| `06_cost_format_ambiguity.csv` | 8 locale cost formats — EUR, JPY, INR, BRL |
| `07_3pl_column_collision.csv` | 3PL freight columns — semantic collision with supply fields |
| `08_missing_critical_columns.csv` | Finance/AP export — no delay_days at all |
| `09_statistical_edge_cases.csv` | Extreme outliers, negatives, inf, NaT, delivery < order |
| `10_single_supplier_dominance.csv` | 90% one supplier — breaks global normalisation |

---

### Improved ingestion strategy

The current two-tier synonym approach is a good start but insufficient
on its own. A robust strategy needs four additional layers:

**Layer 1 — Schema fingerprinting before synonym matching**

Before attempting column mapping, compute a "schema fingerprint" for the
uploaded file: the set of column names, their data types, and the
distribution of values. Compare against a library of known schema
fingerprints: SAP MM, Oracle TMS, UK HMRC customs, Shopify, NetSuite, etc.
If the fingerprint matches a known schema, apply that schema's pre-built
mapping directly rather than going through synonym matching.

```python
KNOWN_SCHEMAS = {
    "sap_mm": {
        "LIFNR": "supplier", "MATNR": "sku", "LGORT": "warehouse",
        "REGIO": "region", "EBELN": "shipment_id", "BEDAT": "order_date",
        "EINDT": "delivery_date", "NETWR": "cost", "MENGE": "quantity",
        "MATKL": "category", "PRÜFLOS": "quality_score",
    },
    "oracle_tms": { ... },
    "uk_customs": { ... },
}
```

**Layer 2 — Value-based type inference alongside name matching**

Examine the actual data in each column to narrow down its identity:
- A column with values like `4500012345`, `4500012346` → looks like PO numbers → `shipment_id`
- A column with values like `0.3` to `100.0` with no negatives → likely a score → `quality_score`
- A column where 30% of rows contain the string `"DE"`, `"FR"`, `"CN"` → country codes → `region`
- A column with values that parse as dates in 95%+ of rows → date field

This is independent of the column name and catches SAP/Oracle code-name columns.

**Layer 3 — Structured confidence reporting, always shown to the user**

The current system blocks on low-confidence mappings. The better approach:
always show the confidence table on the preview screen, even for
high-confidence mappings. Include the first 3 sample values from each
mapped column so the user can visually verify. A human can confirm in
10 seconds that `LIFNR = [1000123, 1000124, 1000125]` is indeed a supplier
code list — no algorithm can do this reliably.

**Layer 4 — Post-ingestion value validation with rejection reasons**

After mapping is confirmed, validate the values before inserting:
- `delay_days` must be numeric and ≥ -7 (allow minor timezone drift). Reject negatives.
- `cost` must be numeric and > 0. Flag zeros. Reject negatives.
- `order_date` must parse to a valid date. Reject NaT.
- `delivery_date` must be ≥ `order_date`. Flag inversions (do not silently fix).
- `quality_score` must be in [0, 100]. Clamp with a warning.

Return a per-column validation report with the API response:
```json
{
  "column_validation": {
    "delay_days": {"valid": 4850, "invalid": 12, "invalid_reason": "negative values"},
    "cost": {"valid": 4860, "invalid": 2, "invalid_reason": "zero or non-numeric"}
  }
}
```

---

## Part 2 — ML Pipeline Critique

### Anomaly detection: Isolation Forest + Z-score + IQR

**What works:**
The three-method ensemble covers different anomaly geometries well.
Isolation Forest catches multivariate patterns (expensive AND late).
Z-score catches univariate spikes. IQR catches quality score drops.
The deduplication fix (Fix #5 in the codebase) ensures they are counted
correctly. This is solid for a first-pass anomaly layer.

**Methodological weaknesses:**

W1 — Contamination parameter is hardcoded at 0.1 (10% anomaly rate)
This means the model always labels exactly 10% of the data as anomalous,
regardless of the actual anomaly rate. In a clean dataset with 2% true
anomalies, it will flag 10% — 80% false positives. In a dataset from a
disrupted quarter (40% genuinely unusual), it will only flag 10% — missing
75% of the real anomalies. The contamination rate should be estimated from
the data or made configurable per-customer.

W2 — Isolation Forest is retrained from scratch on every upload
This means there is no baseline. An anomaly is only anomalous relative to
the current dataset. If a supplier's performance has been consistently
degrading for 6 months, the model trains on the degraded data and finds
nothing anomalous — it has normalised the degradation. You need a
*stable reference period* (e.g., first 90 days of data for each supplier)
against which new data is evaluated.

W3 — Z-score assumes normality; supply chain delays are not normal
Delay distributions are right-skewed and bounded at 0. Z-score on a
right-skewed distribution will over-flag high delays (which may just be
the heavy tail of a log-normal distribution) and under-flag early
deliveries. Use a log-normal Z-score or a non-parametric test
(Anderson-Darling) instead.

W4 — No temporal ordering — anomalies are detected across the entire
dataset without time context. A delay of 10 days in January may be normal
(Chinese New Year). The same delay in July is genuinely anomalous. The
detector does not know this.

**Modern alternatives:**
- ADTK (Anomaly Detection Toolkit) for time-series aware detection
- LSTM Autoencoder for sequence-level anomalies
- Prophet + residual Z-score (detects anomalies after removing trend/seasonality)
- HDBSCAN for density-based multivariate detection (handles non-convex clusters)

---

### Risk scoring with fixed weights

**What works:**
The 6-factor transparent model is genuinely useful. Customers can understand
and challenge it. The factors (delay frequency, severity, cost variance,
quality, volume reliability, consistency) cover the right dimensions.

**Methodological weaknesses:**

W1 — Weights are arbitrary constants (0.30, 0.20, 0.15, 0.15, 0.10, 0.10)
There is no empirical basis for these weights. They have not been fitted to
historical outcomes. A textile customer cares about lead time more than cost
variance; a pharmaceutical customer cares about quality more than anything
else. Fixed weights produce a score that is transparently wrong for most
customers.

W2 — The factors are not independent
`delay_frequency` and `delay_severity` are correlated. A supplier who delays
often also tends to delay badly. Including both with separate weights
double-counts the delay signal. Use PCA or factor analysis to identify
genuinely independent risk dimensions before weighting.

W3 — No confidence interval on the score
A supplier with 3 shipments gets the same score format as one with 3,000.
The 3-shipment score has massive variance — it could be anywhere from 10
to 90 with 95% confidence. The score should be presented with a confidence
interval based on sample size.

W4 — `volume_reliability` penalises small suppliers indiscriminately
`max(0, 50 - len(group))` gives a lower risk score to suppliers with ≥50
shipments. But a new supplier with 10 shipments and zero delays is not
riskier than an established supplier with 100 shipments and 30% delays.
Volume is a proxy for data confidence, not risk — it should adjust the
confidence interval, not the score itself.

**Modern alternatives:**
- Gradient Boosted Trees (XGBoost/LightGBM) trained on historical disruption outcomes
- Learned weight optimisation: use logistic regression on labelled outcomes (supplier failed: yes/no) to derive empirical weights
- Bayesian risk model: represent score as a Beta distribution posterior, updated with each new shipment

---

### Holt-Winters forecasting

**What works:**
The minimum data guards (Fix #6: require 8 months for HW, 4 for Holt's
linear) prevent the crash-on-short-data bug. The fallback chain is correct.

**Methodological weaknesses:**

W1 — Smoothing constants (α=0.3, β=0.1, γ=0.2) are hardcoded
These should be optimised by minimising mean squared error on a holdout
window. Hardcoded constants are only good if the time series happens to
have the same dynamics assumed. Supply chain delays can be highly
non-stationary (a port strike regime-changes the entire series).

W2 — Additive seasonality assumes constant seasonal amplitude
If delays are increasing over time, the seasonal spikes also increase.
Additive HW applies a fixed seasonal adjustment regardless of the level.
Multiplicative HW (`seasonal_periods` × level) is more appropriate for
supply chain data where disruptions scale with volume.

W3 — No prediction intervals are computed or returned
The API returns `predicted_value` with a `confidence` label ("high",
"medium", "low") but no numerical interval. A CFO making safety stock
decisions needs `p50 = 4.2 days, p90 = 7.1 days`, not `confidence: medium`.

W4 — Forecast is only on delay_days, not on cost or risk score trajectory
The three most actionable forecasts for a procurement manager are:
(1) will this supplier's risk score cross the "critical" threshold in the
next 90 days? (2) what is the P90 cost for the next quarter? (3) which
SKUs will be at risk of stockout given forecast delays? None of these are
currently computed.

**Modern alternatives:**
- Prophet (Facebook): handles multiple seasonalities, holidays, changepoints, returns confidence intervals automatically
- SARIMA with AIC-based parameter selection
- LightGBM on time-series features (lag features, rolling statistics) — outperforms classical methods on irregular supply chain data

---

### "Bayesian Causal Inference" (previously claimed)

This claim has been removed from the codebase (Fix #4). The engine now
correctly describes itself as structural risk propagation. For completeness:

True causal inference in supply chain would require:
- A domain-expert specified DAG (which variables cause which)
- The `dowhy` library for do-calculus interventions
- Historical data with natural experiments (e.g., a port strike that
  affected some suppliers but not others) to estimate counterfactual outcomes
- Identifiability analysis to confirm the causal effect is estimable from
  available data

This is a research-grade undertaking. It is not appropriate to claim it
from a BFS traversal of a dependency graph.

---

## Part 3 — Validating the "~94% Simulation Fidelity" and "2.5x Bottleneck Detection" Claims

### Why these claims cannot be defended as stated

"~94% simulation fidelity" requires:
1. A ground truth dataset — historical disruption events where you know what actually happened
2. A held-out time window — the model must not have seen the test period during training
3. A defined metric — fidelity to *what*? Delay magnitude? Stockout occurrence? Supplier failure?
4. A comparison baseline — 94% compared to what? Random guessing on supply chain disruptions
   achieves roughly 5-10% precision (most suppliers are fine most of the time), so even a
   naive "no disruptions predicted" model achieves ~90% accuracy on a class-imbalanced dataset.

"2.5x more latent bottlenecks" requires:
1. A comparison method — 2.5x more than what? Manual analysis? A simpler graph metric?
2. A ground truth for "latent bottleneck" — did the predicted bottlenecks actually fail?
3. A precision/recall breakdown — finding 2.5x more bottlenecks means nothing if 90% are false positives.

### How to build a proper evaluation harness

**Step 1 — Construct a labelled evaluation dataset**

Identify 3-5 historical disruption events in your customer's or sample data where
the outcome is known. Examples:
- A supplier that actually went out of business or had a major quality failure
- A warehouse that experienced a shutdown (fire, flood, strike)
- A region that experienced port congestion causing measurable delays

For each event, create a time-split:
- Training window: all data before the event (e.g., 6 months prior)
- Test window: the event period and 4 weeks after

**Step 2 — Define the prediction task precisely**

"Fidelity" is too vague. Define:
- Binary classification: did this supplier enter the "critical" tier within 30 days? (precision/recall/F1)
- Regression: how close was the forecast delay to actual delay? (MAE, RMSE, MAPE)
- Ranking: were the top-5 riskiest suppliers actually the ones that caused disruptions? (NDCG)

**Step 3 — Run offline evaluation**

```python
# Pseudocode for evaluation harness
for event in historical_disruption_events:
    train_df = data[data["date"] < event.disruption_start]
    test_df  = data[data["date"] >= event.disruption_start]

    # Train on historical window
    analyzer.full_analysis(train_df)

    # Get predictions
    predictions = risk_scorer.score_suppliers(train_df)

    # Compare against known outcome
    actual_failures = event.suppliers_that_failed
    predicted_high_risk = [s for s in predictions if s["risk_score"] > 70]

    precision = len(set(predicted_high_risk) & set(actual_failures)) / len(predicted_high_risk)
    recall    = len(set(predicted_high_risk) & set(actual_failures)) / len(actual_failures)
```

**Step 4 — Report honest metrics**

Replace "~94% simulation fidelity" with a precision/recall table:

| Metric | Value | Notes |
|---|---|---|
| Precision @ risk_score > 70 | 0.XX | Of suppliers flagged, % that actually disrupted |
| Recall @ risk_score > 70 | 0.XX | Of suppliers that disrupted, % that were flagged |
| F1 Score | 0.XX | Harmonic mean |
| MAE on delay forecast | X.X days | Mean absolute error vs actual delays |
| Lead time before disruption | X days | How early did the system flag the issue? |

This is a story you can tell to an enterprise buyer with integrity. A "94% fidelity"
claim with no ground truth comparison is one question from being destroyed in a
technical due diligence.

**Step 5 — Continuous evaluation in production**

Once live, log every prediction with a timestamp. 30 days later, check if the
predicted high-risk suppliers actually had delays or failures. Compute rolling
precision/recall on a 90-day window. Surface this on a model performance
dashboard. This turns "we claim 94% fidelity" into "our current rolling precision
is 71% and improving."

---

## Summary: What to fix now vs later

| Priority | Item | Effort |
|---|---|---|
| Immediate | Add schema fingerprinting for SAP/Oracle/TMS known schemas | 2 days |
| Immediate | Add value-based type inference (parse values to infer column type) | 1 day |
| Immediate | Remove all unverified quantitative claims from marketing materials | 1 hour |
| Immediate | Add per-column post-ingestion validation with rejection reasons | 1 day |
| Short-term | Make Isolation Forest contamination configurable per customer | 2 hours |
| Short-term | Add reference period baseline for anomaly detection | 1 day |
| Short-term | Optimise HW smoothing constants via holdout MSE | 1 day |
| Short-term | Add prediction intervals to forecast output | 1 day |
| Medium-term | Build offline evaluation harness with labelled disruption events | 1 week |
| Medium-term | Replace fixed weights with learned weights from historical outcomes | 2 weeks |
| Long-term | Implement Prophet or LightGBM-based forecasting alongside HW | 1 week |
| Long-term | Add ADTK or LSTM autoencoder for temporal anomaly detection | 2 weeks |

---

*Document generated: June 2026*
*Based on code review of upload.py, analyzer.py, forecaster.py, monte_carlo.py*
*Adversarial test files: data/adversarial_tests/*
