# NEXUS Portfolio Overhaul — Action Items for Suyash

Congratulations! The automated portfolio overhaul for **NEXUS** is complete on the `polish/portfolio-overhaul` branch.

All code has been hardened, security boundaries implemented, evaluation suites measured from real algorithms with zero placeholders, and CI/CD pipelines created.

The following items require your personal credentials, external accounts, or physical recording:

---

## 1. Demo Video & Screen Recording GIF
- [ ] **Record 3-Minute Walkthrough Video**:
  - Open [`docs/DEMO_SCRIPT.md`](file:///d:/supex1/docs/DEMO_SCRIPT.md) for the exact script, timestamps, and click cues.
  - Start local backend (`cd backend && python -m uvicorn app.main:app --port 8000`) and frontend (`cd frontend && npm run dev`).
  - Upload [`data/sample/sample_supply_chain_synthetic.csv`](file:///d:/supex1/data/sample/sample_supply_chain_synthetic.csv) and walk through the 6 scenes.
  - Upload to YouTube (Unlisted or Public).
  - Update line 11 in [`README.md`](file:///d:/supex1/README.md) with your YouTube link:
    ```markdown
    [Watch the demo](https://youtu.be/YOUR_VIDEO_ID) · 3-minute walkthrough: upload, graph, risk scores, explainability, agent approval.
    ```
- [ ] **Capture Demo GIF**:
  - Record a 10–15s clip of the interactive graph cascade simulation or mitigation approval in action.
  - Save as `docs/assets/demo.gif`.

---

## 2. GitHub Repository Topics & Description

Run the following command using the GitHub CLI (`gh`) to update your repository metadata:

```bash
gh repo edit suyash655/Nexus-supplychain \
  --description "Supply chain risk analytics: anomaly detection, forecast-based risk scoring, graph cascade simulation and a human-in-the-loop LangGraph mitigation agent." \
  --add-topic supply-chain \
  --add-topic anomaly-detection \
  --add-topic langgraph \
  --add-topic fastapi \
  --add-topic nextjs \
  --add-topic networkx \
  --add-topic rag \
  --add-topic ml-evaluation
```

---

## 3. Deployment & Live Demo Link (Optional)

- [ ] If deploying live, follow the steps in [`docs/DEPLOY.md`](file:///d:/supex1/docs/DEPLOY.md).
- [ ] Once deployed, update line 13 in [`README.md`](file:///d:/supex1/README.md):
  ```markdown
  Live demo: https://nexus.yourdomain.com (or run locally with one command, see Quick start).
  ```

---

## 4. Live LLM & Langfuse Tracing (Optional)

- [ ] **Live LLM Keys**:
  - Add `GROQ_API_KEY=gsk_...` to `backend/.env` to enable live Groq Llama-3.3-70B inference instead of deterministic fallback.
- [ ] **Langfuse Observability**:
  - Add `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` to `backend/.env`.
  - Capture a screenshot of the trace waterfall and add to `docs/assets/langfuse_trace.png`.

---

## 5. License Decision

- [ ] The current repository contains a proprietary `LICENSE` titled **"Research & Evaluation License"**.
- [ ] If you want this repository to be open source for maximum recruiter accessibility, replace `LICENSE` with the standard MIT or Apache 2.0 license and update the license badge in `README.md`.

---

## 6. Optional Datasets
- [ ] **Kaggle DataCo Public Dataset**:
  - To run benchmarks on Kaggle's public 180k-row DataCo Smart Supply Chain dataset, download `DataCoSupplyChainDataset.csv` from Kaggle into `data/sample/` and run the data conversion pipeline.

---

## 7. Review, Push & Merge

Once you are ready to land these changes:

```bash
# 1. Review status and history
git status
git log --oneline -15

# 2. Push branch to GitHub
git push -u origin polish/portfolio-overhaul

# 3. Create Pull Request into master
gh pr create --base master --head polish/portfolio-overhaul \
  --title "feat: portfolio overhaul — agent reliability, security, evaluation suite, CI/CD" \
  --body "Full portfolio overhaul implementing Phase 0 through Phase 5."

# 4. Merge PR and tag v0.1.0 release
git checkout master
git merge polish/portfolio-overhaul
git tag -a v0.1.0 -m "Release v0.1.0: Supply chain risk intelligence with LangGraph agent"
git push origin master --tags
```
