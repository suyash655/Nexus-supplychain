Supex Project — Simple Test Plan

Purpose
- A simple, step-by-step checklist to test all important features after you upload data.
- Written in plain language so anyone can follow and verify results.

How to use this document
- Follow sections in order: Start servers → Upload → Check results → Test features.
- Use the quick commands shown next to each check.

1) Start the servers
- Backend (API): runs the upload, analysis, and analytics.
  - Command (PowerShell):
    & d:\supex1\.venv\Scripts\Activate.ps1
    python -m uvicorn app.main:app --reload --port 8000
  - Quick check: open http://127.0.0.1:8000/ in browser.

- Frontend (UI): shows dashboard and pages.
  - Command (PowerShell):
    npm --prefix "d:\supex1\frontend" run dev -- --hostname 0.0.0.0
  - Quick check: open http://localhost:3000/ in browser.

2) Preview a CSV (safe check before uploading)
- What it does: reads your CSV and suggests how columns map to system fields.
- Why: avoids wrong imports and many "Unknown Source" rows.
- Command:
  curl -X POST "http://127.0.0.1:8000/upload/preview" -F "file=@/path/to/your.csv"
- Look for: "flat_mapping", "preview_rows", and "requires_confirmation".

3) Register and login (get a token)
- Why: upload and many API calls need an authenticated user.
- Commands:
  curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"email":"you@example.com","username":"you","password":"Password123!","full_name":"You","role":"analyst"}'
  curl -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"Password123!"}'
- Save the `access_token` from the login response.

4) Upload the CSV
- What it does: inserts rows into the database and queues background analysis.
- Command (replace <ACCESS> and file path):
  curl -X POST "http://127.0.0.1:8000/upload" -H "Authorization: Bearer <ACCESS>" -F "file=@/path/to/your.csv"
- Look for in response:
  - rows_inserted: number of rows saved
  - rows_rejected: rows skipped
  - column_mapping: how columns matched
  - data_quality: missing values and validation
  - analysis_started: did the server queue the ML job?

5) Wait for analysis and check analytics
- Analysis may take ~30–120 seconds depending on data.
- Commands:
  curl -H "Authorization: Bearer <ACCESS>" http://127.0.0.1:8000/analytics/summary
  curl -H "Authorization: Bearer <ACCESS>" http://127.0.0.1:8000/analytics/suppliers
  curl -H "Authorization: Bearer <ACCESS>" http://127.0.0.1:8000/ml/full-analysis
- Look for: totals matching the upload, new suppliers present, and risk scores computed.

6) Frontend checks (make UI show real data)
- If UI shows demo data: open browser console and run:
  localStorage.removeItem("nexus_demo_mode")
  localStorage.setItem("nexus_has_real_data", "true")
  location.reload()
- Then open Dashboard and check the widgets (Total Records, Avg Delay, Supplier Leaderboard).

7) Feature-by-feature checks (Overview, Planning, Intelligence, Operations)
- Overview (Command Center / Dashboard):
  - What: high-level KPIs (records, suppliers, delays, anomalies)
  - Check: totals match `analytics/summary`; top suppliers match `analytics/suppliers`.

- Planning (S&OP, Unified IBP):
  - What: planning tools that use the analyzed data to suggest operational changes.
  - Check: open the Planning pages; ensure they load without errors and show supply counts.

- Intelligence (Analytics, Reports, Graph Network, AI Co-Pilot, Risk Propagation, Explainability):
  - Analytics: charts and KPIs reflect backend data.
  - Reports: export or view generated reports for summary numbers.
  - Graph Network: visual shows supplier nodes and links; search for suppliers added.
  - AI Co-Pilot: asks for a short query (e.g., "top risky suppliers") and returns a narrative.
  - Risk Propagation: run a scenario and verify it highlights impacted suppliers.
  - Explainability: pick a supplier and view factors that contributed to its score.

- Operations (Control Tower, Mitigation Loop, Agent Traces, Connectors, Pipeline, Export):
  - Control Tower: shows alerts and recent incidents — verify new alerts are generated for high-risk suppliers.
  - Mitigation Loop: check recommendations exist for top risks.
  - Agent Traces: view agent activity logs for analysis jobs.
  - Connectors: ensure connectors page shows available data sources.
  - Pipeline: inspect recent pipeline runs and statuses.
  - Export: attempt to export a small report and open it.

8) Tests to try (examples)
- Upload a small CSV with known delays to see risk increase for a test supplier.
- Upload a file missing the `supplier` header and see rows mapped to "Unknown Source".
- Intentionally corrupt one line (bad date) and confirm `rows_rejected` increments.
- Trigger `ml/refresh` manually and observe logs for analysis start/finish.

9) Logs and troubleshooting
- Backend logs (where uvicorn runs) show engine errors and analysis tracebacks.
- If UI shows stale values: clear localStorage and reload.
- If import fails with ModuleNotFoundError: make sure you start server from `backend` folder or set `PYTHONPATH`.

10) What to record in your testing notes
- CSV file name and row count
- Mapping used (from upload response)
- rows_inserted / rows_rejected
- analytics/summary before and after upload
- Any errors from backend logs

End of simple checklist


