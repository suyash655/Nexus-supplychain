# Audit and Architectural Decisions Log

This document records conservative engineering decisions taken during the portfolio overhaul to resolve ambiguities without making ungrounded claims.

---

## Decision 1: Accurate Framing of LangGraph Agent Structure
- **Decision:** Document the agent as a **5-node StateGraph with an approval-gated execution node** rather than an unqualified "6-node LangGraph agent".
- **Alternatives considered:**
  1. Claim "6-node LangGraph agent" because `node_execute_action` is a step in the overall mitigation process.
  2. Refactor the graph to force `execute_action` into the compiled `StateGraph` with a pause/interrupt checkpoint.
- **Reason:** The code in `backend/agent/mitigation_graph.py:548-560` literally builds a 5-node graph (`get_backup_suppliers`, `simulate_reroute_cost`, `retrieve_context`, `draft_action`, `write_pending_action`) terminating at `END`. `node_execute_action` is called from the API endpoint when human approval is given. Stating the exact architecture builds trust with hiring managers.

---

## Decision 2: Feature Importance and XAI Methodology
- **Decision:** Disclose the feature importance engine as **Random Forest Permutation Importance** and remove all claims of using `SHAP`.
- **Alternatives considered:**
  1. Add `shap` to `requirements.txt` and wrap `XAIEngine` with a SHAP TreeExplainer.
  2. Leave the claim in README as "SHAP" because both are interpretability methods.
- **Reason:** The codebase has clean, working scikit-learn `permutation_importance` code. Rewriting runtime dependencies risks breaking existing functionality and violates Rule 7 (no scope creep). Hiring managers appreciate accurate attribution over buzzwords.

---

## Decision 3: Naming and Description of TGNNEngine and CausalGenomeEngine
- **Decision:** Retain existing class names (`TGNNEngine`, `CausalGenomeEngine`) to preserve API compatibility, while documenting clearly in the README, `docs/ML_AI_HONESTY.md`, and docstrings that they implement **temporal trend analysis** and **structural risk propagation** respectively.
- **Alternatives considered:**
  1. Rename the classes across the entire backend and frontend.
  2. Keep calling them "Graph Neural Network" and "Causal Inference".
- **Reason:** Renaming classes across 30+ endpoints risks subtle runtime regressions across frontend and backend. Clarifying the reality in documentation and comments demonstrates deep technical maturity and intellectual honesty.

---

## Decision 4: License Documentation
- **Decision:** Document the license honestly as `Research & Evaluation License` in all documentation and badges, matching `LICENSE`, and list the option to adopt MIT/Apache-2.0 in `HUMAN_TODO.md`.
- **Alternatives considered:**
  1. Change `LICENSE` to MIT.
  2. Put an MIT badge while `LICENSE` says "Research & Evaluation License".
- **Reason:** Rule 6 explicitly forbids changing `LICENSE`. Mismatches between badges and the actual license file look sloppy to reviewers.

---

## Decision 5: DBSCAN Clustering Claim
- **Decision:** Remove DBSCAN from all claims in `README.md` and `ARCHITECTURE.md`.
- **Alternatives considered:**
  1. Implement DBSCAN in `analyzer.py`.
  2. Ignore the discrepancy.
- **Reason:** Isolation Forest and Z-score/IQR handle anomaly detection well. Adding unused clustering code creates untested clutter.
